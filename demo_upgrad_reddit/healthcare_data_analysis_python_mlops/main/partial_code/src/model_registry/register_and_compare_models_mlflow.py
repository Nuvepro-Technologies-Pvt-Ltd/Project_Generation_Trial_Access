import os
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
import logging
from typing import Dict, Any
from importlib.util import spec_from_file_location, module_from_spec


def register_model_version(run_id: str, model_name: str, description: str = "") -> str:
    """
    Registers a given run's model artifact as a new version in MLflow Model Registry.
    Returns the model version string (e.g., '1', '2', ...).
    """
    client = MlflowClient()
    # INSTRUCTION: Retrieve the MLflow experiment named "HealthcareRiskPrediction" using mlflow.get_experiment_by_name().
    # If the experiment doesn't exist, raise an error.
    # Construct the model_uri from the run_id in the format "runs:/{run_id}/model".
    # Use client.list_registered_models() to check if a model with the name model_name exists, and create it if it doesn't.
    # Register a new model version using client.create_model_version with the model uri, run_id, description, and model name.
    # Return the string version of the registered model (e.g., '1', '2').


def set_model_stage(model_name: str, model_version: str, stage: str) -> None:
    """
    Transitions model version to a given stage in the MLflow registry (e.g., 'Staging', 'Production').
    """
    client = MlflowClient()
    # INSTRUCTION: Use client.transition_model_version_stage() to move the specified model version to the given stage (such as 'Staging', 'Production', etc.).
    # Set archive_existing_versions=False so only the specified version's stage changes.


def get_model_version_metrics(model_name: str, version: str) -> Dict[str, Any]:
    """
    Collects run metrics and tags for specified model version.
    """
    client = MlflowClient()
    # INSTRUCTION: Use client.get_model_version() to get the model version object.
    # Extract the run_id from the model version.
    # Retrieve the run using client.get_run(run_id).
    # Construct and return a dictionary with 'run_id', 'version', 'stage', 'metrics' (run.data.metrics), 'params' (run.data.params), and 'description' (from model version).


def get_best_version_by_metric(versions: Dict[str, Dict[str, Any]], metric_name: str, maximize: bool = True) -> str:
    """
    Returns the version string of the model version with the best metric value.
    """
    best_version = None
    best_value = None
    # INSTRUCTION: Iterate over the dictionary of versions. For each version, extract the metric value by 'metric_name'.
    # Compare values to identify the best version (maximum if maximize=True, minimum otherwise).
    # Return the version string with the best metric.


def document_promotion_decision(client: MlflowClient, model_name: str, version: str, rationale: str) -> None:
    """
    Updates model version description and tags with the rationale for promotion or archival.
    """
    # INSTRUCTION: Update the model version description using client.update_model_version with the provided rationale on the specific model/version.
    # Add a tag named 'promotion_rationale' to the model version using client.set_model_version_tag().


def main() -> None:
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    client = MlflowClient()
    model_name = 'HealthcareRiskPredictor'
    trained_run_ids = []
    # Dynamically import the tracker module from the experiment tracking activity
    runs_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../experiment_tracking/track_experiments_mlflow.py'))
    spec = spec_from_file_location("track_experiments_mlflow", runs_file)
    tracker_module = module_from_spec(spec)
    spec.loader.exec_module(tracker_module)
    # Instantiate the tracker
    tracker = tracker_module.HealthcareMLflowExperimentTracker("HealthcareRiskPrediction")
    healthcare_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/healthcare_patients.csv'))
    # INSTRUCTION: Use the tracker object to run two different model training experiments by calling tracker.run_training_experiment with different parameters (n_estimators, max_depth, random_state).
    # Collect the returned run_ids and store them in trained_run_ids.
    version_dict = {}
    # INSTRUCTION: For each run_id in trained_run_ids, do the following:
    # - Construct a description string indicating the model's parameters.
    # - Try to register the model version using register_model_version().
    # - If an exception occurs (for example, if model version already exists), fetch the latest version number using client.search_model_versions().
    # - Set the model stage to 'Staging' for the first run, and the default stage for the others using set_model_stage().
    # - For each registered version, retrieve its metrics and details using get_model_version_metrics() and store in version_dict.
    # INSTRUCTION: After registering, compare the versions based on the 'roc_auc' metric using get_best_version_by_metric().
    # Promote the best version to 'Production' using set_model_stage() and document the decision/rationale using document_promotion_decision().
    # For all other versions, move them to 'Archived' and document the rationale similarly.
    # Finally, log the completion of version comparison and registry update using logging.info().


if __name__ == "__main__":
    main()
