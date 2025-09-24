import os
import time
import json
import threading
from typing import Dict, Any, Tuple, List
import logging
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, chisquare
from sklearn.metrics import accuracy_score, roc_auc_score
import mlflow
from mlflow.tracking import MlflowClient
import requests

class DataStreamSimulator:
    """
    Simulates new data input streams to the deployed model endpoint.
    """
    def __init__(self, data_path: str, batch_size: int = 16):
        self.data = pd.read_csv(data_path)
        self.features = self.data.drop('target', axis=1)
        self.targets = self.data['target']
        self.batch_size = batch_size
        self.idx = 0

    def has_next(self) -> bool:
        return self.idx < len(self.features)

    def next_batch(self) -> Tuple[pd.DataFrame, pd.Series]:
        start = self.idx
        end = min(self.idx + self.batch_size, len(self.features))
        batch_X = self.features.iloc[start:end].reset_index(drop=True)
        batch_y = self.targets.iloc[start:end].reset_index(drop=True)
        self.idx = end
        return batch_X, batch_y

class DeployedModelInvoker:
    """
    Invokes the deployed model endpoint for predictions on input data.
    """
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url

    def predict(self, X: pd.DataFrame) -> List[Any]:
        records = X.to_dict(orient='records')
        resp = requests.post(self.endpoint_url, json={"instances": records})
        resp.raise_for_status()
        return resp.json()['predictions']

class DriftDetector:
    """
    Detects data and concept drift for streamed batches against reference statistics.
    """
    def __init__(self, reference_path: str, threshold_p: float = 0.01):
        self.ref_df = pd.read_csv(reference_path)
        self.ref_X = self.ref_df.drop('target', axis=1)
        self.ref_y = self.ref_df['target']
        self.p_threshold = threshold_p
        self.feature_types = self._infer_feature_types(self.ref_X)
        self.ref_stats = self._compute_feature_stats(self.ref_X)

    def _infer_feature_types(self, X: pd.DataFrame) -> Dict[str, str]:
        types = {}
        for col in X.columns:
            if pd.api.types.is_numeric_dtype(X[col]):
                types[col] = 'num'
            else:
                types[col] = 'cat'
        return types

    def _compute_feature_stats(self, X: pd.DataFrame) -> Dict[str, Any]:
        stats = {}
        for col in X.columns:
            if self.feature_types[col] == 'num':
                stats[col] = X[col].values
            else:
                stats[col] = X[col].value_counts(normalize=True).to_dict()
        return stats

    def feature_drift(self, X_new: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        drift_report = {}
        for col in X_new.columns:
            if self.feature_types[col] == 'num':
                stat_ref = self.ref_stats[col]
                stat_new = X_new[col].values
                ks_res = ks_2samp(stat_ref, stat_new)
                drifted = ks_res.pvalue < self.p_threshold
                drift_report[col] = {"p_value": float(ks_res.pvalue), "drifted": drifted, "statistic": float(ks_res.statistic)}
            else:
                ref_dist = self.ref_stats[col]
                new_dist = X_new[col].value_counts(normalize=True).to_dict()
                cats = list(set(list(ref_dist.keys()) + list(new_dist.keys())))
                ref_counts = np.array([ref_dist.get(c, 0) for c in cats]) + 1e-9
                new_counts = np.array([new_dist.get(c, 0) for c in cats]) + 1e-9
                chisq_stats = chisquare(new_counts, ref_counts)
                drifted = chisq_stats.pvalue < self.p_threshold
                drift_report[col] = {"p_value": float(chisq_stats.pvalue), "drifted": drifted, "statistic": float(chisq_stats.statistic)}
        return drift_report

    def concept_drift(self, y_true: np.ndarray, y_pred: np.ndarray, ref_acc: float, ref_auc: float) -> Dict[str, Any]:
        acc = accuracy_score(y_true, y_pred)
        auc = roc_auc_score(y_true, y_pred)
        drift_results = {}
        if abs(ref_acc - acc) > 0.1:  # 10% drop threshold
            drift_results["accuracy_drift"] = {"reference": ref_acc, "current": acc, "drifted": True}
        else:
            drift_results["accuracy_drift"] = {"reference": ref_acc, "current": acc, "drifted": False}
        if abs(ref_auc - auc) > 0.1:
            drift_results["roc_auc_drift"] = {"reference": ref_auc, "current": auc, "drifted": True}
        else:
            drift_results["roc_auc_drift"] = {"reference": ref_auc, "current": auc, "drifted": False}
        return drift_results

class DriftMonitoringDashboard:
    """
    Simple live dashboard engine for drift alerts and statistics.
    Aggregates drift/detection events and logs remediation actions.
    """
    def __init__(self, evidence_dir: str = './monitoring_evidence'):
        self.evidence_dir = os.path.abspath(evidence_dir)
        os.makedirs(self.evidence_dir, exist_ok=True)
        self.events_log_path = os.path.join(self.evidence_dir, 'drift_events_log.jsonl')
        self.remediation_log_path = os.path.join(self.evidence_dir, 'remediation_log.jsonl')
        self.events = []
        self.remediations = []
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    def record_event(self, event: dict):
        self.events.append(event)
        with open(self.events_log_path, 'a') as f:
            f.write(json.dumps(event) + '
')

    def trigger_remediation(self, evidence: dict, suggested_action: str):
        remediation_entry = {
            "detected_at": time.strftime('%Y-%m-%d %H:%M:%S'),
            "evidence": evidence,
            "suggested_action": suggested_action
        }
        self.remediations.append(remediation_entry)
        with open(self.remediation_log_path, 'a') as f:
            f.write(json.dumps(remediation_entry) + '
')
        logging.info(f"Remediation triggered: {suggested_action}")

    def summarize(self) -> Tuple[str, str]:
        events_log = self.events_log_path
        remediation_log = self.remediation_log_path
        return events_log, remediation_log

    def serve_live_dashboard(self):
        from flask import Flask, jsonify, send_file, render_template_string
        app = Flask(__name__)
        @app.route('/monitoring/alerts')
        def alerts():
            events = []
            remediation = []
            if os.path.exists(self.events_log_path):
                with open(self.events_log_path, 'r') as f:
                    events = [json.loads(l) for l in f.readlines()]
            if os.path.exists(self.remediation_log_path):
                with open(self.remediation_log_path, 'r') as f:
                    remediation = [json.loads(l) for l in f.readlines()]
            resp = {"drift_events": events, "remediations": remediation}
            return jsonify(resp)
        @app.route('/')
        def dashboard():
            alerts_url = '/monitoring/alerts'
            html = '''
                <html><head><title>Clinical Model Monitoring Dashboard</title></head>
                <body>
                    <h1>Model Drift Monitoring Dashboard</h1>
                    <div id="alerts"></div>
                    <script>
                    async function refresh() {
                        let resp = await fetch('''' + alerts_url + '''');
                        let data = await resp.json();
                        let content = '<h2>Drift Events</h2><pre>' + JSON.stringify(data.drift_events, null, 2) + '</pre>';
                        content += '<h2>Remediation Log</h2><pre>' + JSON.stringify(data.remediations, null, 2) + '</pre>';
                        document.getElementById('alerts').innerHTML = content;
                    }
                    setInterval(refresh, 4000); window.onload = refresh;
                    </script>
                </body></html>
            '''
            return render_template_string(html)
        app.run(port=8099, debug=False)

class ProductionReferenceMetrics:
    @staticmethod
    def from_mlflow(model_name: str, stage: str = "Production") -> Tuple[Any, float, float]:
        client = MlflowClient()
        latest = client.get_latest_versions(model_name, [stage])
        if not latest:
            raise RuntimeError(f"No {stage} version for model {model_name}")
        run_id = latest[0].run_id
        # Recover test arrays logged during best run
        art_dir = mlflow.artifacts.download_artifacts(f"runs:/{run_id}/artifacts_run_{run_id}")
        arrays_file = os.path.join(art_dir, 'test_arrays.npz')
        arrays = np.load(arrays_file)
        X = arrays['X_test']
        y = arrays['y_test']
        model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")
        y_pred = model.predict(X)
        acc = accuracy_score(y, y_pred)
        auc = roc_auc_score(y, y_pred)
        return (arrays, acc, auc)

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    # Hyperparams/configs
    model_name = "HealthcareRiskPredictor"
    stage = "Production"
    cloud_endpoint_url = os.environ.get("CLINICAL_MODEL_ENDPOINT", "http://localhost:6001/invocations")
    reference_data_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/healthcare_patients.csv'))
    monitoring_evidence_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../monitoring_evidence'))
    # Step 1: Get production reference metrics
    arrays, ref_acc, ref_auc = ProductionReferenceMetrics.from_mlflow(model_name=model_name, stage=stage)
    X_ref = pd.read_csv(reference_data_csv).drop('target', axis=1)
    # Step 2: Prepare drift monitoring tools
    dashboard = DriftMonitoringDashboard(evidence_dir=monitoring_evidence_dir)
    detector = DriftDetector(reference_path=reference_data_csv, threshold_p=0.01)
    invoker = DeployedModelInvoker(endpoint_url=cloud_endpoint_url)
    simulator = DataStreamSimulator(data_path=reference_data_csv, batch_size=24)
    # Step 3: Start monitoring dashboard in a separate thread
    dashboard_thread = threading.Thread(target=dashboard.serve_live_dashboard, daemon=True)
    dashboard_thread.start()
    # Step 4: Simulate incoming data batches; invoke deployed model; monitor
    batch_idx = 0
    while simulator.has_next():
        batch_X, batch_y = simulator.next_batch()
        try:
            y_pred = invoker.predict(batch_X)
            if isinstance(y_pred, dict) and 'predictions' in y_pred:
                y_pred = y_pred['predictions']
            y_pred = np.array(y_pred)
        except Exception as ex:
            dashboard.record_event({'timestamp': time.time(), 'type': 'inference_error', 'error': str(ex), 'batch': batch_idx})
            continue
        feat_drift = detector.feature_drift(batch_X)
        concept_drift = detector.concept_drift(batch_y, y_pred, ref_acc, ref_auc)
        drift_instance = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'batch_index': batch_idx,
            'feature_drift': feat_drift,
            'concept_drift': concept_drift
        }
        dashboard.record_event(drift_instance)
        # Remediation: alert if any features or metrics drifted
        drifted_feats = [f for f, v in feat_drift.items() if v['drifted']]
        concept_issues = [k for k, v in concept_drift.items() if v['drifted']]
        if drifted_feats or concept_issues:
            evidence = {'batch': batch_idx, 'feature_drifted': drifted_feats, 'concept_drifted': concept_issues, 'metrics': drift_instance}
            recommended_action = "Alert: Data/model drift detected. Investigate input distribution or retrain model as needed."
            dashboard.trigger_remediation(evidence, recommended_action)
        batch_idx += 1
        time.sleep(2)
    # Step 5: Final evidence/log output
    events_log, remediation_log = dashboard.summarize()
    print(f"Monitoring complete. Events log: {events_log} | Remediation log: {remediation_log}")

if __name__ == "__main__":
    main()
