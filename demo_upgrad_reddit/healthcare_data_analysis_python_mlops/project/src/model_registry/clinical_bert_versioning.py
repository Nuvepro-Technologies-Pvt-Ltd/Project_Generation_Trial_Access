import os
import mlflow
import mlflow.pyfunc
import logging
import torch
import pandas as pd
from typing import Dict, Any
from transformers import AutoTokenizer, AutoModelForTokenClassification, Trainer, TrainingArguments
from sklearn.metrics import f1_score
import ast  # Used to safely parse string representations of lists
import json  # For saving/loading label artifacts

logger = logging.getLogger("model_registry")
logger.setLevel(logging.INFO)

class ClinicalBERTNERPipeline(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        from transformers import AutoTokenizer, AutoModelForTokenClassification
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(context.artifacts["tokenizer_path"])
        # Load model
        self.model = AutoModelForTokenClassification.from_pretrained(context.artifacts["model_path"])
        # Load label list, label2id, and id2label from artifacts
        # The context.artifacts-values are file paths to JSON files
        with open(context.artifacts["label_list"], "r") as f:
            self.label_list = json.load(f)
        with open(context.artifacts["label2id"], "r") as f:
            self.label2id = json.load(f)
        with open(context.artifacts["id2label"], "r") as f:
            self.id2label = {int(k): v for k, v in json.load(f).items()}

    def predict(self, context, model_input):
        # Tokenize the input texts
        tokens = self.tokenizer(model_input["text"].tolist(), truncation=True, padding=True, return_tensors="pt")
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(**tokens)
            probs = torch.nn.functional.softmax(outputs.logits, dim=2)
            pred_labels = torch.argmax(probs, dim=2).cpu().numpy()
        results = []
        texts = model_input["text"].tolist()
        for idx, prediction in enumerate(pred_labels):
            original_length = len(texts[idx].split())
            label_indices = prediction[:original_length]
            # Map token indices to labels using id2label loaded from artifact
            results.append([self.id2label[str(i)] if str(i) in self.id2label else "O" for i in label_indices])
        return results

# ====================== Data Loading ======================
def load_dataset(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        return df
    except FileNotFoundError:
        logger.error(f"Data file not found: {path}")
        raise
    except Exception as e:
        logger.error(f"Error loading data from {path}: {e}")
        raise

# =========== Safe F1 Computation For NER =============
def compute_ner_f1(y_true, y_pred) -> float:
    # Simple macro F1 for NER token labels
    flat_true = [item for sublist in y_true for item in sublist]
    flat_pred = [item for sublist in y_pred for item in sublist]
    return f1_score(flat_true, flat_pred, average="macro")

# ============= NER Fine Tune Pipeline =======================
def fine_tune_ner_pipeline(
    base_model: str,
    train_data: pd.DataFrame,
    eval_data: pd.DataFrame,
    label_col: str = "tags",
    text_col: str = "text",
    output_dir: str = "outputs/clinicalbert_v2"
) -> Dict[str, Any]:
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    # Securely parse the label lists using ast.literal_eval
    label_set = sorted(list(set(label for labels in train_data[label_col] for label in ast.literal_eval(labels))))
    label2id = {l: i for i, l in enumerate(label_set)}
    id2label = {i: l for l, i in label2id.items()}

    class NERDataset(torch.utils.data.Dataset):
        def __init__(self, data, tokenizer, label2id):
            self.data = data
            self.tokenizer = tokenizer
            self.label2id = label2id
        def __len__(self):
            return len(self.data)
        def __getitem__(self, idx):
            text = self.data.iloc[idx][text_col]
            # Safely parse labels with ast.literal_eval instead of eval
            labels = ast.literal_eval(self.data.iloc[idx][label_col])
            encoding = self.tokenizer(text, truncation=True, padding="max_length", max_length=128, return_tensors="pt")
            label_ids = [self.label2id.get(l, 0) for l in labels]
            label_ids += [0] * (128 - len(label_ids))
            label_ids = label_ids[:128]
            return {
                'input_ids': encoding['input_ids'].squeeze(),
                'attention_mask': encoding['attention_mask'].squeeze(),
                'labels': torch.tensor(label_ids)
            }
    train_dataset = NERDataset(train_data, tokenizer, label2id)
    eval_dataset = NERDataset(eval_data, tokenizer, label2id)

    model = AutoModelForTokenClassification.from_pretrained(base_model, num_labels=len(label2id), label2id=label2id, id2label=id2label)
    args = TrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=2,
        logging_steps=10,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True
    )
    def compute_metrics(p):
        preds = p.predictions.argmax(-1)
        labels = p.label_ids
        real_pred = []
        real_labels = []
        for pred_row, label_row in zip(preds, labels):
            actual_len = sum(label_row != 0)
            l = [id2label[id] for id in label_row[:actual_len]]
            p = [id2label[id] for id in pred_row[:actual_len]]
            real_pred.append(p)
            real_labels.append(l)
        return {"f1": compute_ner_f1(real_labels, real_pred)}
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        compute_metrics=compute_metrics
    )
    trainer.train()
    os.makedirs(output_dir, exist_ok=True)
    # Save model and tokenizer
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    # ==== Save label_list, label2id, and id2label as explicit artifacts ====
    with open(os.path.join(output_dir, "label_list.json"), "w") as f:
        json.dump(label_set, f)
    with open(os.path.join(output_dir, "label2id.json"), "w") as f:
        json.dump(label2id, f)
    with open(os.path.join(output_dir, "id2label.json"), "w") as f:
        json.dump({str(k): v for k, v in id2label.items()}, f)
    # Compute eval metrics
    y_true = [ast.literal_eval(tags) for tags in eval_data[label_col]]
    texts = eval_data[text_col].tolist()
    eval_rows = [{"text": t} for t in texts]
    pred_labels = []
    model.eval()
    for ix, sample in enumerate(eval_rows):
        toks = tokenizer(sample["text"], return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            logits = model(**toks).logits
        preds = torch.argmax(logits, dim=2)[0][:len(sample["text"].split())].tolist()
        pred_labels.append([id2label.get(i, "O") for i in preds])
    f1 = compute_ner_f1(y_true, pred_labels)
    return {
        "model_path": output_dir,
        "tokenizer_path": output_dir,
        "label_list": os.path.join(output_dir, "label_list.json"),  # Now a file path
        "label2id": os.path.join(output_dir, "label2id.json"),
        "id2label": os.path.join(output_dir, "id2label.json"),
        "f1": f1
    }

# =========== Model Version Registration ===============
def register_new_model_version(
        run_name: str,
        fine_tune_result: Dict[str, Any],
        base_version: str,
        description: str,
        production_criteria: float,
        registry_model_name: str
    ) -> str:
    mlflow.set_experiment("ClinicalNLP_ClinicalBERT_Finetune")
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_param("base_version", base_version)
        mlflow.log_metric("NER_F1", fine_tune_result["f1"])
        mlflow.log_param("description", description)
        # Log model with all needed artifacts as file paths
        mlflow.pyfunc.log_model(
            artifact_path="clinical_bert_model",
            python_model=ClinicalBERTNERPipeline(),
            artifacts={
                "model_path": fine_tune_result["model_path"],
                "tokenizer_path": fine_tune_result["tokenizer_path"],
                "label_list": fine_tune_result["label_list"],
                "label2id": fine_tune_result["label2id"],
                "id2label": fine_tune_result["id2label"]
            },
            code_path=[]
        )
        model_uri = f"runs:/{run.info.run_id}/clinical_bert_model"
        mv = mlflow.register_model(
            model_uri=model_uri,
            name=registry_model_name
        )
        mlflow.set_tag("NER_F1", fine_tune_result["f1"])
        mlflow.set_tag("base_version", base_version)
        mlflow.set_tag("description", description)
        # Move to Staging or Production if criteria met
        client = mlflow.tracking.MlflowClient()
        if fine_tune_result["f1"] >= production_criteria:
            client.transition_model_version_stage(
                name=registry_model_name,
                version=mv.version,
                stage="Production",
                archive_existing_versions=True
            )
            logger.info(f"Model version {mv.version} promoted to Production.")
        else:
            client.transition_model_version_stage(
                name=registry_model_name,
                version=mv.version,
                stage="Staging",
                archive_existing_versions=False
            )
            logger.info(f"Model version {mv.version} placed in Staging.")
        logger.info(f"Registered ClinicalBERT model as version {mv.version} with F1={fine_tune_result['f1']}")
        return mv.version

# ========== Registry Model Version Comparison ===========
def compare_registry_versions(registry_model_name: str) -> None:
    client = mlflow.tracking.MlflowClient()
    try:
        versions = client.get_latest_versions(registry_model_name, stages=["None", "Production", "Staging"])
    except Exception as e:
        logger.error(f"Error fetching model versions for {registry_model_name}: {e}")
        return
    version_info = {}
    for v in versions:
        metrics = client.get_run(v.run_id).data.metrics
        params = client.get_run(v.run_id).data.params
        tags = client.get_run(v.run_id).data.tags
        version_info[v.version] = {
            "stage": v.current_stage,
            "f1": metrics.get("NER_F1", None),
            "base_version": params.get("base_version", None),
            "description": tags.get("description", "")
        }
    for ver, vals in version_info.items():
        logger.info(f"Model v{ver}: F1={vals['f1']} | Stage={vals['stage']} | Base={vals['base_version']} | Desc={vals['description']}")

# ====== Main process orchestrating ==================
def main():
    os.makedirs("outputs", exist_ok=True)
    train_path = "data/clinical_ner_train.csv"
    eval_path = "data/clinical_ner_eval.csv"
    base_model = "emilyalsentzer/Bio_ClinicalBERT"
    base_version = "v1"
    # Load data with error handling
    try:
        train_df = load_dataset(train_path)
        eval_df = load_dataset(eval_path)
    except Exception as e:
        logger.error(f"Cannot load train/eval datasets: {e}")
        return
    # Fine-tune model with new configs (simulate change)
    fine_tune_result = fine_tune_ner_pipeline(
        base_model=base_model,
        train_data=train_df,
        eval_data=eval_df,
        output_dir="outputs/clinicalbert_v2"
    )
    registry_model_name = "ClinicalBERT_NER"
    try:
        version = register_new_model_version(
            run_name="ClinicalBERT_NER_v2_Finetune",
            fine_tune_result=fine_tune_result,
            base_version=base_version,
            description="Fine-tuned on more annotated NER data. New configs: epochs=2, batch_size=8, improved preprocessing.",
            production_criteria=0.9,
            registry_model_name=registry_model_name
        )
    except Exception as e:
        logger.error(f"Model registration failed: {e}")
        return
    compare_registry_versions(registry_model_name=registry_model_name)
    logger.info(f"Registry review complete. Production version flagged.")

if __name__ == "__main__":
    main()
