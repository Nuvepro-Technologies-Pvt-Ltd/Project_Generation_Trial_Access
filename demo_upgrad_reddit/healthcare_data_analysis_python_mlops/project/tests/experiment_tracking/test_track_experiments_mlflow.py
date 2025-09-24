import os
import shutil
import tempfile
import pytest
import pandas as pd
import numpy as np
from unittest import mock
from experiment_tracking.track_experiments_mlflow import HealthcareMLflowExperimentTracker

##############################
# Test Suite for HealthcareMLflowExperimentTracker
#
# Coverage:
# - Unit tests for data loading, preprocessing, experiment running, and best run retrieval
# - Edge cases: missing files, missing/invalid columns, empty dataframe
# - Error scenarios: MLflow errors, no runs exist
# - Integration: run_training_experiment end-to-end (mocking MLflow interactions)
##############################

@pytest.fixture(scope="function")
def sample_healthcare_data_csv():
    df = pd.DataFrame({
        'age': [29, 48, 56],
        'bmi': [22.3, 28.4, np.nan],
        'bp': [80, 92, 110],
        'chol': [169, 210, 275],
        'target': [0, 1, 0]
    })
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "sample.csv")
    df.to_csv(file_path, index=False)
    yield file_path
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")
def tracker():
    # Use a unique experiment per test run
    auto_expt_name = f"TestExperiment_{np.random.randint(0, 1e8)}"
    return HealthcareMLflowExperimentTracker(experiment_name=auto_expt_name)

################ UNIT TESTS ################

def test_load_healthcare_data_valid_file(sample_healthcare_data_csv, tracker):
    # Arrange
    file_path = sample_healthcare_data_csv
    # Act
    df = tracker.load_healthcare_data(file_path)
    # Assert
    assert not df.empty, "Loaded dataframe should not be empty."
    assert all(col in df.columns for col in ['age', 'bmi', 'bp', 'chol', 'target']), "All expected columns should be present."

def test_load_healthcare_data_file_not_found(tracker):
    # Arrange
    bad_path = "/tmp/does_not_exist.csv"
    # Act & Assert
    with pytest.raises(FileNotFoundError) as exc:
        tracker.load_healthcare_data(bad_path)
    assert str(exc.value).startswith("Data file not found"), "Should raise FileNotFoundError if file missing."

def test_preprocess_success(tracker):
    # Arrange
    df = pd.DataFrame({
        'feature_1': [1, 2, 3],
        'feature_2': [4, np.nan, 6],
        'target': [0, 1, 0]
    })
    # Act
    X_out, y_out = tracker.preprocess(df)
    # Assert
    assert X_out.shape[1] == 2, "Should return all feature columns."
    assert np.isnan(X_out).sum() == 0, "There should be no NaNs after imputation."
    assert y_out.tolist() == [0, 1, 0], "Target column values must match."

def test_preprocess_missing_target_column(tracker):
    # Arrange
    df = pd.DataFrame({
        'a': [1, 2, 3],
        'b': [2, 3, 4]
    })
    # Act & Assert
    with pytest.raises(ValueError) as exc:
        tracker.preprocess(df)
    assert "Missing target column" in str(exc.value), "Should raise ValueError if 'target' column is missing."

def test_preprocess_empty_dataframe(tracker):
    # Arrange
    df = pd.DataFrame(columns=['target'])
    # Act
    X_out, y_out = tracker.preprocess(df)
    # Assert
    assert X_out.shape[0] == 0, "No samples for empty dataframe."
    assert len(y_out) == 0, "No targets for empty dataframe."

############### run_training_experiment ###############

def test_run_training_experiment_happy_path(monkeypatch, sample_healthcare_data_csv, tracker):
    # Arrange: Mock all MLflow methods to avoid side effects
    dummy_run_id = "123456"
    class DummyRun:
        class info:
            run_id = dummy_run_id
        @property
        def __enter__(self):
            return self
        def __exit__(self, *a):
            pass
    monkeypatch.setattr("mlflow.start_run", lambda *a, **k: DummyRun())
    monkeypatch.setattr("mlflow.log_param", lambda *a, **k: None)
    monkeypatch.setattr("mlflow.log_metric", lambda *a, **k: None)
    monkeypatch.setattr("mlflow.sklearn.log_model", lambda *a, **k: None)
    monkeypatch.setattr("mlflow.log_artifact", lambda *a, **k: None)
    # Act
    run_id = tracker.run_training_experiment(
        data_path=sample_healthcare_data_csv,
        n_estimators=5, max_depth=2, random_state=123)
    # Assert
    assert run_id == dummy_run_id, "Returned run_id should match the expected dummy id."

def test_run_training_experiment_bad_data_path(tracker):
    # Act & Assert
    with pytest.raises(FileNotFoundError):
        tracker.run_training_experiment(
            data_path="/tmp/not_existing.csv",
            n_estimators=5, max_depth=2, random_state=123)

############### get_best_run ###############

def test_get_best_run_success(monkeypatch, tracker):
    # Arrange: Patch MLflowClient to simulate experiment & run results
    class DummyRunData:
        def __init__(self):
            self.metrics = {"roc_auc": 0.95, "accuracy": 0.92}
            self.params = {"n_estimators": "10"}
    class DummyRunInfo:
        run_id = "bestid123"
    class DummyRun:
        info = DummyRunInfo()
        data = DummyRunData()
    class DummyExperiment:
        experiment_id = "exp1"
    class DummyClient:
        def get_experiment_by_name(self, name): return DummyExperiment()
        def search_runs(self, experiment_ids, order_by=None): return [DummyRun()]
    monkeypatch.setattr("mlflow.tracking.MlflowClient", lambda: DummyClient())
    # Act
    result = tracker.get_best_run(metric_name="roc_auc", maximize=True)
    # Assert
    assert result["run_id"] == "bestid123"
    assert result["metrics"]["roc_auc"] == 0.95
    assert result["params"]["n_estimators"] == "10"

def test_get_best_run_experiment_not_found(monkeypatch, tracker):
    class DummyClient:
        def get_experiment_by_name(self, name): return None
    monkeypatch.setattr("mlflow.tracking.MlflowClient", lambda: DummyClient())
    with pytest.raises(ValueError) as exc:
        tracker.get_best_run()
    assert "does not exist" in str(exc.value)

def test_get_best_run_no_runs(monkeypatch, tracker):
    class DummyExperiment:
        experiment_id = "exp1"
    class DummyClient:
        def get_experiment_by_name(self, name): return DummyExperiment()
        def search_runs(self, experiment_ids, order_by=None): return []
    monkeypatch.setattr("mlflow.tracking.MlflowClient", lambda: DummyClient())
    with pytest.raises(RuntimeError) as exc:
        tracker.get_best_run()
    assert "No runs found" in str(exc.value)

############### Edge/Corner Cases ###############

def test_run_training_experiment_empty_dataframe(monkeypatch, tracker):
    # Arrange
    temp_dir = tempfile.mkdtemp()
    empty_csv = os.path.join(temp_dir, "empty.csv")
    # Create CSV with header only (target column present)
    pd.DataFrame(columns=["age", "bmi", "bp", "chol", "target"]).to_csv(empty_csv, index=False)
    monkeypatch.setattr("mlflow.start_run", lambda *a, **k: mock.DEFAULT)
    monkeypatch.setattr("mlflow.log_param", lambda *a, **k: None)
    monkeypatch.setattr("mlflow.log_metric", lambda *a, **k: None)
    monkeypatch.setattr("mlflow.sklearn.log_model", lambda *a, **k: None)
    monkeypatch.setattr("mlflow.log_artifact", lambda *a, **k: None)
    try:
        with pytest.raises(ValueError):
            tracker.run_training_experiment(
                data_path=empty_csv, n_estimators=10, max_depth=3, random_state=0)
    finally:
        shutil.rmtree(temp_dir)