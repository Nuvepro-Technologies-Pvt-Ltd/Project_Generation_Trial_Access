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
        # Initialize the experiment tracker.
        # 1. Store the experiment_name parameter as an instance variable.
        # 2. Set the MLflow experiment using mlflow.set_experiment with the experiment name.
        # 3. Set up logging configuration with level INFO and a standard format.
        self.experiment_name = experiment_name
        # IMPLEMENT ABOVE INSTRUCTIONS

    def load_healthcare_data(self, file_path: str) -> pd.DataFrame:
        """Loads healthcare dataset from the provided path."""
        # INSTRUCTIONS:
        # 1. Check if the file_path exists using os.path.exists.
        #    - If it does not exist, raise a FileNotFoundError with a descriptive message.
        # 2. Load the data from the specified file_path into a pandas DataFrame using pd.read_csv.
        # 3. Return the loaded DataFrame.
        # IMPLEMENT ABOVE INSTRUCTIONS
        pass

    def preprocess(self, data: pd.DataFrame) -> tuple:
        """Preprocesses input data for ML training."""
        # INSTRUCTIONS:
        # 1. Check and ensure that the 'target' column exists in data.columns, otherwise raise ValueError.
        # 2. Separate X (the features) by dropping 'target', and y (the target) as data['target'].
        # 3. Create an instance of SimpleImputer with strategy 'mean'.
        # 4. Fit and transform X with the imputer to create X_imputed.
        # 5. Return (X_imputed, y) as a tuple.
        # Variables provided:
        #   data : the input dataframe
        # IMPLEMENT ABOVE INSTRUCTIONS
        pass

    def run_training_experiment(self, data_path: str, n_estimators: int, max_depth: int, random_state: int) -> str:
        """
        Executes a single experiment run, logs to MLflow.
        Returns the run_id of the experiment.
        """
        # INSTRUCTIONS:
        # 1. Load data by calling self.load_healthcare_data(data_path).
        # 2. Preprocess the data by calling self.preprocess(data) to get X and y.
        # 3. Split the data using train_test_split, with test_size=0.2, stratify=y, random_state=random_state.
        # 4. Create RandomForestClassifier with n_estimators, max_depth, random_state.
        # 5. Start an MLflow run context (with mlflow.start_run() as run):
        #    a. Log an info message containing training parameters.
        #    b. Fit the model using model.fit() with X_train and y_train.
        #    c. Predict on X_test to get y_pred.
        #    d. Score accuracy, AUC, and F1 using sklearn metrics on y_test/y_pred.
        #    e. Log each hyperparameter (mlflow.log_param) and each metric (mlflow.log_metric).
        #    f. Log the model with mlflow.sklearn.log_model.
        #    g. Create directory for artifacts for this run.
        #    h. Save X_test and y_test as a compressed npz file in the artifact directory.
        #    i. Log the test arrays file as an MLflow artifact.
        #    j. Log an info message with run_id and metric summaries.
        #    k. Return the MLflow run id (run.info.run_id).
        # Variables provided:
        #   data_path, n_estimators, max_depth, random_state
        # IMPLEMENT ABOVE INSTRUCTIONS
        pass

    def get_best_run(self, metric_name: str = 'roc_auc', maximize: bool = True) -> dict:
        """
        Retrieves the best MLflow run details based on metric_name.
        """
        # INSTRUCTIONS:
        # 1. Create MlflowClient instance.
        # 2. Get the experiment object by name using client.get_experiment_by_name(self.experiment_name).
        #    - If experiment does not exist, raise ValueError.
        # 3. Search all runs for that experiment using client.search_runs ordered by metric_name DESC if maximize else ASC.
        #    - If no runs are found, raise RuntimeError.
        # 4. Take the first run as the best_run.
        # 5. Prepare run_details as a dict with keys:
        #    - 'run_id': best_run.info.run_id
        #    - 'metrics': best_run.data.metrics
        #    - 'params': best_run.data.params
        # 6. Log the best run info.
        # 7. Return run_details.
        # Variables provided:
        #   metric_name, maximize
        # IMPLEMENT ABOVE INSTRUCTIONS
        pass

if __name__ == "__main__":
    # INSTRUCTIONS:
    # 1. Create an instance of HealthcareMLflowExperimentTracker, passing "HealthcareRiskPrediction" as experiment name.
    # 2. Construct the absolute healthcare_data_path using os.path and __file__, pointing to '../../data/healthcare_patients.csv'.
    # 3. Run two training experiments with different hyperparameters using run_training_experiment method; store results in run_id_1 and run_id_2.
    # 4. Call get_best_run with metric_name 'roc_auc' and maximize=True; store result in best_details.
    # 5. Print the best run details.
    # IMPLEMENT ABOVE INSTRUCTIONS
    pass
