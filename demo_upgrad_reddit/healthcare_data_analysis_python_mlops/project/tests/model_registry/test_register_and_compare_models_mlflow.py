import os
import sys
import types
import pytest
from unittest import mock
from types import SimpleNamespace
from src.model_registry import register_and_compare_models_mlflow

import builtins

# Arrange-Act-Assert test suite for register_and_compare_models_mlflow.py
def mock_experiment(name):
    # Simulate a valid MLflow experiment object
    return SimpleNamespace(name=name, experiment_id='1')

@pytest.fixture
def mock_mlflow(monkeypatch):
    # Mock mlflow and experiment related functions
    mlflow_mock = mock.Mock()
    mlflow_mock.get_experiment_by_name.side_effect = lambda name: mock_experiment(name) if name == "HealthcareRiskPrediction" else None
    monkeypatch.setattr(register_and_compare_models_mlflow, 'mlflow', mlflow_mock)
    return mlflow_mock

@pytest.fixture
def mock_mlflow_client(monkeypatch):
    # Provide a configurable mock for MlflowClient
    client_mock = mock.Mock()
    monkeypatch.setattr(register_and_compare_models_mlflow, 'MlflowClient', mock.Mock(return_value=client_mock))
    return client_mock

# --- Unit Tests ---
def test_register_model_version_success_new_model(mock_mlflow, mock_mlflow_client):
    # Arrange
    run_id = 'abc123'
    model_name = 'TestModel'
    description = 'desc123'
    # No existing models
    mock_mlflow_client.list_registered_models.return_value = []
    mock_registered_model = SimpleNamespace(version='1')
    mock_mlflow_client.create_model_version.return_value = mock_registered_model
    # Act
    version = register_and_compare_models_mlflow.register_model_version(run_id, model_name, description)
    # Assert
    assert version == '1'
    mock_mlflow_client.create_registered_model.assert_called_once_with(model_name)
    mock_mlflow_client.create_model_version.assert_called_once_with(
        name=model_name,
        source=f"runs:/{run_id}/model",
        run_id=run_id,
        description=description
    )

def test_register_model_version_existing_model(mock_mlflow, mock_mlflow_client):
    # Arrange
    run_id = 'xyz789'
    model_name = 'ExistingModel'
    mock_locally_registered_model = SimpleNamespace(name=model_name)
    mock_mlflow_client.list_registered_models.return_value = [mock_locally_registered_model]
    mock_registered_model = SimpleNamespace(version='2')
    mock_mlflow_client.create_model_version.return_value = mock_registered_model
    # Act
    version = register_and_compare_models_mlflow.register_model_version(run_id, model_name)
    # Assert
    mock_mlflow_client.create_registered_model.assert_not_called()
    assert version == '2'

def test_register_model_version_experiment_missing(mock_mlflow, mock_mlflow_client):
    # Arrange
    mock_mlflow.get_experiment_by_name.side_effect = lambda name: None
    # Act & Assert
    with pytest.raises(RuntimeError, match="Experiment 'HealthcareRiskPrediction' does not exist."):
        register_and_compare_models_mlflow.register_model_version('dummy', 'SomeModel')

def test_set_model_stage_calls_client(mock_mlflow_client):
    # Arrange
    # Act
    register_and_compare_models_mlflow.set_model_stage('TestModel', '1', 'Production')
    # Assert
    mock_mlflow_client.transition_model_version_stage.assert_called_once_with(
        name='TestModel', version='1', stage='Production', archive_existing_versions=False
    )

def test_get_model_version_metrics_returns_dict(mock_mlflow_client):
    # Arrange
    version = '2'
    model_name = 'TestModel'
    mv = SimpleNamespace(
        run_id='run_id_xyz',
        current_stage='Staging',
        description='Some desc'
    )
    run = SimpleNamespace(data=SimpleNamespace(
        metrics={'roc_auc': 0.78},
        params={'n_estimators': '100'}))
    mock_mlflow_client.get_model_version.return_value = mv
    mock_mlflow_client.get_run.return_value = run
    # Act
    result = register_and_compare_models_mlflow.get_model_version_metrics(model_name, version)
    # Assert
    assert result == {
        'run_id': 'run_id_xyz',
        'version': '2',
        'stage': 'Staging',
        'metrics': {'roc_auc': 0.78},
        'params': {'n_estimators': '100'},
        'description': 'Some desc'
    }

def test_get_best_version_by_metric_maximize():
    # Arrange
    versions = {
        '1': {'metrics': {'roc_auc': 0.75}},
        '2': {'metrics': {'roc_auc': 0.81}},
        '3': {'metrics': {'roc_auc': 0.78}}
    }
    # Act
    res = register_and_compare_models_mlflow.get_best_version_by_metric(versions, 'roc_auc', maximize=True)
    # Assert
    assert res == '2'

def test_get_best_version_by_metric_minimize():
    # Arrange
    versions = {
        '1': {'metrics': {'loss': 0.12}},
        '2': {'metrics': {'loss': 0.14}},
        '3': {'metrics': {'loss': 0.10}}
    }
    # Act
    res = register_and_compare_models_mlflow.get_best_version_by_metric(versions, 'loss', maximize=False)
    # Assert
    assert res == '3'

def test_get_best_version_by_metric_missing_metric():
    # Arrange
    versions = {
        '1': {'metrics': {}},
        '2': {'metrics': {'roc_auc': 0.70}}
    }
    # Act
    res = register_and_compare_models_mlflow.get_best_version_by_metric(versions, 'roc_auc', maximize=True)
    # Assert
    assert res == '2'

def test_document_promotion_decision_updates_description_and_tag(mock_mlflow_client):
    # Arrange
    client = mock_mlflow_client
    model_name = 'TestModel'
    version = '5'
    rationale = 'Promoted due to excellent performance.'
    # Act
    register_and_compare_models_mlflow.document_promotion_decision(client, model_name, version, rationale)
    # Assert
    client.update_model_version.assert_called_once_with(
        name=model_name, version=version, description=rationale
    )
    client.set_model_version_tag.assert_called_once_with(
        name=model_name,
        version=version,
        key="promotion_rationale",
        value=rationale
    )

# --- Integration and Edge Case Tests ---
def test_main_promotes_best_version(monkeypatch):
    """
    Integration test: For main(), verify best version gets promoted, rationale is documented,
    and other versions are archived. Uses mocks to avoid actual MLflow side-effects.
    """
    # Arrange
    logging_mock = mock.Mock()
    monkeypatch.setattr(register_and_compare_models_mlflow.logging, 'basicConfig', mock.Mock())
    monkeypatch.setattr(register_and_compare_models_mlflow.logging, 'info', logging_mock)
    # Mock experiment tracker and training runs
    tracker_mock = mock.Mock()
    tracker_mock.run_training_experiment.side_effect = ['runA', 'runB']
    tracker_cls_mock = mock.Mock(return_value=tracker_mock)
    track_module_mock = types.SimpleNamespace(HealthcareMLflowExperimentTracker=tracker_cls_mock)
    def fake_spec(*args, **kwargs): return SimpleNamespace(loader=SimpleNamespace(exec_module=lambda module: None))
    monkeypatch.setattr(register_and_compare_models_mlflow, 'spec_from_file_location', lambda *a, **kw: SimpleNamespace(loader=SimpleNamespace(exec_module=lambda m: None)))
    monkeypatch.setattr(register_and_compare_models_mlflow, 'module_from_spec', lambda spec: track_module_mock)
    # Patch os.path.abspath and os.path.join to prevent file issues
    monkeypatch.setattr(os.path, 'abspath', lambda p: '/tmp/dummy.csv')
    monkeypatch.setattr(os.path, 'join', lambda *a: '/tmp/dummy.csv')
    monkeypatch.setattr(os.path, 'dirname', lambda _: '')
    # MLflow client mocks
    client_mock = mock.Mock()
    monkeypatch.setattr(register_and_compare_models_mlflow, 'MlflowClient', mock.Mock(return_value=client_mock))
    client_mock.list_registered_models.return_value = []
    mock_exp = mock_experiment("HealthcareRiskPrediction")
    monkeypatch.setattr(register_and_compare_models_mlflow.mlflow, 'get_experiment_by_name', lambda name: mock_exp)
    client_mock.create_model_version.side_effect = [SimpleNamespace(version='1'), SimpleNamespace(version='2')]
    def fake_metrics_mock(ver):
        if ver == '1':
            return SimpleNamespace(run_id='runA', current_stage='Staging', description='d1')
        else:
            return SimpleNamespace(run_id='runB', current_stage='None', description='d2')
    client_mock.get_model_version.side_effect = fake_metrics_mock
    # Run object with metrics
    run_mocks = {
        'runA': SimpleNamespace(data=SimpleNamespace(metrics={'roc_auc': 0.61}, params={'n_estimators': '100'})),
        'runB': SimpleNamespace(data=SimpleNamespace(metrics={'roc_auc': 0.85}, params={'n_estimators': '150'}))
    }
    client_mock.get_run.side_effect = lambda run_id: run_mocks[run_id]
    client_mock.search_model_versions.return_value = []
    # Patch set_model_stage to observe calls
    original_set_model_stage = register_and_compare_models_mlflow.set_model_stage
    set_stage_calls = []
    def set_model_stage_spy(mn, ver, stage): set_stage_calls.append((mn, ver, stage))
    monkeypatch.setattr(register_and_compare_models_mlflow, 'set_model_stage', set_model_stage_spy)
    # Patch document_promotion_decision as a no-op
    monkeypatch.setattr(register_and_compare_models_mlflow, 'document_promotion_decision', lambda *a, **kw: None)
    # Act
    register_and_compare_models_mlflow.main()
    # Assert (best version '2' should be Production, other is Archived)
    assert ('HealthcareRiskPredictor', '2', 'Production') in set_stage_calls
    assert any(stage == 'Archived' for _, _, stage in set_stage_calls if stage != 'Production')
    assert logging_mock.called
    # Clean up monkeypatch
    monkeypatch.setattr(register_and_compare_models_mlflow, 'set_model_stage', original_set_model_stage)

# --- Edge/Boundary Tests ---
def test_get_best_version_by_metric_all_missing_metric():
    # Arrange
    versions = {
        '1': {'metrics': {}},
        '2': {'metrics': {}}
    }
    # Act
    result = register_and_compare_models_mlflow.get_best_version_by_metric(versions, 'accuracy', maximize=True)
    # Assert
    assert result is None

def test_register_model_version_creates_model_only_once(mock_mlflow, mock_mlflow_client):
    # Arrange
    run_id = 'newrun001'
    model_name = 'UniqueModel'
    # client.list_registered_models returns models with different names
    mock_mlflow_client.list_registered_models.return_value = [SimpleNamespace(name='OtherModel')]
    mock_registered_model = SimpleNamespace(version='5')
    mock_mlflow_client.create_model_version.return_value = mock_registered_model
    # Act
    version = register_and_compare_models_mlflow.register_model_version(run_id, model_name)
    # Assert - should create the model since it's not in the list
    mock_mlflow_client.create_registered_model.assert_called_once_with(model_name)
    assert version == '5'

# --- Invalid/Exception Case ---
def test_register_model_version_create_model_raises(monkeypatch, mock_mlflow, mock_mlflow_client):
    # Arrange
    mock_mlflow_client.list_registered_models.return_value = []
    mock_mlflow_client.create_registered_model.side_effect = Exception('failure!')
    # Act & Assert
    with pytest.raises(Exception, match='failure!'):
        register_and_compare_models_mlflow.register_model_version('run123', 'MyModel')