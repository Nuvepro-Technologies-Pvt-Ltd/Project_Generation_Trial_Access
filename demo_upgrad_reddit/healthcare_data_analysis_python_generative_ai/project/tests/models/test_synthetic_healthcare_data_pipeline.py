import os
import io
import json
import tempfile
import shutil
import pytest
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from unittest import mock
from models.synthetic_healthcare_data_pipeline import (
    TabularHealthcareDataset,
    TabularVAE,
    vae_loss,
    validate_config,
    train_vae_with_privacy,
    sample_synthetic_data,
    PrivacyUtilityValidator,
    minimum_viable_quality_checks,
    design_pipeline_documentation
)


# Arrange-Act-Assert style tests for synthetic healthcare data pipeline
# These are designed for pytest and can be run as-is

# --------------------
# Fixtures & Test Constants
# --------------------

@pytest.fixture(scope='module')
def small_dataframe():
    # Simulate tabular EHR data
    np.random.seed(123)
    df = pd.DataFrame({
        'age': np.random.randint(20, 60, 32),
        'bp': np.random.normal(120, 10, 32),
        'med': np.random.randint(0, 2, 32),
        'outcome': np.random.randint(0, 3, 32),
    })
    return df

@pytest.fixture(scope='function')
def temp_datafile(small_dataframe):
    # Create a temp CSV file
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.csv') as f:
        small_dataframe.to_csv(f.name, index=False)
        yield f.name
    os.remove(f.name)

@pytest.fixture(scope='function')
def temp_configfile():
    config = {
        'seed': 42,
        'batch_size': 4,
        'latent_dim': 4,
        'lr': 1e-3,
        'epochs': 2,   # keep low for fast tests
        'noise_multiplier': 1.1
    }
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as f:
        json.dump(config, f)
        yield f.name
    os.remove(f.name)

@pytest.fixture(scope='function')
def temp_model_file():
    path = tempfile.mktemp(suffix='.pt')
    yield path
    if os.path.exists(path):
        os.remove(path)

@pytest.fixture(scope='function')
def temp_output_csv():
    fn = tempfile.mktemp(suffix='.csv')
    yield fn
    if os.path.exists(fn):
        os.remove(fn)

# ---------------------------
# Unit tests
# ---------------------------

def test_TabularHealthcareDataset_basic_len_get(small_dataframe):
    dataset = TabularHealthcareDataset(small_dataframe)
    assert len(dataset) == small_dataframe.shape[0], 'Dataset length should match number of rows.'
    t = dataset[0]
    assert isinstance(t, torch.Tensor), 'Item from dataset should be a torch Tensor.'
    assert t.shape[0] == small_dataframe.shape[1]

def test_TabularVAE_shapes_and_forward(small_dataframe):
    input_dim = small_dataframe.shape[1]
    vae = TabularVAE(input_dim=input_dim, latent_dim=2)
    batch = torch.from_numpy(small_dataframe.iloc[:3].to_numpy(dtype=np.float32))
    recon, mu, logvar = vae(batch)
    assert recon.shape == batch.shape
    assert mu.shape == (3, 2)
    assert logvar.shape == (3, 2)

def test_validate_config_defaults_and_missing():
    cfg = {'seed': 7}
    required = {'seed': 1, 'extra': 2}
    result = validate_config(cfg, required)
    assert result['seed'] == 7
    assert result['extra'] == 2, 'Should fill in missing default.'
    with pytest.raises(ValueError):
        validate_config({}, {'a': None})

def test_vae_loss_behavior():
    recon = torch.tensor([[1.0,2.0]], requires_grad=True)
    x = torch.tensor([[1.0,1.1]], requires_grad=True)
    mu = torch.tensor([[0.0,0.0]], requires_grad=True)
    logvar = torch.tensor([[0.0,0.0]], requires_grad=True)
    l = vae_loss(recon, x, mu, logvar)
    assert l.item() > 0
    l.backward()

# ---------------------------
# Integration tests: training & sampling
# ---------------------------

def test_train_vae_with_privacy_and_sampling(temp_datafile, temp_configfile, temp_model_file):
    # Train with privacy enabled
    result = train_vae_with_privacy(
        data_path=temp_datafile,
        config_path=temp_configfile,
        model_save_path=temp_model_file,
        privacy=True,
        epsilon=2.0,
        delta=1e-5,
        max_grad_norm=1.2,
        device='cpu'
    )
    assert os.path.exists(temp_model_file), 'Model file should be created.'
    assert 'final_loss' in result and result['final_loss'] > 0
    assert isinstance(result['privacy_report'], dict)
    # Try loading the model and sampling synthetic data
    output_csv = tempfile.mktemp(suffix='.csv')
    try:
        sample_synthetic_data(
            model_path=temp_model_file,
            config_path=temp_configfile,
            num_samples=5,
            output_path=output_csv,
            device='cpu'
        )
        assert os.path.exists(output_csv), 'Synthetic data CSV should be created.'
        df = pd.read_csv(output_csv)
        assert df.shape[0] == 5
    finally:
        if os.path.exists(output_csv):
            os.remove(output_csv)

# ---------------------------
# PrivacyUtilityValidator and metric checks
# ---------------------------

def test_PrivacyUtilityValidator_stat_and_metrics(small_dataframe, temp_output_csv):
    # Generate synthetic data similar to the real
    synth = small_dataframe.copy()
    synth.loc[:, :] += np.random.normal(0, 0.5, synth.shape)
    synth.to_csv(temp_output_csv, index=False)
    small_dataframe.to_csv('real_test.csv', index=False)
    try:
        v = PrivacyUtilityValidator('real_test.csv', temp_output_csv)
        stats = v.stat_metrics()
        mi = v.mutual_information()
        sil = v.silhouette()
        mirisk = v.membership_inference_risk(n_probe=5)
        assert 'feature_mse' in stats
        assert 'mutual_info' in mi
        assert isinstance(sil, float)
        assert 0.0 <= mirisk <= 1.0
        allchk = v.all_checks()
        assert 'stat_metrics' in allchk and 'silhouette_score' in allchk
    finally:
        os.remove('real_test.csv')

# --------- minimum_viable_quality_checks

def test_minimum_viable_quality_checks(small_dataframe, temp_output_csv):
    synth = small_dataframe.copy()
    synth.loc[:, :] += np.random.normal(0, 0.2, synth.shape)
    synth.to_csv(temp_output_csv, index=False)
    real_csv = tempfile.mktemp(suffix='.csv')
    try:
        small_dataframe.to_csv(real_csv, index=False)
        thresholds = { 'feature_mse': 3.0, 'silhouette': 0.05, 'mirisk': 0.8 }
        result = minimum_viable_quality_checks(real_csv, temp_output_csv, thresholds)
        assert 'feature_mse' in result and 'passed' in result
        assert result['passed'] is True or result['passed'] is False
        assert 'details' in result
    finally:
        if os.path.exists(real_csv): os.remove(real_csv)

# --------- Pipeline documentation

def test_design_pipeline_documentation(tmp_path):
    # Arrange
    pipeline_dir = tmp_path
    data_path = str(tmp_path / 'input.csv')
    synth_path = str(tmp_path / 'syn_out.csv')
    real_config = {'lr': 1e-3}
    privacy_cfg = {'noise_multiplier': 1.5}
    # Act
    design_pipeline_documentation(pipeline_dir, data_path, synth_path, real_config, privacy_cfg)
    # Assert
    doc_path = os.path.join(pipeline_dir, 'healthcare_data_gen_pipeline_doc.json')
    assert os.path.exists(doc_path)
    with open(doc_path, 'r') as f:
        data = json.load(f)
    assert 'data_ingestion' in data and 'output' in data

# --------------
# Error Handling & Edge Cases
# --------------

def test_validate_config_raises_on_missing_required():
    with pytest.raises(ValueError):
        validate_config({}, {'must': None})

def test_train_vae_with_privacy_raises_on_missing_noise(temp_datafile, temp_configfile, temp_model_file):
    # Remove noise_multiplier from config
    with open(temp_configfile, 'r') as f:
        cfg = json.load(f)
    cfg.pop('noise_multiplier', None)
    cfg_file2 = tempfile.mktemp(suffix='.json')
    with open(cfg_file2, 'w') as f:
        json.dump(cfg, f)
    with pytest.raises(ValueError):
        train_vae_with_privacy(
            data_path=temp_datafile,
            config_path=cfg_file2,
            model_save_path=temp_model_file,
            privacy=True,
            epsilon=1.0,
            delta=1e-5,
            max_grad_norm=1.0,
            device='cpu'
        )
    if os.path.exists(cfg_file2):
        os.remove(cfg_file2)

def test_sample_synthetic_data_raises_on_missing_data_path(temp_model_file, temp_configfile):
    # Remove data_path from config
    with open(temp_configfile, 'r') as f:
        cfg = json.load(f)
    if 'data_path' in cfg: cfg.pop('data_path')
    bad_cfg_path = tempfile.mktemp(suffix='.json')
    with open(bad_cfg_path, 'w') as f:
        json.dump(cfg, f)
    with pytest.raises(ValueError):
        sample_synthetic_data(
            model_path=temp_model_file,
            config_path=bad_cfg_path,
            num_samples=3,
            output_path='junk.csv',
            device='cpu'
        )
    os.remove(bad_cfg_path)