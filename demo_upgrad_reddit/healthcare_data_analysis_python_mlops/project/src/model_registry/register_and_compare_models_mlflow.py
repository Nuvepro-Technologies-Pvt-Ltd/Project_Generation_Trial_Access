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
    experiment = mlflow.get_experiment_by_name("HealthcareRiskPrediction")
    if not experiment:
        raise RuntimeError("Experiment 'HealthcareRiskPrediction' does not exist.")
    model_uri = f"runs:/{run_id}/model"
    # Register model only if it does not exist yet
    existing_models = [m for m in client.list_registered_models() if m.name == model_name]
    if not existing_models:
        client.create_registered_model(model_name)
    # Register a new model version
    registered_model = client.create_model_version(
        name=model_name,
        source=model_uri,
        run_id=run_id,
        description=description
    )
    return str(registered_model.version)


def set_model_stage(model_name: str, model_version: str, stage: str) -> None:
    """
    Transitions model version to a given stage in the MLflow registry (e.g., 'Staging', 'Production').
    """
    client = MlflowClient()
    client.transition_model_version_stage(
        name=model_name,
        version=model_version,
        stage=stage,
        archive_existing_versions=False
    )


def get_model_version_metrics(model_name: str, version: str) -> Dict[str, Any]:
    """
    Collects run metrics and tags for specified model version.
    """
    client = MlflowClient()
    mv = client.get_model_version(model_name, version)
    run_id = mv.run_id
    run = client.get_run(run_id)
    return {
        'run_id': run_id,
        'version': version,
        'stage': mv.current_stage,
        'metrics': run.data.metrics,
        'params': run.data.params,
        'description': mv.description
    }


def get_best_version_by_metric(versions: Dict[str, Dict[str, Any]], metric_name: str, maximize: bool = True) -> str:
    """
    Returns the version string of the model version with the best metric value.
    """
    best_version = None
    best_value = None
    for version, meta in versions.items():
        metrics = meta['metrics']
        value = metrics.get(metric_name)
        if value is None:
            continue
        if best_version is None or (maximize and value > best_value) or (not maximize and value < best_value):
            best_version = version
            best_value = value
    return best_version


def document_promotion_decision(client: MlflowClient, model_name: str, version: str, rationale: str) -> None:
    """
    Updates model version description and tags with the rationale for promotion or archival.
    """
    client.update_model_version(
        name=model_name,
        version=version,
        description=rationale
    )
    client.set_model_version_tag(
        name=model_name,
        version=version,
        key="promotion_rationale",
        value=rationale
    )


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
    # Train two different model configurations
    run_id_1 = tracker.run_training_experiment(
        data_path=healthcare_data_path, n_estimators=100, max_depth=5, random_state=42
    )
    run_id_2 = tracker.run_training_experiment(
        data_path=healthcare_data_path, n_estimators=150, max_depth=7, random_state=7
    )
    trained_run_ids = [run_id_1, run_id_2]
    version_dict = {}
    # Register both runs as model versions in the MLflow Model Registry
    for idx, (run_id, label) in enumerate(zip(trained_run_ids, ["rf-100x5", "rf-150x7"])):
        description = f"Trained with RandomForest params label: {label}"
        try:
            version = register_model_version(run_id, model_name, description)
        except Exception:
            # If registration fails because model exists and model version exists, fetch latest version
            version = None
            model_versions = [mv.version for mv in client.search_model_versions(f"name='{model_name}'")]
            if model_versions:
                # Pick latest version as a fallback
                version = str(max([int(v) for v in model_versions]))
        # Set model stage: first run to 'Staging', second to 'None' (initial state)
        stage = 'Staging' if idx == 0 else 'None'
        if version:
            set_model_stage(model_name, version, stage)
            version_dict[version] = get_model_version_metrics(model_name, version)
    # Compare metric (roc_auc) and promote the best to 'Production', archive the others
    metric_name = 'roc_auc'
    best_version = get_best_version_by_metric(version_dict, metric_name, maximize=True)
    # Corrected syntax error: removed extra closing parenthesis at end of rationale assignment
    rationale = f"Promoted to Production: best {metric_name} = {version_dict[best_version]['metrics'][metric_name]}. See MLflow run."
    set_model_stage(model_name, best_version, 'Production')
    document_promotion_decision(client, model_name, best_version, rationale)
    for v in version_dict:
        if v != best_version:
            set_model_stage(model_name, v, 'Archived')
            document_promotion_decision(
                client, model_name, v,
                f"Archived: lesser {metric_name} ({version_dict[v]['metrics'][metric_name]}) than prod version ({version_dict[best_version]['metrics'][metric_name]})."
            )
    logging.info(f"Comparison complete: Production version {best_version}. All stages and rationales updated in registry.")


if __name__ == "__main__":
    main()
