import os
import sys
import json
import tempfile
import shutil
import pytest
from unittest import mock
import numpy as np
import pandas as pd
from src.model_serving.package_model_mlflow import ModelPackager

# We use pytest and unittest.mock to test ModelPackager.
# Fixtures are used to create temp dirs and mock objects.
# Paths and model IO are isolated to avoid side effects.
def fake_model_predict(X):
    # Simulate output for model.predict, assuming binary output.
    return np.zeros(len(X), dtype=np.float32)

class FakeMv:
    def __init__(self, run_id='123', description='model description'):
        self.run_id = run_id
        self.description = description
        self.version = '1'

class FakeRun:
    info = type('info', (), {'run_id': '123'})
    data = type('data', (), {'tags': {}})

def mock_get_latest_versions(name, stages):
    return [FakeMv()]

def mock_get_model_version(model_name, version):
    return FakeMv()

def mock_get_run(run_id):
    return FakeRun()

def mock_load_model(model_uri):
    class FakeModel:
        def predict(self, X):
            return fake_model_predict(X)
    return FakeModel()

def mock_download_artifacts(artifact_uri, dst_path=None):
    # Simulate run artifact download: create expected files
    if 'test_arrays.npz' in artifact_uri:
        # Called for test array; create a npz file with X_test, y_test
        os.makedirs(dst_path, exist_ok=True)
        arrf = os.path.join(dst_path, 'test_arrays.npz')
        np.savez(arrf, X_test=np.random.rand(5, 3), y_test=np.array([0, 1, 1, 0, 1]))
        return dst_path
    elif '/model' in artifact_uri:
        os.makedirs(dst_path, exist_ok=True)
        # Simulate model directory with requirements.txt, conda.yaml
        req = os.path.join(dst_path, 'requirements.txt')
        conda = os.path.join(dst_path, 'conda.yaml')
        with open(req, 'w') as f:
            f.write('mlflow\nnumpy')
        with open(conda, 'w') as f:
            f.write('dependencies:\n  - python=3.8')
        return dst_path
    else:
        os.makedirs(dst_path, exist_ok=True)
        return dst_path

def create_fake_healthcare_csv(path):
    df = pd.DataFrame({
        'feat1': [0, 1, 2, 3, 4],
        'feat2': [0.1, 0.2, 0.3, 0.4, 0.5],
        'feat3': [9, 8, 7, 6, 5],
        'target': [0, 1, 1, 0, 1]
    })
    df.to_csv(path, index=False)

@pytest.fixture
def temp_export_dir(tmp_path):
    dir_ = tmp_path / "packaged_model_export"
    dir_.mkdir()
    return str(dir_)

@pytest.fixture(autouse=True)
def patch_mlflow(monkeypatch, tmp_path):
    monkeypatch.setattr('mlflow.artifacts.download_artifacts', mock_download_artifacts)
    monkeypatch.setattr('mlflow.sklearn.load_model', mock_load_model)
    fake_client = mock.Mock()
    fake_client.get_latest_versions.side_effect = mock_get_latest_versions
    fake_client.get_model_version.side_effect = mock_get_model_version
    fake_client.get_run.side_effect = mock_get_run
    # Patch out MLflowClient to always use fake client
    monkeypatch.setattr('mlflow.tracking.MlflowClient', lambda: fake_client)
    return fake_client

@pytest.fixture(autouse=True)
def fake_schema_csv(monkeypatch, tmp_path):
    # Create fake healthcare_patients.csv to allow pandas usage
    csv_path = tmp_path / 'healthcare_patients.csv'
    create_fake_healthcare_csv(csv_path)
    # Patch __file__ to resolve relative path inside module
    monkeypatch.setattr('src.model_serving.package_model_mlflow.__file__', str(tmp_path / 'dummy.py'))
    # Monkeypatch pd.read_csv to only accept known path (simulate schema lookup)
    orig = pd.read_csv
    def fake_read_csv(path, *a, **k):
        if 'healthcare_patients.csv' in path:
            return orig(csv_path)
        return orig(path, *a, **k)
    monkeypatch.setattr('pandas.read_csv', fake_read_csv)

# -- UNIT TESTS --
def test_get_latest_model_version_success(temp_export_dir):
    packager = ModelPackager(model_name='fake_model', stage='Production', export_dir=temp_export_dir)
    version = packager.get_latest_model_version()
    assert version == '1', "Should retrieve version '1' from mock"

def test_get_latest_model_version_no_model(monkeypatch, temp_export_dir):
    # Simulate no model in stage: should raise RuntimeError
    packager = ModelPackager(model_name='no_model', stage='Production', export_dir=temp_export_dir)
    def none_versions(name, stages):
        return []
    packager.client.get_latest_versions = none_versions
    with pytest.raises(RuntimeError) as excinfo:
        packager.get_latest_model_version()
    assert "No model version in stage" in str(excinfo.value)

# -- INTEGRATION-LIKE TESTS --
def test_package_full_flow(temp_export_dir):
    packager = ModelPackager(model_name='HealthcareRiskPredictor', stage='Production', export_dir=temp_export_dir)
    zip_path = packager.package()
    assert os.path.exists(zip_path), "Packaged ZIP should be created"
    # Check for expected metadata inside the zip (extract and check file names)
    extract_dir = tempfile.mkdtemp()
    shutil.unpack_archive(zip_path, extract_dir)
    files = os.listdir(extract_dir)
    assert "model_metadata.json" in files, "Packaged content should have model_metadata.json"
    assert "requirements.txt" in files, "requirements.txt should be present if exists in model dir"
    assert "conda.yaml" in files, "conda.yaml should be present if exists in model dir"
    assert "input_output_schema.json" in files, "input_output_schema.json should be present"
    shutil.rmtree(extract_dir)

# -- ERROR HANDLING --
def test_infer_and_save_schema_npz_not_found(monkeypatch, temp_export_dir):
    # Remove npz path to simulate error
    packager = ModelPackager(model_name='HealthcareRiskPredictor', stage='Production', export_dir=temp_export_dir)
    # Use normal dependencies but patch os.path.exists to always False for test_arrays.npz
    model, model_uri = mock_load_model('fakeuri'), "runs:/123/model"
    def always_false(path):
        if 'test_arrays.npz' in path:
            return False
        return os.path.exists(path)
    monkeypatch.setattr(os.path, 'exists', always_false)
    with pytest.raises(RuntimeError) as exc:
        packager.infer_and_save_schema(model, '1', model_uri, temp_export_dir)
    assert "Test arrays not found for schema inference." in str(exc.value)

# -- EDGE AND PARAMETERIZED TESTS --
@pytest.mark.parametrize("version", ['1', '2', 'latest'])
def test_export_model_artifact_various_versions(temp_export_dir, version):
    packager = ModelPackager(model_name='HealthcareRiskPredictor', stage='Production', export_dir=temp_export_dir)
    # Patch client to return version as needed
    fake_mv = FakeMv(run_id='321', description=f"desc_{version}")
    fake_mv.version = version
    packager.client.get_model_version = lambda n, v: fake_mv
    packager.client.get_latest_versions = lambda name, stages: [fake_mv]
    res_dir = packager.export_model_artifact(version)
    # Should create dir for the exported version
    assert os.path.exists(res_dir), f"Export dir {res_dir} must be created"
    assert os.path.isdir(res_dir)
    with open(os.path.join(res_dir, "model_metadata.json")) as f:
        meta = json.load(f)
    assert meta['version'] == version
    assert meta['model_name'] == 'HealthcareRiskPredictor'