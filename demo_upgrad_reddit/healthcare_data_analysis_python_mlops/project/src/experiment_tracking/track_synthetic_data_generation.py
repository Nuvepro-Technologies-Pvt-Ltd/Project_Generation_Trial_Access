import os
import mlflow
import mlflow.pyfunc
import uuid
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any
from sklearn.metrics import mean_squared_error
from src.data.synthetic_healthcare_loader import load_healthcare_dataset
from src.models.gan_synthesizer import GANHealthcareSynthesizer
from src.models.vae_synthesizer import VAEHealthcareSynthesizer
from src.monitoring.privacy_fidelity_metrics import compute_privacy_score, compute_fidelity_score

logger = logging.getLogger("experiment_tracking")
logger.setLevel(logging.INFO)

class ExperimentRunner:
    """
    Executes and tracks synthetic data generation experiments for healthcare using MLflow.
    Each run logs config, metrics (privacy, fidelity), and generated data artifact.
    """
    def __init__(self, experiment_name: str):
        mlflow.set_experiment(experiment_name)
        self.experiment_name = experiment_name

    def run_gan_experiment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        data = load_healthcare_dataset()
        gan = GANHealthcareSynthesizer(
            input_dim=config["input_dim"],
            latent_dim=config["latent_dim"],
            hidden_dim=config["hidden_dim"],
            epochs=config["epochs"]
        )
        gan.train(data)
        synthetic = gan.generate(n_samples=len(data))
        privacy = compute_privacy_score(data, synthetic)
        fidelity = compute_fidelity_score(data, synthetic)
        synthetic_path = f"outputs/synth_gan_{uuid.uuid4().hex}.csv"
        pd.DataFrame(synthetic).to_csv(synthetic_path, index=False)
        return {
            "description": f"GAN run: latent_dim={config['latent_dim']}, hidden_dim={config['hidden_dim']}",
            "params": config,
            "metrics": {"privacy_score": privacy, "fidelity_score": fidelity},
            "artifact": synthetic_path
        }

    def run_vae_experiment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        data = load_healthcare_dataset()
        vae = VAEHealthcareSynthesizer(
            input_dim=config["input_dim"],
            latent_dim=config["latent_dim"],
            hidden_dim=config["hidden_dim"],
            epochs=config["epochs"]
        )
        vae.train(data)
        synthetic = vae.generate(n_samples=len(data))
        privacy = compute_privacy_score(data, synthetic)
        fidelity = compute_fidelity_score(data, synthetic)
        synthetic_path = f"outputs/synth_vae_{uuid.uuid4().hex}.csv"
        pd.DataFrame(synthetic).to_csv(synthetic_path, index=False)
        return {
            "description": f"VAE run: latent_dim={config['latent_dim']}, hidden_dim={config['hidden_dim']}",
            "params": config,
            "metrics": {"privacy_score": privacy, "fidelity_score": fidelity},
            "artifact": synthetic_path
        }

    def track_run(self, model_type: str, run_details: Dict[str, Any], tags: Dict[str, Any]):
        with mlflow.start_run(run_name=f"{model_type}_synthetic_run") as run:
            mlflow.set_tags(tags)
            mlflow.log_params(run_details["params"])
            mlflow.log_metrics(run_details["metrics"])
            mlflow.set_tag("description", run_details["description"])
            mlflow.log_artifact(run_details["artifact"], artifact_path="synthetic_outputs")
            logger.info(f"Tracked {model_type} run: {run_details['description']}")

if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    runner = ExperimentRunner(experiment_name="Healthcare_Synth_Data_Generation")
    # Model Variation 1: GAN
    gan_config = {"input_dim": 25, "latent_dim": 32, "hidden_dim": 128, "epochs": 100}
    gan_details = runner.run_gan_experiment(gan_config)
    runner.track_run(
        model_type="GAN",
        run_details=gan_details,
        tags={"privacy_objective": "high", "synth_model": "GAN", "experiment_variation": "baseline_gan"}
    )
    # Model Variation 2: VAE with different latent size
    vae_config = {"input_dim": 25, "latent_dim": 16, "hidden_dim": 64, "epochs": 100}
    vae_details = runner.run_vae_experiment(vae_config)
    runner.track_run(
        model_type="VAE",
        run_details=vae_details,
        tags={"privacy_objective": "high", "synth_model": "VAE", "experiment_variation": "vae_latent16"}
    )
    logger.info("All experimental runs tracked in MLflow. Use the UI to compare privacy and fidelity metrics.")