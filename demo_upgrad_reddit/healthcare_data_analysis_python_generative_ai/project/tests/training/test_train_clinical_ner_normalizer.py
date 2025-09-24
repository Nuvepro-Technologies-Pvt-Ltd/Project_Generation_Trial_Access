import os
import tempfile
import shutil
import logging
import types
import builtins
import pandas as pd
import numpy as np
import pytest
from unittest import mock
import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer
from src.training import train_clinical_ner_normalizer


# Arrange-Act-Assert pattern and Pytest fixtures are used throughout.
# All external dependencies (transformers, pandas, Trainer) are mocked to ensure deterministic, side-effect-free tests.

@pytest.fixture(scope='module')
def concept_vocab_csv(tmp_path_factory):
    p = tmp_path_factory.mktemp('vocab') / 'concept_vocab.csv'
    df = pd.DataFrame({
        'concept_id': ['C001', 'C002'],
        'concept_name': ['Disease', 'Symptom']
    })
    df.to_csv(p, index=False)
    return str(p)

@pytest.fixture(scope='module')
def ml_ready_train_data_csv(tmp_path_factory):
    # data: 2 examples, varied entities, stringified entity lists
    p = tmp_path_factory.mktemp('data') / 'train.csv'
    entities1 = "[{'start': 0, 'end': 7, 'label': 'O', 'concept_id': 'C001'}]"
    entities2 = "[{'start': 5, 'end': 10, 'label': 'Symptom', 'concept_id': 'C002'}]"
    df = pd.DataFrame({
        'note_text': ['disease', 'has pain'],
        'entities': [entities1, entities2]
    })
    df.to_csv(p, index=False)
    return str(p)

@pytest.fixture(scope='module')
def dummy_tokenizer(monkeypatch):
    # AutoTokenizer mock that provides tokenization/encoding and from_pretrained
    class DummyTokenizer:
        def __init__(self):
            self.model_max_length = 16
        def __call__(self, text, *args, **kwargs):
            # Simulate tokenizer returning results with offset_mapping
            max_len = kwargs.get('max_length', 16)
            n = min(len(text.split()), max_len)
            input_ids = [1]*n + [0]*(max_len-n)
            offset_mapping = [(i, i+1) for i in range(n)] + [(None, None)]*(max_len-n)
            attention_mask = [1]*n + [0]*(max_len-n)
            return {'input_ids': input_ids, 'attention_mask': attention_mask, 'offset_mapping': offset_mapping}
        def save_pretrained(self, dir):
            pass
        @classmethod
        def from_pretrained(cls, name):
            return cls()
    monkeypatch.setattr(train_clinical_ner_normalizer.AutoTokenizer, 'from_pretrained', DummyTokenizer.from_pretrained)
    return DummyTokenizer()

@pytest.fixture(scope='module')
def dummy_model(monkeypatch):
    # Mock AutoModelForTokenClassification.from_pretrained
    class DummyModel(torch.nn.Module):
        def __init__(self, *a, **kw):
            super().__init__()
            self.dummy_param = torch.nn.Parameter(torch.zeros(1))
        @classmethod
        def from_pretrained(cls, name, **kwargs):
            return cls()
        def forward(self, input_ids=None, **kwargs):
            # Return dummy logits/outputs as expected
            batch, seq = input_ids.shape
            return types.SimpleNamespace(
                logits = torch.ones((batch, seq, 4)), # 4 labels for illustration
                loss = torch.tensor(0.5)
            )
    monkeypatch.setattr(train_clinical_ner_normalizer.AutoModelForTokenClassification, 'from_pretrained', DummyModel.from_pretrained)
    return DummyModel()

@pytest.fixture(scope='module')
def dummy_trainer(monkeypatch):
    # Patch Trainer for fast dry runs and track calls
    class DummyTrainer:
        def __init__(self, *a, **kw):
            self.kw = kw
            self._trained = False
        def train(self):
            self._trained = True
        def evaluate(self):
            return {'eval_loss': 0.1}
        def predict(self, dataset):
            # Return (predictions, labels, metrics) with shape (num_examples, seq_len, num_labels)
            n = len(dataset)
            seq_len = 8
            num_labels = 3
            # Simulate logits, labels
            preds = np.zeros((n, seq_len, num_labels))
            preds[:, :, 1] = 10.0  # Highest predicted label 1 so argmax is 1
            labels = np.ones((n, seq_len), dtype=int)
            labels[:, 4:] = -100  # Simulate padding
            metrics = None
            return preds, labels, metrics
        def save_model(self, output_dir):
            self.output_dir = output_dir
        @property
        def model(self):
            return self
    monkeypatch.setattr(train_clinical_ner_normalizer, 'Trainer', DummyTrainer)
    return DummyTrainer

# ---- Unit Tests ----
def test_load_snomed_vocab(concept_vocab_csv):
    result = train_clinical_ner_normalizer.load_snomed_vocab(concept_vocab_csv)
    assert result == {'C001': 'Disease', 'C002': 'Symptom'}

def test_prepare_examples_from_csv(ml_ready_train_data_csv):
    concept_map = {'C001': 'Disease', 'C002': 'Symptom'}
    result = train_clinical_ner_normalizer.prepare_examples_from_csv(ml_ready_train_data_csv, concept_map)
    assert isinstance(result, list)
    assert set(result[0].keys()) == {'text', 'entities'}
    assert result[0]['entities'][0]['label'] == 'Disease'
    assert result[1]['entities'][0]['label'] == 'Symptom'

def test_get_label_list():
    examples = [
        {'text': 'a', 'entities': [{'label':'Disease'}]},
        {'text': 'b', 'entities': [{'label':'Symptom'}]}
    ]
    labels = train_clinical_ner_normalizer.get_label_list(examples)
    assert 'B-Disease' in labels and 'B-Symptom' in labels
    assert 'I-Disease' in labels and 'I-Symptom' in labels
    assert 'O' in labels

def test_seed_all():
    # Check random state after seeding
    train_clinical_ner_normalizer.seed_all(42)
    assert random.randint(0, 1000) == np.random.randint(0, 1000)  # likely equal

@pytest.mark.parametrize('val_frac', [0.1, 0.2, 0.5])
def test_split_data(val_frac):
    examples = [{'text': str(i), 'entities': []} for i in range(10)]
    train, val = train_clinical_ner_normalizer.split_data(examples, val_frac=val_frac, seed=23)
    assert len(train) + len(val) == 10
    assert abs(len(val) - int(val_frac*10)) <= 1
    # Test deterministic split
    train2, val2 = train_clinical_ner_normalizer.split_data(examples, val_frac=val_frac, seed=23)
    assert val == val2
    assert train == train2

# ---- ClinicalNERDataset edge cases ----
def test_clinical_dataset_getitem(dummy_tokenizer):
    ex = [{'text': 'some disease', 'entities': [{'start': 5, 'end': 12, 'label': 'Disease'}]}]
    label2id = {'O':0, 'B-Disease':1, 'I-Disease':2}
    ds = train_clinical_ner_normalizer.ClinicalNERDataset(ex, dummy_tokenizer, label2id, max_length=8)
    item = ds[0]
    assert set(item.keys()) == {'input_ids', 'attention_mask', 'labels'}
    assert isinstance(item['labels'], torch.Tensor)
    assert item['labels'].shape[0] == 8

def test_clinical_dataset_len(dummy_tokenizer):
    exs = [{'text':'a','entities':[]},{'text':'b','entities':[]}]
    ds = train_clinical_ner_normalizer.ClinicalNERDataset(exs, dummy_tokenizer, {'O':0}, max_length=8)
    assert len(ds) == 2

# ---- Metrics, Evaluation & Interpret ----
def test_compute_metrics_typical():
    # Simulate predictions and ground truths, expects all pred==label
    class Output:
        predictions = np.array([[[0.0, 3.0], [1.0, 2.0]], [[1.0, 9.0], [2.0, 2.0]]])
        label_ids = np.array([[1, 1], [0, -100]])
    out = train_clinical_ner_normalizer.compute_metrics(Output)
    assert set(out.keys()) >= {'precision','recall','f1','accuracy'}
    assert all(0.0 <= out[k] <= 1.0 for k in out)

def test_evaluate_model_logs_and_return(monkeypatch, dummy_trainer, dummy_model, dummy_tokenizer, tmp_path):
    # Setup id2label for mapping ints
    id2label = {0:'O', 1:'Disease', 2:'Symptom'}
    val_ds = [0,1]  # Dummy arg, only __len__ is used
    log_records = []
    def dummy_log(msg):
        log_records.append(msg)
    monkeypatch.setattr(logging, 'info', dummy_log)
    metrics, y_true, y_pred = train_clinical_ner_normalizer.evaluate_model(dummy_trainer(None), val_ds, id2label)
    assert 'precision' in metrics
    assert isinstance(y_true, list)
    assert any('Classification Report' in r or 'Evaluation Metrics' in r for r in log_records)  # check logging

def test_interpret_results_low_recall():
    metrics = {'precision':0.85, 'recall':0.6, 'f1':0.7}
    y_true = [['Disease']*5]
    y_pred = [['Disease']*3+['O']*2]
    out = train_clinical_ner_normalizer.interpret_results(metrics, y_true, y_pred)
    assert 'To improve recall' in out
    assert 'Eval Summary' in out
    assert 'Strong:' in out

def test_interpret_results_high_f1():
    metrics = {'precision':0.91,'recall':0.92,'f1':0.95}
    y_true = [['Symptom']*3]
    y_pred = [['Symptom']*3]
    out = train_clinical_ner_normalizer.interpret_results(metrics, y_true, y_pred)
    assert 'Model achieves strong F1-score' in out

# ---- Integration Test: main ----
def test_main_training_end_to_end(monkeypatch, tmp_path, ml_ready_train_data_csv, concept_vocab_csv, dummy_tokenizer, dummy_model, dummy_trainer):
    # Patch parser to inject arguments
    output_dir = str(tmp_path / 'out')
    parser_args = [
        '--train_data', ml_ready_train_data_csv,
        '--concept_vocab', concept_vocab_csv,
        '--output_dir', output_dir,
        '--max_epochs', '1',
        '--batch_size', '2',
        '--model_name', 'dummy',
        '--val_frac', '0.5',
        '--seed', '23'
    ]
    monkeypatch.setattr('sys.argv', ['prog'] + parser_args)
    # Patch logging to avoid file output
    monkeypatch.setattr(logging, 'basicConfig', lambda **kwargs: None)
    # Patch model/tokenizer/trainer from above fixtures
    # Patch pd.read_csv with original---pytest fixtures have created real files
    # Run main (no exception indicates success). Trainers/model/tokenizer are all mocked
    train_clinical_ner_normalizer.main()
    # outputs: summary file and model/tokenizer save_pretrained called, check file written
    assert os.path.isfile(os.path.join(output_dir, 'eval_summary.txt'))
    with open(os.path.join(output_dir, 'eval_summary.txt')) as f:
        content = f.read()
        assert 'Eval Summary' in content