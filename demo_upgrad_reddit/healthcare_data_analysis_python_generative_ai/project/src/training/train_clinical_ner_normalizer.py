import os
import logging
import random
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Any
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer
from transformers import DataCollatorForTokenClassification
from seqeval.metrics import classification_report, precision_score, recall_score, f1_score
from sklearn.metrics import accuracy_score

class ClinicalNERDataset(Dataset):
    """
    Torch Dataset class for token classification (NER) and concept normalization.
    """
    def __init__(self, examples: List[Dict[str, Any]], tokenizer, label2id: Dict[str, int], max_length: int = 256):
        self.examples = examples
        self.tokenizer = tokenizer
        self.label2id = label2id
        self.max_length = max_length
    def __len__(self) -> int:
        return len(self.examples)
    def _tokenize_and_align_labels(self, text: str, entities: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[int]]:
        encoding = self.tokenizer(text, truncation=True, max_length=self.max_length, is_split_into_words=False, return_offsets_mapping=True, padding='max_length')
        labels = [self.label2id['O']] * len(encoding['input_ids'])
        offset_mapping = encoding['offset_mapping']
        for entity in entities:
            ent_label = entity['label']
            ent_start = entity['start']
            ent_end = entity['end']
            for idx, (start, end) in enumerate(offset_mapping):
                if start is None or end is None:
                    continue
                if start >= ent_start and end <= ent_end:
                    if start == ent_start:
                        labels[idx] = self.label2id['B-' + ent_label]
                    else:
                        labels[idx] = self.label2id['I-' + ent_label]
        encoding.pop('offset_mapping')
        return encoding, labels
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        item = self.examples[idx]
        encoding, labels = self._tokenize_and_align_labels(item['text'], item['entities'])
        encoding['labels'] = labels
        return {k: torch.tensor(v) for k, v in encoding.items()}

def load_snomed_vocab(vocab_file: str) -> Dict[str, str]:
    vocab = {}
    df = pd.read_csv(vocab_file)
    for _, r in df.iterrows():
        vocab[r['concept_id']] = r['concept_name']
    return vocab

def prepare_examples_from_csv(csv_path: str, concept_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
    data = pd.read_csv(csv_path)
    examples = []
    for _, row in data.iterrows():
        text = str(row['note_text'])
        entities = []
        if isinstance(row.get('entities'), str):
            import ast
            entities = ast.literal_eval(row['entities'])
        mapped_ents = []
        for ent in entities:
            mapped_ent = ent.copy()
            mapped_ent['label'] = concept_mapping.get(ent.get('concept_id', ''), ent.get('label', 'O'))
            mapped_ents.append(mapped_ent)
        examples.append({'text': text, 'entities': mapped_ents})
    return examples

def get_label_list(examples: List[Dict[str, Any]]) -> List[str]:
    labels = set(['O'])
    for ex in examples:
        for ent in ex['entities']:
            labels.add('B-' + ent['label'])
            labels.add('I-' + ent['label'])
    return sorted(list(labels))

def seed_all(seed: int = 23):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def compute_metrics(p):
    preds = np.argmax(p.predictions, axis=2)
    labels = p.label_ids
    true_labels = [
        [l for (l, label_id) in zip(label_row, label_row) if l != -100]
        for label_row in labels
    ]
    true_preds = [
        [l for (l, label_id) in zip(pred_row, label_row) if label_id != -100]
        for pred_row, label_row in zip(preds, labels)
    ]
    return {
        'precision': precision_score(true_labels, true_preds),
        'recall': recall_score(true_labels, true_preds),
        'f1': f1_score(true_labels, true_preds),
        'accuracy': accuracy_score(np.array(true_labels).flatten(), np.array(true_preds).flatten())
    }

def split_data(examples: List[Dict[str, Any]], val_frac: float = 0.1, seed: int = 23) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    rng = np.random.RandomState(seed)
    perm = rng.permutation(len(examples))
    n_val = int(val_frac * len(examples))
    val_idx = perm[:n_val]
    train_idx = perm[n_val:]
    train_set = [examples[i] for i in train_idx]
    val_set = [examples[i] for i in val_idx]
    return train_set, val_set

def evaluate_model(trainer: Trainer, val_dataset: Dataset, id2label: Dict[int, str]):
    preds_out, labels, _ = trainer.predict(val_dataset)
    preds = np.argmax(preds_out, axis=2)
    y_true = []
    y_pred = []
    for i in range(labels.shape[0]):
        true_labels = [id2label[lab] for lab in labels[i] if lab != -100]
        pred_labels = [id2label[pr] for (pr, lab) in zip(preds[i], labels[i]) if lab != -100]
        y_true.append(true_labels)
        y_pred.append(pred_labels)
    logging.info('Classification Report: 
' + classification_report(y_true, y_pred))
    metrics = {
        'precision': precision_score(y_true, y_pred),
        'recall': recall_score(y_true, y_pred),
        'f1': f1_score(y_true, y_pred)
    }
    logging.info('Evaluation Metrics: {}'.format(metrics))
    return metrics, y_true, y_pred

def interpret_results(metrics: Dict[str, float], y_true, y_pred) -> str:
    strongest = ''
    weakest = ''
    if metrics['f1'] >= 0.9:
        strongest = 'Model achieves strong F1-score, indicating overall effective NER and normalization.'
    elif metrics['precision'] > metrics['recall']:
        strongest = 'High precision: most detected entities are correct.'
        weakest = 'Lower recall: misses some relevant entities.'
    else:
        strongest = 'Balanced precision and recall.'
        weakest = ''
    report = classification_report(y_true, y_pred)
    suggestions = []
    if metrics['recall'] < 0.8:
        suggestions.append('To improve recall, enrich training data with more rare entity mentions, or apply class-balancing and upsampling for underrepresented classes.')
    if metrics['precision'] < 0.8:
        suggestions.append('Improve precision by further data cleaning and adding false-positive mitigations.')
    if 'suggestions' not in locals():
        suggestions.append('Review model logs and confusion matrix.')
    out = f'Eval Summary:
{report}
Strong: {strongest}
Weak: {weakest}
Improvement: {" ".join(suggestions)}'
    return out

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Train/Evaluate Clinical NER & Concept Normalization model')
    parser.add_argument('--train_data', type=str, required=True, help='ML-ready CSV with note_text and entities')
    parser.add_argument('--concept_vocab', type=str, required=True, help='CSV with columns: concept_id,concept_name')
    parser.add_argument('--model_name', type=str, default='emilyalsentzer/Bio_ClinicalBERT')
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--max_epochs', type=int, default=5)
    parser.add_argument('--batch_size', type=int, default=8)
    parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu')
    parser.add_argument('--val_frac', type=float, default=0.1)
    parser.add_argument('--seed', type=int, default=23)
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    logging.basicConfig(filename=os.path.join(args.output_dir, 'training.log'), level=logging.INFO)
    seed_all(args.seed)
    concept_map = load_snomed_vocab(args.concept_vocab)
    examples = prepare_examples_from_csv(args.train_data, concept_map)
    train_examples, val_examples = split_data(examples, val_frac=args.val_frac, seed=args.seed)
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    label_list = get_label_list(examples)
    label2id = {l: i for i, l in enumerate(label_list)}
    id2label = {i: l for l, i in label2id.items()}
    train_dataset = ClinicalNERDataset(train_examples, tokenizer, label2id)
    val_dataset = ClinicalNERDataset(val_examples, tokenizer, label2id)
    model = AutoModelForTokenClassification.from_pretrained(
        args.model_name,
        num_labels=len(label_list),
        id2label=id2label,
        label2id=label2id
    )
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        num_train_epochs=args.max_epochs,
        evaluation_strategy='epoch',
        save_strategy='epoch',
        logging_dir=os.path.join(args.output_dir, 'logs'),
        logging_strategy='epoch',
        report_to = [],
        seed=args.seed,
        load_best_model_at_end=True,
        metric_for_best_model='f1'
    )
    data_collator = DataCollatorForTokenClassification(tokenizer, pad_to_multiple_of=8)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )
    trainer.train()
    metrics, y_true, y_pred = evaluate_model(trainer, val_dataset, id2label)
    summary = interpret_results(metrics, y_true, y_pred)
    print(summary)
    with open(os.path.join(args.output_dir, 'eval_summary.txt'), 'w') as f:
        f.write(summary)
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

if __name__ == '__main__':
    main()
