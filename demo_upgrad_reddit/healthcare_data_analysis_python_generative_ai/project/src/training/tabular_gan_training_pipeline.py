import os
import logging
import json
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from typing import Tuple, Dict, Any, List  # Fixed: Ensure List is imported as required
# Project-specific imports (assumed present)
from src.utils.dp_metrics import compute_epsilon_delta, membership_inference_attack
from src.utils.model_versioning import save_model, load_latest_model, version_dataset, log_run_result
from src.evaluation.tabular_utility import evaluate_downstream_classifier


def preprocess_healthcare_data(
    data_path: str, deid_cols: List[str], cat_cols: List[str], num_cols: List[str], output_path: str
) -> Tuple[pd.DataFrame, Dict[str, Any], MinMaxScaler, Dict[str, LabelEncoder]]:
    """
    Preprocess tabular healthcare data with deidentification and normalization.
    Args:
        data_path: Path to CSV file with raw tabular healthcare data.
        deid_cols: List of columns to drop (PII/PHI).
        cat_cols: List of categorical column names.
        num_cols: List of numerical column names.
        output_path: Where to save the preprocessed data.
    Returns:
        Tuple of (preprocessed df, column metadata, scaler, label encoders for cat cols).
    """
    try:
        df = pd.read_csv(data_path)
    except Exception as e:
        raise RuntimeError(f'Error reading input data: {e}')
    df = df.drop(columns=deid_cols)
    cat_encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        cat_encoders[col] = le
    scaler = MinMaxScaler()
    df[num_cols] = scaler.fit_transform(df[num_cols])
    col_metadata = {"cat_cols": cat_cols, "num_cols": num_cols}
    # Save preprocessed data
    try:
        df.to_csv(output_path, index=False)
    except Exception as e:
        raise RuntimeError(f'Error saving preprocessed data: {e}')
    return df, col_metadata, scaler, cat_encoders


class Generator(nn.Module):
    """
    Generator neural network for tabular GAN.
    """
    def __init__(self, noise_dim: int, data_dim: int, hidden_dim: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(noise_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, data_dim),
            nn.Sigmoid()
        )
    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.net(z)


class Discriminator(nn.Module):
    """
    Discriminator neural network for tabular GAN.
    """
    def __init__(self, data_dim: int, hidden_dim: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(data_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def train_gan(
    data: np.ndarray,
    noise_dim: int,
    epochs: int,
    batch_size: int,
    output_dir: str,
    model_name: str,
    logging_path: str,
    lr: float = 0.0002,
    device: str = None
) -> Tuple[Generator, Discriminator]:
    """
    Train a GAN on tabular data using PyTorch.
    Args:
        data: Numpy array of normalized tabular data.
        noise_dim: Dimension of noise input.
        epochs: Number of training epochs.
        batch_size: Batch size.
        output_dir: Model output directory.
        model_name: Name prefix for saved models.
        logging_path: Log file path.
        lr: Learning rate.
        device: Device string, autodetect if None.
    Returns:
        (Trained Generator, Discriminator)
    """
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    os.makedirs(output_dir, exist_ok=True)
    logging.basicConfig(filename=logging_path, filemode='w', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    data_tensor = torch.tensor(data, dtype=torch.float32).to(device)
    data_dim = data.shape[1]
    generator = Generator(noise_dim, data_dim).to(device)
    discriminator = Discriminator(data_dim).to(device)
    g_optimizer = optim.Adam(generator.parameters(), lr=lr)
    d_optimizer = optim.Adam(discriminator.parameters(), lr=lr)
    criterion = nn.BCELoss()
    steps_per_epoch = max(1, data.shape[0] // batch_size)
    for epoch in range(epochs):
        perm = torch.randperm(data.shape[0])
        for i in range(steps_per_epoch):
            idx = perm[i*batch_size:(i+1)*batch_size]
            real_data = data_tensor[idx]
            batch_size_actual = real_data.shape[0]
            real_labels = torch.ones((batch_size_actual, 1), device=device)
            fake_labels = torch.zeros((batch_size_actual, 1), device=device)
            z = torch.randn((batch_size_actual, noise_dim), device=device)
            fake_data = generator(z)
            d_real = discriminator(real_data)
            d_fake = discriminator(fake_data.detach())
            d_loss = criterion(d_real, real_labels) + criterion(d_fake, fake_labels)
            d_optimizer.zero_grad()
            d_loss.backward()
            d_optimizer.step()
            z = torch.randn((batch_size_actual, noise_dim), device=device)
            fake_data = generator(z)
            d_fake = discriminator(fake_data)
            g_loss = criterion(d_fake, real_labels)
            g_optimizer.zero_grad()
            g_loss.backward()
            g_optimizer.step()
        logging.info(f'Epoch {epoch+1}/{epochs} | D_loss={d_loss.item():.4f} | G_loss={g_loss.item():.4f}')
        # Save checkpoint each epoch (best practice: saves resilience to interruptions)
        save_model(generator, os.path.join(output_dir, f'{model_name}_generator_epoch{epoch+1}.pt'))
        save_model(discriminator, os.path.join(output_dir, f'{model_name}_discriminator_epoch{epoch+1}.pt'))
    save_model(generator, os.path.join(output_dir, f'{model_name}_generator_final.pt'))
    save_model(discriminator, os.path.join(output_dir, f'{model_name}_discriminator_final.pt'))
    return generator, discriminator


def generate_synthetic_data(
    generator: Generator, num_samples: int, noise_dim: int, device: str = None
) -> np.ndarray:
    """
    Use trained generator to sample synthetic tabular data.
    Args:
        generator: Trained Generator model.
        num_samples: Number of records to generate.
        noise_dim: Dimension of generator noise input.
        device: PyTorch device string.
    Returns:
        np.ndarray of synthetic samples.
    """
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    generator.eval()
    with torch.no_grad():
        z = torch.randn((num_samples, noise_dim), device=device)
        synth = generator(z).cpu().numpy()
    return synth


def pipeline(
    raw_data_path: str,
    output_dir: str,
    deid_cols: List[str],
    cat_cols: List[str],
    num_cols: List[str],
    noise_dim: int = 24,
    batch_size: int = 256,
    epochs: int = 100,
    downstream_target_col: str = None,
    dp_delta: float = 1e-5,
    baseline_accuracy_drop: float = 0.1
) -> Dict[str, Any]:
    """
    Complete workflow for GAN-based tabular healthcare data generation and evaluation.
    Args:
        raw_data_path: Path to raw healthcare CSV.
        output_dir: Workflow output directory.
        deid_cols: List of columns (PII/PHI) to remove.
        cat_cols: List of categorical features.
        num_cols: List of continuous features.
        noise_dim: Dimension of GAN noise.
        batch_size: GAN mini-batch size.
        epochs: GAN training epochs.
        downstream_target_col: Optional, for downstream utility classifier.
        dp_delta: For differential privacy epsilon estimation.
        baseline_accuracy_drop: Acceptable accuracy drop as downstream utility threshold.
    Returns:
        Dict with metrics, model/dataset versioning info, logs.
    """
    os.makedirs(output_dir, exist_ok=True)
    preprocessed_path = os.path.join(output_dir, 'preprocessed.csv')
    df, meta, scaler, cat_encoders = preprocess_healthcare_data(raw_data_path, deid_cols, cat_cols, num_cols, preprocessed_path)
    if downstream_target_col and downstream_target_col in df.columns:
        X = df.drop(columns=[downstream_target_col])
        y = df[downstream_target_col]
    else:
        X = df
        y = None
    data_np = X.to_numpy().astype(np.float32)
    generator, discriminator = train_gan(
        data=data_np,
        noise_dim=noise_dim,
        epochs=epochs,
        batch_size=batch_size,
        output_dir=output_dir,
        model_name='tabgan',
        logging_path=os.path.join(output_dir, 'training.log')
    )
    synth_np = generate_synthetic_data(generator, num_samples=data_np.shape[0], noise_dim=noise_dim)
    synth_df = pd.DataFrame(synth_np, columns=X.columns)
    synth_df[num_cols] = scaler.inverse_transform(synth_df[num_cols])
    # Reverse label encoding for categorical columns
    for col in cat_cols:
        inv = np.round(synth_df[col]).clip(0, len(cat_encoders[col].classes_)-1).astype(int)
        synth_df[col] = cat_encoders[col].inverse_transform(inv)
    synth_data_path = os.path.join(output_dir, 'synthetic.csv')
    try:
        synth_df.to_csv(synth_data_path, index=False)
    except Exception as e:
        raise RuntimeError(f'Error saving synthetic data: {e}')
    # Version real/preprocessed dataset and model
    dataset_version = version_dataset(preprocessed_path)
    model_version = save_model(generator, os.path.join(output_dir, 'tabgan_generator_final.pt'))
    logging.info(f'Dataset version: {dataset_version}, Model version: {model_version}')
    # Privacy risk metrics
    dp_epsilon = compute_epsilon_delta(real_df=df, synth_df=synth_df, delta=dp_delta)
    privacy_risk = membership_inference_attack(real_df=df, synth_df=synth_df)
    logging.info(f'DP epsilon (lower=stronger privacy): {dp_epsilon:.2f}, MIA risk: {privacy_risk}')
    if downstream_target_col and y is not None:
        real_train_X, real_test_X, real_train_y, real_test_y = train_test_split(X, y, test_size=0.3, random_state=42)
        # For downstream utility, we'll use same labels for synth as real (cf. context requirements)
        synth_train_X, synth_train_y = synth_df, y[:synth_df.shape[0]]
        real_acc, synth_acc = evaluate_downstream_classifier(real_train_X, real_train_y, real_test_X, real_test_y, synth_train_X, synth_train_y)
        accuracy_drop = real_acc - synth_acc
        utility_valid = accuracy_drop < baseline_accuracy_drop
    else:
        real_acc, synth_acc, accuracy_drop, utility_valid = None, None, None, None
    run_report = {
        'dataset_version': dataset_version,
        'model_version': model_version,
        'dp_epsilon': dp_epsilon,
        'mia_risk': privacy_risk,
        'real_classifier_accuracy': real_acc,
        'synthetic_classifier_accuracy': synth_acc,
        'accuracy_drop': accuracy_drop,
        'utility_valid': utility_valid
    }
    # Save run report
    try:
        log_run_result(os.path.join(output_dir, 'run_report.json'), run_report)
    except Exception as e:
        logging.error(f'Unable to save run report: {e}')
    return run_report
