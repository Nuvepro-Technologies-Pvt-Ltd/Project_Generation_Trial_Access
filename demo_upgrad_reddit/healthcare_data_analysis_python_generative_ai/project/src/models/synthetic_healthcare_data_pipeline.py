import os
import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from opacus import PrivacyEngine
from sklearn.metrics import mutual_info_score, silhouette_score

# Define device as a global constant for code cleanliness
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

class TabularHealthcareDataset(Dataset):
    """
    Tabular dataset for structured healthcare data (post-normalization, ML-ready).
    """
    def __init__(self, data: pd.DataFrame):
        self.data = data.reset_index(drop=True)
        self.arr = self.data.to_numpy(dtype=np.float32)
    def __len__(self) -> int:
        return self.arr.shape[0]
    def __getitem__(self, idx: int) -> torch.Tensor:
        return torch.tensor(self.arr[idx], dtype=torch.float32)

class TabularVAE(nn.Module):
    """
    Variational Autoencoder for structured tabular healthcare data.
    """
    def __init__(self, input_dim: int, latent_dim: int = 32):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
        )
        self.fc_mu = nn.Linear(64, latent_dim)
        self.fc_logvar = nn.Linear(64, latent_dim)
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, input_dim)
        )
    def encode(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        h = self.encoder(x)
        return self.fc_mu(h), self.fc_logvar(h)
    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        return self.decoder(z)
    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        recon = self.decode(z)
        return recon, mu, logvar
    def sample(self, num_samples: int, device: str) -> torch.Tensor:
        z = torch.randn(num_samples, self.fc_mu.out_features, device=device)
        samples = self.decode(z)
        return samples

# Loss function for VAE

def vae_loss(recon_x: torch.Tensor, x: torch.Tensor, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
    recon_loss = nn.MSELoss()(recon_x, x)
    kl_div = -0.5 * torch.mean(1 + logvar - mu.pow(2) - logvar.exp())
    return recon_loss + kl_div

# Helper to validate config and provide defaults

def validate_config(cfg: Dict[str, Any], required: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate config dictionary for required keys. If missing, set to defaults or raise error.
    """
    checked = cfg.copy()
    for k, default in required.items():
        if k not in checked:
            if default is None:
                raise ValueError(f"Missing required config value: {k}")
            checked[k] = default
    return checked

# Train VAE with optional privacy

def train_vae_with_privacy(
    data_path: str,
    config_path: str,
    model_save_path: str,
    privacy: bool = True,
    epsilon: float = 1.0,
    delta: float = 1e-5,
    max_grad_norm: float = 1.0,
    device: str = DEVICE
) -> Dict[str, Any]:
    """
    Train Tabular VAE on healthcare data. Supports Differential Privacy via Opacus PrivacyEngine.
    """
    logging.basicConfig(filename=os.path.join(os.path.dirname(model_save_path), 'vae_training.log'), level=logging.INFO)
    with open(config_path, 'r') as f:
        cfg = json.load(f)

    # Validate the config and provide defaults or raise for mandatory settings
    required = {
        'seed': 42,
        'batch_size': 32,
        'latent_dim': 32,
        'lr': 1e-3,
        'epochs': 20
    }
    cfg = validate_config(cfg, required)
    if privacy and ('noise_multiplier' not in cfg or cfg['noise_multiplier'] is None):
        # Differentially Private training requires non-None noise_multiplier
        raise ValueError("Differential Privacy enabled but 'noise_multiplier' not provided in config or is None.")

    df = pd.read_csv(data_path)
    np.random.seed(cfg['seed'])
    torch.manual_seed(cfg['seed'])
    dataset = TabularHealthcareDataset(df)
    loader = DataLoader(dataset, batch_size=cfg['batch_size'], shuffle=True, drop_last=True)
    model = TabularVAE(input_dim=dataset.arr.shape[1], latent_dim=cfg['latent_dim']).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg['lr'])
    if privacy:
        # Set noise_multiplier properly from config
        privacy_engine = PrivacyEngine(
            model,
            batch_size=cfg['batch_size'],
            sample_size=len(dataset),
            alphas=[10, 100],
            noise_multiplier=cfg['noise_multiplier'],
            max_grad_norm=max_grad_norm,
        )
        privacy_engine.attach(optimizer)
    else:
        privacy_engine = None
    train_losses = []
    for epoch in range(cfg['epochs']):
        model.train()
        epoch_loss = 0.0
        for batch in loader:
            batch = batch.to(device)
            optimizer.zero_grad()
            recon, mu, logvar = model(batch)
            loss = vae_loss(recon, batch, mu, logvar)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * batch.size(0)
        avg_loss = epoch_loss / len(dataset)
        train_losses.append(avg_loss)
        logging.info(f"Epoch {epoch+1}/{cfg['epochs']} | Loss: {avg_loss:.4f}")
    torch.save(model.state_dict(), model_save_path)
    privacy_report = {}
    if privacy and hasattr(optimizer, 'privacy_engine'):
        epsilon_spent, best_alpha = optimizer.privacy_engine.get_privacy_spent(delta)
        privacy_report = {'epsilon': epsilon_spent, 'best_alpha': best_alpha, 'delta': delta}
        logging.info(f"Differential Privacy Epsilon spent: {epsilon_spent}, Best Alpha: {best_alpha}, Delta: {delta}")
    return {
        'final_loss': train_losses[-1],
        'privacy_report': privacy_report,
        'model_path': model_save_path,
        'train_losses': train_losses
    }

# Generate synthetic data from trained VAE weight

def sample_synthetic_data(model_path: str, config_path: str, num_samples: int, output_path: str, device: str = DEVICE) -> None:
    """
    Load trained VAE weights and sample synthetic tabular healthcare data.
    """
    with open(config_path, 'r') as f:
        cfg = json.load(f)
    if 'data_path' in cfg:
        df = pd.read_csv(cfg['data_path'])
    else:
        raise ValueError("'data_path' field must exist in model config JSON.")
    model = TabularVAE(input_dim=df.shape[1], latent_dim=cfg.get('latent_dim', 32)).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    with torch.no_grad():
        syn_arr = model.sample(num_samples, device).cpu().numpy()
    colnames = df.columns
    syn_df = pd.DataFrame(syn_arr, columns=colnames)
    syn_df = syn_df.clip(lower=0)  # Practical post-processing
    syn_df.to_csv(output_path, index=False)

class PrivacyUtilityValidator:
    """
    Evaluates the utility and privacy of synthetic vs. real datasets using statistical and privacy metrics.
    """
    def __init__(self, real_path: str, synth_path: str):
        self.real = pd.read_csv(real_path)
        self.synth = pd.read_csv(synth_path)
        self.cols = list(self.real.columns)
    def stat_metrics(self) -> Dict[str, Any]:
        dist_mses = {}
        for col in self.cols:
            if self.real[col].dtype in [np.float32, np.float64, np.int64, np.int32]:
                real_vals = np.asarray(self.real[col].fillna(0))
                synth_vals = np.asarray(self.synth[col].fillna(0))
                mse = np.mean((real_vals - synth_vals) ** 2)
                dist_mses[col] = mse
        return {'feature_mse': dist_mses}
    def mutual_information(self) -> Dict[str, Any]:
        mi_vals = {}
        for col in self.cols:
            if self.real[col].dtype in [np.int64, np.int32]:
                mi = mutual_info_score(self.real[col], self.synth[col])
                mi_vals[col] = mi
        return {'mutual_info': mi_vals}
    def silhouette(self) -> float:
        arr = pd.concat([self.real, self.synth], ignore_index=True).to_numpy()
        labels = np.array([0] * len(self.real) + [1] * len(self.synth))
        score = silhouette_score(arr, labels)
        return float(score)
    def membership_inference_risk(self, n_probe: int = 10) -> float:
        np.random.seed(17)
        probes = self.real.sample(min(n_probe, len(self.real)))
        synth_flat = self.synth.apply(tuple, axis=1).values
        matches = 0
        for _, row in probes.iterrows():
            if tuple(row.values) in synth_flat:
                matches += 1
        return matches / n_probe
    def all_checks(self) -> Dict[str, Any]:
        stats = self.stat_metrics()
        mi = self.mutual_information()
        sil = self.silhouette()
        mirisk = self.membership_inference_risk()
        return {'stat_metrics': stats, 'mutual_info': mi, 'silhouette_score': sil, 'membership_inf_risk': mirisk}

def minimum_viable_quality_checks(
    real_path: str,
    synth_path: str,
    thresholds: Dict[str, float]
) -> Dict[str, Any]:
    """
    Run minimum viable utility and privacy checks for synthetic tabular healthcare data.
    thresholds: {'feature_mse': float, 'silhouette': float, 'mirisk': float}
    """
    validator = PrivacyUtilityValidator(real_path, synth_path)
    results = validator.all_checks()
    feature_mse = np.mean(list(results['stat_metrics']['feature_mse'].values()))
    silhouette = results['silhouette_score']
    mirisk = results['membership_inf_risk']
    passed = (feature_mse < thresholds['feature_mse']) and (silhouette > thresholds['silhouette']) and (mirisk < thresholds['mirisk'])
    return {
        'feature_mse': feature_mse,
        'silhouette': silhouette,
        'membership_risk': mirisk,
        'passed': passed,
        'details': results
    }

def design_pipeline_documentation(
    pipeline_dir: str,
    data_path: str,
    synth_path: str,
    real_config: Dict[str, Any],
    privacy_cfg: Dict[str, Any]
) -> None:
    """
    Generate a pipeline documentation JSON file capturing the synthetic data pipeline workflow, configs, and outputs.
    """
    pipeline_doc = {
        'data_ingestion': {
            'desc': 'Load and normalize healthcare EHR and clinical data, de-identification by downstream pipeline.'
        },
        'model_train': {
            'desc': 'Train tabular VAE under differential privacy with Opacus.',
            'config': real_config
        },
        'privacy': {
            'desc': 'Differential Privacy enabled (Opacus).',
            'config': privacy_cfg
        },
        'validation': {
            'desc': 'Run statistical and privacy utility checks against real data.',
            'metrics': ['feature-wise MSE', 'mutual information', 'silhouette score', 'membership inference risk']
        },
        'quality_checks': {
            'desc': 'Feature MSE < threshold, silhouette > threshold, membership risk < threshold, passes if all true.'
        },
        'output': {
            'location': synth_path
        }
    }
    out_path = os.path.join(pipeline_dir, 'healthcare_data_gen_pipeline_doc.json')
    with open(out_path, 'w') as f:
        json.dump(pipeline_doc, f, indent=2)
