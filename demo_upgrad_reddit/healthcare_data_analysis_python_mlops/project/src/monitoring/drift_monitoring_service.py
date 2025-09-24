import os
import json
import logging
import mlflow
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from sklearn.metrics import mean_squared_error
from scipy.stats import wasserstein_distance, entropy
import requests

logger = logging.getLogger("drift_monitoring")
logger.setLevel(logging.INFO)

class DriftMonitoringService:
    """
    Real-time drift monitoring for a deployed MLflow healthcare AI model.
    Computes data and prediction drift against baseline and triggers alerts/events.
    """
    def __init__(
        self,
        model_name: str,
        model_stage: str = "Production",
        mlflow_tracking_uri: Optional[str] = None,
        baseline_profile_path: str = "outputs/baseline_profile.json",
        drift_thresholds: Optional[Dict[str, float]] = None,
        event_log_path: str = "outputs/drift_event_log.jsonl"
    ):
        if mlflow_tracking_uri:
            mlflow.set_tracking_uri(mlflow_tracking_uri)
        self.model_name = model_name
        self.model_stage = model_stage
        self.baseline_profile_path = baseline_profile_path
        self.drift_thresholds = drift_thresholds or {}
        self.event_log_path = event_log_path
        self.endpoint = self._get_production_endpoint()
        self.model_version = self._get_production_version()
        self.baseline_stats = self._load_baseline_profile()
        self.drift_events = []

    def _get_production_endpoint(self) -> str:
        port = 5001
        return f"http://localhost:{port}/invocations"

    def _get_production_version(self) -> str:
        from mlflow.tracking import MlflowClient
        client = MlflowClient()
        versions = client.get_latest_versions(self.model_name, stages=[self.model_stage])
        if not versions:
            raise Exception(f"No model in {self.model_stage} for: {self.model_name}")
        return str(versions[0].version)

    def _load_baseline_profile(self) -> Dict[str, Any]:
        if not os.path.exists(self.baseline_profile_path):
            raise FileNotFoundError(f"Baseline profile not found at {self.baseline_profile_path}.")
        with open(self.baseline_profile_path, "r") as f:
            return json.load(f)

    def _call_model(self, input_df: pd.DataFrame) -> Any:
        payload = input_df.to_dict(orient="list")
        try:
            response = requests.post(self.endpoint, json=payload, timeout=15)
            response.raise_for_status()
            predictions = response.json()
            return predictions
        except Exception as exc:
            logger.error(f"Prediction request failed: {exc}")
            return None

    def compute_feature_drift(self, curr_data: pd.DataFrame) -> Dict[str, float]:
        feature_drifts = {}
        for col in self.baseline_stats.get("feature_means", {}):
            if col in curr_data.columns:
                base_mean = self.baseline_stats["feature_means"][col]
                curr_mean = float(curr_data[col].mean())
                drift = abs(curr_mean - base_mean)
                feature_drifts[col] = drift
        return feature_drifts

    def compute_prediction_drift(self, pred_result: List[Any]) -> float:
        base_dist = self.baseline_stats.get("pred_label_distribution", None)
        if base_dist is None or not pred_result:
            return 0.0
        unique, counts = np.unique(np.array(pred_result).flatten(), return_counts=True)
        curr_dist = dict(zip(unique, counts / counts.sum()))
        all_labels = set(list(base_dist.keys()) + list(curr_dist.keys()))
        base_vec = np.array([base_dist.get(str(k), 0.0) for k in all_labels])
        curr_vec = np.array([curr_dist.get(str(k), 0.0) for k in all_labels])
        # Use symmetric KL divergence in case of nonzero alignment
        base_vec += 1e-8
        curr_vec += 1e-8
        kl1 = entropy(base_vec, curr_vec)
        kl2 = entropy(curr_vec, base_vec)
        return 0.5 * (kl1 + kl2)

    def check_and_log_drift(self, curr_data: pd.DataFrame, pred_result: List[Any], batch_id: str = None):
        feature_drift = self.compute_feature_drift(curr_data)
        pred_drift = self.compute_prediction_drift(pred_result)
        drift_alerts = {
            "feature": {},
            "prediction": False
        }
        for col, drift in feature_drift.items():
            thres = self.drift_thresholds.get("feature_means", {}).get(col, 0.1)
            if drift > thres:
                drift_alerts["feature"][col] = True
            else:
                drift_alerts["feature"][col] = False
        pred_thres = self.drift_thresholds.get("pred_kl", 0.1)
        drift_alerts["prediction"] = pred_drift > pred_thres
        event = {
            "batch_id": batch_id or os.urandom(4).hex(),
            "model_name": self.model_name,
            "model_version": self.model_version,
            "feature_drift": feature_drift,
            "pred_kl": pred_drift,
            "feature_drift_alerts": drift_alerts["feature"],
            "prediction_drift_alert": drift_alerts["prediction"],
            "detected": any(drift_alerts["feature"].values()) or drift_alerts["prediction"]
        }
        if event["detected"]:
            logger.warning(f"Drift detected: {event}")
        else:
            logger.info(f"No drift detected for batch: {event['batch_id']}")
        with open(self.event_log_path, "a") as f:
            f.write(json.dumps(event) + "
")
        self.drift_events.append(event)
        return event

    def monitor_stream(self, batch_data_files: List[str]):
        for batch_path in batch_data_files:
            df = pd.read_csv(batch_path)
            preds = self._call_model(df)
            if preds is None:
                continue
            event = self.check_and_log_drift(curr_data=df, pred_result=preds, batch_id=os.path.basename(batch_path))
            self._visualize_drift(event, df, preds)

    def _visualize_drift(self, event: Dict[str, Any], data: pd.DataFrame, pred_result: List[Any]):
        # Save drift histogram for features and prediction distribution per batch
        import matplotlib.pyplot as plt
        outdir = "outputs/drift_stats_visualizations"
        os.makedirs(outdir, exist_ok=True)
        # Feature drift
        feat_drift = event["feature_drift"]
        plt.figure(figsize=(10,4))
        plt.bar(list(feat_drift.keys()), list(feat_drift.values()))
        plt.xlabel("Feature")
        plt.ylabel("Mean Drift vs Baseline")
        plt.title(f"Feature Drift (batch {event['batch_id']})")
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"feature_drift_{event['batch_id']}.png"))
        plt.close()
        # Prediction distribution
        flat_preds = np.array(pred_result).flatten()
        unique, counts = np.unique(flat_preds, return_counts=True)
        plt.figure(figsize=(6,4))
        plt.bar(unique.astype(str), counts)
        plt.xlabel("Predicted Label")
        plt.ylabel("Count")
        plt.title(f"Predicted Label Distribution (batch {event['batch_id']})")
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, f"pred_dist_{event['batch_id']}.png"))
        plt.close()

    def get_logged_events(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.event_log_path):
            return []
        with open(self.event_log_path, "r") as f:
            return [json.loads(line) for line in f]

# --------- Baseline Profiling Utility ----------------
def generate_baseline_profile(data_path: str, model_endpoint: str, output_path: str) -> None:
    df = pd.read_csv(data_path)
    payload = df.to_dict(orient="list")
    try:
        response = requests.post(model_endpoint, json=payload, timeout=20)
        response.raise_for_status()
        preds = response.json()
    except Exception as exc:
        logger.error(f"Failed to call model for baseline predictions: {exc}")
        preds = []
    # Compute means
    feature_means = {col: float(df[col].mean()) for col in df.columns}
    # Compute prediction distribution (for sequence NER, this will be token labels)
    flat_preds = np.array(preds).flatten()
    unique, counts = np.unique(flat_preds, return_counts=True)
    distribution = {str(label): float(count)/max(1, counts.sum()) for label, count in zip(unique, counts)}
    baseline = {
        "feature_means": feature_means,
        "pred_label_distribution": distribution
    }
    with open(output_path, "w") as f:
        json.dump(baseline, f)
    logger.info(f"Baseline profile saved to {output_path}")

if __name__ == "__main__":
    # Generate baseline only if needed
    if not os.path.exists("outputs/baseline_profile.json"):
        generate_baseline_profile(
            data_path="data/clinical_ner_eval.csv",  # or other relevant historical batch
            model_endpoint="http://localhost:5001/invocations",
            output_path="outputs/baseline_profile.json"
        )
    drift_thresholds = {
        "feature_means": {},      # e.g., {"age": 2.0, "glucose": 5.0}
        "pred_kl": 0.15           # KL divergence warning threshold for pred distribution
    }
    monitor = DriftMonitoringService(
        model_name="ClinicalBERT_NER",
        model_stage="Production",
        baseline_profile_path="outputs/baseline_profile.json",
        drift_thresholds=drift_thresholds,
        event_log_path="outputs/drift_event_log.jsonl"
    )
    # Simulate batches for drift monitoring (files should mimic incoming feed)
    batch_filelist = [os.path.join("data/sim_batches", fn) for fn in os.listdir("data/sim_batches") if fn.endswith(".csv")]
    monitor.monitor_stream(batch_filelist)
    logger.info(f"Drift monitoring complete. See drift events in outputs/drift_event_log.jsonl. Visualizations are in outputs/drift_stats_visualizations/")