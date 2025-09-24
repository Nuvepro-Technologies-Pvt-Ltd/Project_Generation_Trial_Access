import os
import io
import json
import tempfile
import shutil
from unittest import mock
import pytest
from fastapi.testclient import TestClient
from starlette.status import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from src.api import synthetic_data_api


# --- Setup FastAPI Test Client ---
@pytest.fixture(scope='module')
def client():
    return TestClient(synthetic_data_api.app)

# --- Helper Fixtures for Mocking Dependencies & Test Data ---
@pytest.fixture
def valid_api_key(monkeypatch):
    monkeypatch.setenv('HEALTH_API_KEY', 'test_secret')
    synthetic_data_api.API_KEY = 'test_secret'
    return 'test_secret'

@pytest.fixture
def temp_files():
    temp_dir = tempfile.mkdtemp()
    config_path = os.path.join(temp_dir, 'config.json')
    weights_path = os.path.join(temp_dir, 'model.pt')
    # Write dummy config and model files
    with open(config_path, 'w') as f:
        json.dump({'data_path': 'data.csv', 'latent_dim': 10, 'batch_size': 8}, f)
    with open(weights_path, 'w') as f:
        f.write('dummy-weights')
    yield {
        'config_path': config_path,
        'weights_path': weights_path,
        'tmp_dir': temp_dir
    }
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_sample_synthetic_data():
    with mock.patch('src.models.synthetic_healthcare_data_pipeline.sample_synthetic_data') as sample_mock:
        # Simulate writing a csv file
        def writer(model_path, config_path, num_samples, output_path):
            with open(output_path, 'w') as f:
                f.write('id,col1\n1,foo\n')
        sample_mock.side_effect = writer
        yield sample_mock

@pytest.fixture
def mock_quality_checks():
    with mock.patch('src.models.synthetic_healthcare_data_pipeline.minimum_viable_quality_checks') as mock_checks:
        def check(real_file, synth_file, thresholds):
            return {'passed': True, 'feature_mse': 0.3}
        mock_checks.side_effect = check
        yield mock_checks

@pytest.fixture
def patch_logdir(tmp_path, monkeypatch):
    logdir = tmp_path / 'logs'
    logdir.mkdir()
    monkeypatch.setenv('SYNTH_API_LOGDIR', str(logdir))
    synthetic_data_api.LOGDIR = str(logdir)
    return str(logdir)

# --- Test Cases for Endpoint /api/v1/generate ---
def test_generate_synthetic_data_success(client, valid_api_key, temp_files, mock_sample_synthetic_data, mock_quality_checks, patch_logdir):
    req_data = {
        'num_records': 5,
        'model_config_path': temp_files['config_path'],
        'trained_model_path': temp_files['weights_path'],
        # Test implicit output_csv_path (should default to /tmp)
        # Provide prompt engineering fields as well
        'prompt_template': 'Patient: {name}',
        'prompt_vars': {'name': 'John Doe'}
    }
    headers = {'X-API-KEY': valid_api_key}
    response = client.post('/api/v1/generate', json=req_data, headers=headers)
    assert response.status_code == HTTP_201_CREATED, 'Expected 201 Created on successful generation.'
    resp_json = response.json()
    assert 'synthetic_data_file' in resp_json
    assert resp_json['detail'] == 'Synthetic data generated successfully.'
    assert resp_json['validation_report']['feature_mse'] == 0.3
    assert resp_json['download_url'].startswith('/api/v1/download')
    assert resp_json['generation_time_seconds'] > 0
    # Check that prompt file is created alongside output CSV
    prompt_path = resp_json['synthetic_data_file'].replace('.csv', '_prompt.json')
    assert os.path.exists(prompt_path), 'Prompt file should be created when prompt_template and prompt_vars provided.'
    # Check CSV is actually written
    assert os.path.exists(resp_json['synthetic_data_file']), 'Synthetic data file should exist.'

# --- Negative Tests: auth, validation, errors ---
def test_generate_synthetic_data_missing_api_key(client, temp_files):
    req_data = {
        'num_records': 3,
        'model_config_path': temp_files['config_path'],
        'trained_model_path': temp_files['weights_path']
    }
    response = client.post('/api/v1/generate', json=req_data)
    assert response.status_code == HTTP_401_UNAUTHORIZED

@pytest.mark.parametrize('missing_field', ['num_records', 'model_config_path', 'trained_model_path'])
def test_generate_synthetic_data_validation_error(client, valid_api_key, temp_files, missing_field):
    data = {
        'num_records': 2,
        'model_config_path': temp_files['config_path'],
        'trained_model_path': temp_files['weights_path']
    }
    data.pop(missing_field)
    headers = {'X-API-KEY': valid_api_key}
    resp = client.post('/api/v1/generate', json=data, headers=headers)
    assert resp.status_code == 422, 'Should fail if required field is missing.'

# Edge: num_records outside allowed
@pytest.mark.parametrize('bad_num', [0, 10001])
def test_num_records_bounds(client, valid_api_key, temp_files, bad_num):
    data = {
        'num_records': bad_num,
        'model_config_path': temp_files['config_path'],
        'trained_model_path': temp_files['weights_path']
    }
    headers = {'X-API-KEY': valid_api_key}
    resp = client.post('/api/v1/generate', json=data, headers=headers)
    assert resp.status_code == 422

# File missing validation
def test_generate_bad_paths(client, valid_api_key, temp_files):
    req_data = {
        'num_records': 2,
        'model_config_path': '/no/such/config.json',
        'trained_model_path': temp_files['weights_path']
    }
    headers = {'X-API-KEY': valid_api_key}
    resp = client.post('/api/v1/generate', json=req_data, headers=headers)
    assert resp.status_code == 422 or resp.status_code == 500
    req_data['model_config_path'] = temp_files['config_path']
    req_data['trained_model_path'] = '/no/such/model.pt'
    resp2 = client.post('/api/v1/generate', json=req_data, headers=headers)
    assert resp2.status_code == 422 or resp2.status_code == 500

# Step fail: privacy/utility check fails
def test_generate_utility_rejects(client, valid_api_key, temp_files, mock_sample_synthetic_data, patch_logdir):
    # Patch the quality check to return failed
    with mock.patch('src.models.synthetic_healthcare_data_pipeline.minimum_viable_quality_checks', return_value={'passed': False, 'feature_mse': 100.0}):
        req = {
            'num_records': 2,
            'model_config_path': temp_files['config_path'],
            'trained_model_path': temp_files['weights_path']
        }
        headers = {'X-API-KEY': valid_api_key}
        resp = client.post('/api/v1/generate', json=req, headers=headers)
        assert resp.status_code == HTTP_422_UNPROCESSABLE_ENTITY
        assert 'did not pass privacy' in resp.text

# Test GET /api/v1/healthz
def test_healthz(client):
    resp = client.get('/api/v1/healthz')
    assert resp.status_code == 200
    assert resp.json()['status'] == 'ready'

# --- Download endpoint tests ---
def test_download_synthetic_file_success(client, valid_api_key, temp_files, patch_logdir):
    # Place fake file in /tmp (allowed)
    file_path = os.path.join('/tmp', 'testfile.csv')
    with open(file_path, 'w') as f:
        f.write('id,col1\n1,foo\n')
    headers = {'X-API-KEY': valid_api_key}
    resp = client.get(f'/api/v1/download?file={file_path}', headers=headers)
    assert resp.status_code == 200
    assert resp.headers['content-type'] == 'text/csv'
    os.remove(file_path)

def test_download_synthetic_file_forbidden(client, valid_api_key, temp_files, patch_logdir):
    # Path outside allowed dirs
    outside_file = os.path.join(os.getcwd(), 'notallowed.csv')
    with open(outside_file, 'w') as f:
        f.write('something')
    headers = {'X-API-KEY': valid_api_key}
    resp = client.get(f'/api/v1/download?file={outside_file}', headers=headers)
    assert resp.status_code == HTTP_403_FORBIDDEN
    os.remove(outside_file)

def test_download_synthetic_file_missing(client, valid_api_key, patch_logdir):
    headers = {'X-API-KEY': valid_api_key}
    missing_path = '/tmp/doesnotexist.csv'
    resp = client.get(f'/api/v1/download?file={missing_path}', headers=headers)
    assert resp.status_code == HTTP_404_NOT_FOUND

# --- Security test: path traversal attempt
@pytest.mark.parametrize('evil_path', ['../tmp/evil.csv', '/etc/passwd', '/tmp/../etc/passwd'])
def test_download_path_traversal(client, valid_api_key, evil_path):
    headers = {'X-API-KEY': valid_api_key}
    resp = client.get(f'/api/v1/download?file={evil_path}', headers=headers)
    assert resp.status_code == HTTP_403_FORBIDDEN or resp.status_code == HTTP_404_NOT_FOUND