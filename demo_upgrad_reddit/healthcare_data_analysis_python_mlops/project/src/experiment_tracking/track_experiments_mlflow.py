import os
import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
from sklearn.impute import SimpleImputer
import logging

class HealthcareMLflowExperimentTracker:
    """
    Tracks ML experiments using MLflow for Healthcare AI pipelines.
    Captures parameters, metrics, and artifacts for each run.
    """
    def __init__(self, experiment_name: str = "HealthcareRiskPrediction"):
        self.experiment_name = experiment_name
        mlflow.set_experiment(self.experiment_name)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    def load_healthcare_data(self, file_path: str) -> pd.DataFrame:
        """Loads healthcare dataset from the provided path."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found at {file_path}")
        data = pd.read_csv(file_path)
        return data

    def preprocess(self, data: pd.DataFrame) -> tuple:
        """Preprocesses input data for ML training."""
        if 'target' not in data.columns:
            raise ValueError('Missing target column in data.')
        X = data.drop('target', axis=1)
        y = data['target']
        imputer = SimpleImputer(strategy='mean')
        X_imputed = imputer.fit_transform(X)
        return X_imputed, y

    def run_training_experiment(self, data_path: str, n_estimators: int, max_depth: int, random_state: int) -> str:
        """
        Executes a single experiment run, logs to MLflow.
        Returns the run_id of the experiment.
        """
        data = self.load_healthcare_data(data_path)
        X, y = self.preprocess(data)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=random_state
        )
        model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=random_state)
        with mlflow.start_run() as run:
            logging.info(f"Training RandomForest (n_estimators={n_estimators}, max_depth={max_depth}, random_state={random_state})")
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            auc = roc_auc_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            mlflow.log_param('n_estimators', n_estimators)
            mlflow.log_param('max_depth', max_depth)
            mlflow.log_param('random_state', random_state)
            mlflow.log_metric('accuracy', accuracy)
            mlflow.log_metric('roc_auc', auc)
            mlflow.log_metric('f1_score', f1)
            mlflow.sklearn.log_model(model, artifact_path="model")
            # Ensure artifact directory exists before saving arrays (fixes previous issue)
            artifact_path = f"artifacts_run_{run.info.run_id}"
            os.makedirs(artifact_path, exist_ok=True)  # Create directory if it doesn't exist
            np.savez_compressed(os.path.join(artifact_path, 'test_arrays.npz'), X_test=X_test, y_test=y_test)
            mlflow.log_artifact(os.path.join(artifact_path, 'test_arrays.npz'))
            logging.info(f"Run {run.info.run_id} logged to MLflow. Metrics: accuracy={accuracy}, AUC={auc}, f1={f1}")
            return run.info.run_id

    def get_best_run(self, metric_name: str = 'roc_auc', maximize: bool = True) -> dict:
        """
        Retrieves the best MLflow run details based on metric_name.
        """
        client = mlflow.tracking.MlflowClient()
        experiment = client.get_experiment_by_name(self.experiment_name)
        if experiment is None:
            raise ValueError(f"Experiment {self.experiment_name} does not exist.")
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=[f"metrics.{metric_name} DESC" if maximize else f"metrics.{metric_name} ASC"]
        )
        if not runs:
            raise RuntimeError("No runs found.")
        best_run = runs[0]
        run_details = {
            'run_id': best_run.info.run_id,
            'metrics': best_run.data.metrics,
            'params': best_run.data.params
        }
        logging.info(f"Best run: {best_run.info.run_id} | Metrics: {best_run.data.metrics} | Params: {best_run.data.params}")
        return run_details

if __name__ == "__main__":
    tracker = HealthcareMLflowExperimentTracker("HealthcareRiskPrediction")
    # Use __file__ and os.path operations for robust data file location
    healthcare_data_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../data/healthcare_patients.csv')
    )
    run_id_1 = tracker.run_training_experiment(
        data_path=healthcare_data_path, n_estimators=100, max_depth=5, random_state=42
    )
    run_id_2 = tracker.run_training_experiment(
        data_path=healthcare_data_path, n_estimators=150, max_depth=7, random_state=7
    )
    best_details = tracker.get_best_run(metric_name='roc_auc', maximize=True)
    print(f"Best Run Details: {best_details}")
