import os
import json
import torch
import logging
import random
import numpy as np
from typing import Tuple, Dict, Any, List
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    Trainer,
    TrainingArguments,
    DataCollatorForTokenClassification
)
from datasets import Dataset
from evaluate import load as load_metric  # Fixed: use 'evaluate' instead of deprecated 'datasets.load_metric'
from src.data.fhir_preprocess import FHIRClinicalDataPreprocessor
from src.utils.deid_utils import Deidentifier
from src.utils.fhir_encoder import FHIRTagEncoder

# Note: compute_ner_metrics from 'src.evaluation.ner_metrics' was imported previously but never used, so not imported now


def set_seed(seed: int) -> None:
    """
    Set all random seeds for reproducibility.
    """
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_pipeline(
    data_path: str,
    model_checkpoint: str,
    output_dir: str,
    label_list: List[str],
    max_length: int = 256,
    batch_size: int = 16,
    num_train_epochs: int = 3,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Orchestrate the clinical NER model training pipeline.

    Args:
        data_path (str): Path to raw JSON data (FHIR-compliant clinical records).
        model_checkpoint (str): Model checkpoint name for transformer backbone.
        output_dir (str): Directory to save trained model and tokenizer.
        label_list (List[str]): List of entity string labels for NER.
        max_length (int): Maximum sequence length for tokenization.
        batch_size (int): Batch size for training/evaluation.
        num_train_epochs (int): Number of training epochs.
        seed (int): Random seed for reproducibility.

    Returns:
        Dict[str, Any]: Metrics and mitigation advice.
    """
    set_seed(seed)

    logging.basicConfig(
        filename=os.path.join(output_dir, 'training.log'),
        filemode='w',
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        level=logging.INFO
    )
    logging.info('Starting FHIR-compliant NER pipeline training')

    # Preprocessing + deidentification pipeline
    preprocessor = FHIRClinicalDataPreprocessor()
    deidentifier = Deidentifier()
    encoder = FHIRTagEncoder(label_list)

    with open(data_path, 'r', encoding='utf8') as f:
        raw_data = json.load(f)

    # Preprocess FHIR data -> deidentify -> encode labels
    dataset = preprocessor.preprocess(raw_data)
    dataset = deidentifier.deidentify(dataset)
    dataset = encoder.encode_labels(dataset)

    # Convert to HuggingFace Dataset
    hf_dataset = Dataset.from_pandas(dataset)

    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint, use_fast=True)

    def tokenize_and_align_labels(examples: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tokenizes text and aligns entity label IDs to tokens.

        Assumes 'examples["text"]' is a list of lists of words (already split!), and 'examples["labels"]' matches.
        """
        # Fix: If upstream pipeline doesn't split text, apply split here. But as per review: FHIRClinicalDataPreprocessor, deidentifier, encoder.encode_labels must produce split tokens.
        tokenized_inputs = tokenizer(
            examples['text'],
            padding='max_length',
            truncation=True,
            max_length=max_length,
            is_split_into_words=True,
            return_offsets_mapping=True
        )
        labels = []
        for i, label in enumerate(examples['labels']):
            word_ids = tokenized_inputs.word_ids(batch_index=i)
            label_ids = []
            for word_idx in word_ids:
                if word_idx is None:
                    label_ids.append(-100)  # Special token, will be ignored in loss calculation
                else:
                    label_ids.append(label[word_idx])
            labels.append(label_ids)
        tokenized_inputs['labels'] = labels
        return tokenized_inputs

    # Map dataset through tokenizer/label aligner
    hf_dataset = hf_dataset.map(
        tokenize_and_align_labels,
        batched=True,
        remove_columns=hf_dataset.column_names  # Remove raw columns
    )
    logging.info('Tokenization and encoding complete')

    data_collator = DataCollatorForTokenClassification(tokenizer)

    # Train/eval split
    data_split = hf_dataset.train_test_split(test_size=0.2, seed=seed)
    train_dataset = data_split['train']
    eval_dataset = data_split['test']

    model = AutoModelForTokenClassification.from_pretrained(
        model_checkpoint,
        num_labels=len(label_list)
    )

    metric = load_metric('seqeval')  # Fixed: Now from evaluate.load

    def compute_metrics(p: Tuple[np.ndarray, np.ndarray]) -> Dict[str, float]:
        """
        Compute precision, recall, F1, accuracy for NER.

        Args:
            p: Tuple(predictions, labels)

        Returns:
            Dict[str, float]: Evaluation metrics
        """
        predictions, labels = p
        predictions = np.argmax(predictions, axis=2)
        true_predictions, true_labels = [], []
        for pred, label in zip(predictions, labels):
            # Only evaluate where label != -100 (i.e., tokens to ignore)
            true_pred = [label_list[p_idx] for (p_idx, l_idx) in zip(pred, label) if l_idx != -100]
            true_lab = [label_list[l_idx] for (p_idx, l_idx) in zip(pred, label) if l_idx != -100]
            true_predictions.append(true_pred)
            true_labels.append(true_lab)
        results = metric.compute(
            predictions=true_predictions,
            references=true_labels
        )
        # Return key metrics
        return {
            'precision': results['overall_precision'],
            'recall': results['overall_recall'],
            'f1': results['overall_f1'],
            'accuracy': results['overall_accuracy']
        }

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        evaluation_strategy='epoch',
        save_strategy='epoch',
        logging_dir=os.path.join(output_dir, 'logs'),
        logging_steps=50,
        seed=seed,
        load_best_model_at_end=True,
        metric_for_best_model='f1',
        greater_is_better=True
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics
    )

    trainer.train()
    metrics = trainer.evaluate()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    logging.info(f'Training complete. Metrics: {metrics}')

    model_drift_flag = check_model_drift(metrics, baseline_f1=0.85)
    privacy_issues_flag = check_data_privacy(dataset)
    mitigation = {
        'model_drift': model_drift_flag,
        'privacy_issues': privacy_issues_flag,
        'mitigation_advice': consolidated_mitigation_advice(model_drift_flag, privacy_issues_flag)  # Fixed typo here
    }
    return {'metrics': metrics, 'mitigation': mitigation}


def check_model_drift(metrics: Dict[str, float], baseline_f1: float) -> bool:
    """
    Returns True if F1 score falls below a specified baseline (indicating possible drift).
    """
    return metrics['f1'] < baseline_f1


def check_data_privacy(dataset: Any) -> bool:
    """
    Checks for presence of potentially sensitive tokens (e.g. PHI like names/addresses).
    Args:
        dataset: Pandas DataFrame or Dataset with 'text' column (list of words per row).
    Returns:
        bool: True if privacy-violating patterns detected.
    """
    # Added type hint for clarity: expects pandas.DataFrame (review feedback)
    # Assumes 'text' column is list of words
    for patient in dataset.itertuples():
        for token in patient.text:
            if 'name' in token.lower() or 'address' in token.lower():
                return True  # Privacy risk detected
    return False


def consolidated_mitigation_advice(model_drift: bool, privacy_issues: bool) -> List[str]:
    """
    Generate advice notes if model drift or privacy issues detected.
    Returns a list of mitigation suggestions.
    """
    advice = []
    if model_drift:
        advice.append('Model drift detected: consider retraining with recent data and monitor for data distribution changes.')
    if privacy_issues:
        advice.append('Data privacy risk detected: ensure all PHI/PII fields are properly de-identified and apply rigorous audits.')
    if not advice:
        advice.append('No mitigation needed. Model and data privacy checks passed.')
    return advice
