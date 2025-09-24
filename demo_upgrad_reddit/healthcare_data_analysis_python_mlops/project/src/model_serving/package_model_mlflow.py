import os
import mlflow
from mlflow.tracking import MlflowClient
import json
import shutil
from typing import Dict
import logging
from mlflow.models.signature import infer_signature
import pandas as pd

class ModelPackager:
    """
    Packages a trained Healthcare ML model from MLflow Model Registry for production deployment.
    Includes input/output schema, metadata, and requirements for reproducible and portable ML serving.
    """
    def __init__(self, model_name: str, stage: str, export_dir: str = "./packaged_model_export"):
        self.model_name = model_name
        self.stage = stage
        self.export_dir = os.path.abspath(export_dir)
        self.client = MlflowClient()
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    def get_latest_model_version(self) -> str:
        versions = self.client.get_latest_versions(name=self.model_name, stages=[self.stage])
        if not versions:
            logging.error(f"No model version in stage '{self.stage}' for model '{self.model_name}'")
            raise RuntimeError(f"No model version in stage '{self.stage}' for model '{self.model_name}'")
        return versions[0].version

    def export_model_artifact(self, version: str) -> str:
        dst_dir = os.path.join(self.export_dir, f"{self.model_name}_v{version}")
        if os.path.exists(dst_dir):
            shutil.rmtree(dst_dir)  # Ensure no residue
        os.makedirs(dst_dir)
        mv = self.client.get_model_version(self.model_name, version)
        run_id = mv.run_id
        model_src = f"runs:/{run_id}/model"
        # Download the model artifact locally
        local_path = mlflow.artifacts.download_artifacts(artifact_uri=model_src, dst_path=dst_dir)
        # Save MLmodel YAML and any additional artifacts
        artifact_metadata = {
            "source": model_src,
            "local_dir": local_path,
            "run_id": run_id,
            "model_name": self.model_name,
            "version": version,
            "stage": self.stage,
            "description": mv.description
        }
        metadata_f = os.path.join(dst_dir, "model_metadata.json")
        with open(metadata_f, "w") as f:
            json.dump(artifact_metadata, f, indent=2)
        return dst_dir

    def retrieve_model(self, version: str):
        mv = self.client.get_model_version(self.model_name, version)
        run_id = mv.run_id
        model_uri = f"runs:/{run_id}/model"
        model = mlflow.sklearn.load_model(model_uri)
        return model, model_uri

    def infer_and_save_schema(self, model, version: str, model_uri: str, dst_dir: str):
        client = self.client
        mv = client.get_model_version(self.model_name, version)
        run_id = mv.run_id
        run = client.get_run(run_id)
        # Download test arrays artifact for schema inference
        artifact_dir = mlflow.artifacts.download_artifacts(
            f"runs:/{run_id}/artifacts_run_{run_id}", dst_path=dst_dir
        )
        array_npz = os.path.join(artifact_dir, "test_arrays.npz")
        if os.path.exists(array_npz):
            import numpy as np  # Local import if artifact exists
            arrays = np.load(array_npz)
            X_test = arrays["X_test"]
            y_test = arrays["y_test"]
            all_feats_f = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/healthcare_patients.csv'))
            df = pd.read_csv(all_feats_f)
            features = df.drop("target", axis=1).columns.tolist()
            X_df = pd.DataFrame(X_test, columns=features)
            y_ser = pd.Series(y_test, name="target")
            # Infer MLflow signature from data and prediction
            signature = infer_signature(X_df, model.predict(X_df))
            # Save MLflow signature for modern deployment tools
            signature_path = os.path.join(dst_dir, "mlflow_signature.json")
            with open(signature_path, "w") as sig_file:
                # JSON-serializable representation
                json.dump(signature.to_dict(), sig_file, indent=2)
            # Also store a schema summary for convenience
            schema_dict = {
                "inputs": [
                    {"name": c, "type": str(X_df.dtypes[i])} for i, c in enumerate(X_df.columns)
                ],
                "outputs": {"name": "prediction", "type": str(model.predict(X_df[:1]).dtype)}
            }
        else:
            logging.error("Test arrays not found for schema inference.")
            raise RuntimeError("Test arrays not found for schema inference.")
        sig_path = os.path.join(dst_dir, "input_output_schema.json")
        with open(sig_path, "w") as f:
            json.dump(schema_dict, f, indent=2)
        # Save the MLmodel YAML if it exists
        mlmodel_path = os.path.join(dst_dir, "MLmodel.yaml")
        if os.path.exists(os.path.join(dst_dir, "MLmodel")):
            mlmodel_f = os.path.join(dst_dir, "MLmodel")
            with open(mlmodel_f, "r") as source, open(mlmodel_path, "w") as dest:
                dest.write(source.read())
        return sig_path

    def export_requirements(self, dst_dir: str, version: str):
        # Fetch run's conda.yaml, requirements.txt from MLflow; add to exported folder if present
        mv = self.client.get_model_version(self.model_name, version)
        run_id = mv.run_id
        model_dir = mlflow.artifacts.download_artifacts(f"runs:/{run_id}/model", dst_path=dst_dir)
        req_path = os.path.join(model_dir, "requirements.txt")
        conda_path = os.path.join(model_dir, "conda.yaml")
        if os.path.exists(req_path):
            shutil.copy2(req_path, os.path.join(dst_dir, "requirements.txt"))
        if os.path.exists(conda_path):
            shutil.copy2(conda_path, os.path.join(dst_dir, "conda.yaml"))

    def package(self) -> str:
        logging.info(f"Packaging model '{self.model_name}' [{self.stage}] for production deployment.")
        version = self.get_latest_model_version()
        dst_dir = self.export_model_artifact(version)
        model, model_uri = self.retrieve_model(version)
        self.infer_and_save_schema(model, version, model_uri, dst_dir)
        self.export_requirements(dst_dir, version)
        # Ensure target ZIP directory exists for canonical artifact output
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
        packaged_zip_base = os.path.join(self.export_dir, f"{self.model_name}_v{version}")
        packaged_zip = shutil.make_archive(base_name=packaged_zip_base, format="zip", root_dir=dst_dir)
        # Move/copy the ZIP archive into the export_dir path for standardized artifact location
        std_zip_path = os.path.join(self.export_dir, os.path.basename(packaged_zip))
        if os.path.abspath(packaged_zip) != os.path.abspath(std_zip_path):
            shutil.move(packaged_zip, std_zip_path)
        logging.info(f"Model packaged at {std_zip_path}")
        return std_zip_path

def main() -> None:
    model_name = "HealthcareRiskPredictor"
    stage = "Production"
    packager = ModelPackager(model_name=model_name, stage=stage)
    try:
        packaged_path = packager.package()
        print(f"Packaged model artifact for deployment: {packaged_path}")
    except Exception as e:
        logging.error(f"Model packaging failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
