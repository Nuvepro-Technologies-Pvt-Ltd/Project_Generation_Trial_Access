import os
import logging
import mlflow
from mlflow.tracking import MlflowClient
import subprocess
import requests
from typing import Dict, Any

logger = logging.getLogger("deployment")
logger.setLevel(logging.INFO)

class ModelDeployer:
    """
    Automates packaging a registered MLflow model as a container and deploying as a REST API.
    """
    def __init__(self, registry_model_name: str, model_stage: str = "Production", mlflow_tracking_uri: str = None):
        if mlflow_tracking_uri:
            mlflow.set_tracking_uri(mlflow_tracking_uri)
        self.client = MlflowClient()
        self.model_name = registry_model_name
        self.model_stage = model_stage
        self.model_info = self.select_production_model()

    def select_production_model(self) -> Dict[str, Any]:
        versions = self.client.get_latest_versions(self.model_name, stages=[self.model_stage])
        if not versions:
            raise Exception(f"No model in stage '{self.model_stage}' found for {self.model_name}")
        mv = versions[0]
        logger.info(f"Selected {self.model_name} version {mv.version} for deployment (stage {self.model_stage})")
        return {
            "version": mv.version,
            "run_id": mv.run_id,
            "source": mv.source
        }

    def package_model_as_container(self, image_name: str) -> str:
        model_uri = f"models:/{self.model_name}/{self.model_stage}"
        logger.info(f"Building container image for model URI: {model_uri}")
        cmd = [
            "mlflow", "models", "build-docker",
            "-m", model_uri,
            "-n", image_name
        ]
        try:
            subprocess.run(cmd, check=True)
            logger.info(f"Container image built and tagged as: {image_name}")
        except FileNotFoundError as fnf_err:
            # More descriptive error if mlflow CLI or Docker is missing
            logger.error("mlflow CLI or Docker not found. Please ensure both are installed and accessible in your PATH.")
            raise
        except Exception as e:
            logger.error(f"Failed to build docker image: {e}")
            raise
        return image_name

    def deploy_container(self, image_name: str, container_name: str, host_port: int = 5001) -> Dict[str, Any]:
        docker_cmd = [
            "docker", "run", "-d",
            "--rm",
            "--name", container_name,
            "-p", f"{host_port}:8080",
            image_name
        ]
        container_id = None  # Ensure container_id is always defined
        try:
            # Try a pre-flight check to ensure Docker is accessible
            try:
                subprocess.run(["docker", "--version"], check=True, capture_output=True)
            except FileNotFoundError:
                logger.error("Docker is not installed or not found in PATH. Please install Docker to continue.")
                raise
            except Exception as dck_err:
                logger.error(f"Unable to execute 'docker' CLI. Details: {dck_err}")
                raise
            # Stop previous instance if exists (does not throw on fail)
            subprocess.run(["docker", "stop", container_name], check=False)
            result = subprocess.run(docker_cmd, check=True, capture_output=True, text=True)
            # Ensure docker output was actually returned
            if result.stdout:
                container_id = result.stdout.strip().split("
")[-1]
            else:
                container_id = "unknown"
            logger.info(f"Started container: {container_id}")
        except subprocess.CalledProcessError as exc:
            logger.error(f"Failed to start container. Docker output: {exc.stderr}")
            raise
        except Exception as exc:
            logger.error(f"Failed to start container: {exc}")
            raise
        return {
            "container_id": container_id,
            "host_port": host_port,
            "endpoint": f"http://localhost:{host_port}/invocations"
        }

    def verify_deployment_health(self, endpoint: str) -> Dict[str, Any]:
        health_url = endpoint.replace("/invocations", "/ping")
        try:
            response = requests.get(health_url, timeout=10)
            healthy = response.text.strip().lower() == "pong"
            logger.info(f"Healthcheck {health_url}: status={response.status_code} ({response.text.strip()})")
        except Exception as e:
            logger.error(f"Healthcheck failed: {e}")
            healthy = False
        return {"healthy": healthy, "health_url": health_url}

    def fetch_deployment_logs(self, container_name: str) -> str:
        try:
            logs = subprocess.check_output(["docker", "logs", container_name], text=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to fetch logs for container {container_name}: {e}")
            logs = ""
        except Exception as e:
            logger.error(f"Error while fetching logs: {e}")
            logs = ""
        return logs

    def record_release_metadata(self, artifact_path: str, metadata: Dict[str, Any]):
        os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
        with open(artifact_path, "w") as f:
            for k, v in metadata.items():
                f.write(f"{k}: {v}
")

    def run(self, image_tag: str = "clinicalbert_ner_service:latest", container_name: str = "clinicalbert_ner_service", port: int = 5001):
        logger.info("===== Starting Containerized Model Deployment Pipeline =====")
        # Optionally warn or document Docker/MLflow requirements for reproducibility
        logger.info("[INFO] This script requires Docker and MLflow CLI tools installed and available in system PATH.")
        logger.info("[INFO] Expected model image runtime requirements (Dockerfile base image will include python, MLflow, transformers, and additional dependencies as captured by the MLflow model artifact requirements.txt. Ensure your MLflow model is logged with all dependencies or add a requirements.txt to support your model.")
        image_name = self.package_model_as_container(image_name=image_tag)
        deployment = self.deploy_container(image_name=image_name, container_name=container_name, host_port=port)
        health = self.verify_deployment_health(endpoint=deployment["endpoint"])
        logs = self.fetch_deployment_logs(container_name)
        metadata = {
            "model_name": self.model_name,
            "model_version": str(self.model_info["version"]),
            "model_uri": f"models:/{self.model_name}/{self.model_stage}",
            "container_id": deployment["container_id"],
            "api_endpoint": deployment["endpoint"],
            "status": "Healthy" if health["healthy"] else "Unhealthy"
        }
        logger.info(f"Deployment Info: {metadata}")
        self.record_release_metadata("outputs/deployment_info.txt", metadata)
        self.record_release_metadata("outputs/deployment_logs.txt", {"logs": logs})
        return metadata

def main():
    deployer = ModelDeployer(registry_model_name="ClinicalBERT_NER", model_stage="Production")
    result = deployer.run(
        image_tag="clinicalbert_ner_service:latest",
        container_name="clinicalbert_ner_service",
        port=5001
    )
    logger.info(f"Deployed REST API at: {result['api_endpoint']} (Status: {result['status']})")
    logger.info(f"Deployment details recorded in outputs/deployment_info.txt and logs in outputs/deployment_logs.txt")
    # ================== PIPELINE ORCHESTRATION/CI =======================
    # For production/CI automation, trigger this script from your CI/CD tool or via CRON.
    # For example, to run as a GitHub Action or via shell: python src/deployment/deploy_model_container.py
    # Place your orchestration manifest or CI workflow definition (like .github/workflows/deploy.yml) separately as needed.

if __name__ == "__main__":
    main()
