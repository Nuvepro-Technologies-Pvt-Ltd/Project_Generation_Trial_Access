import numpy as np
import pandas as pd
from sklearn.metrics import pairwise_distances

def compute_privacy_score(real: pd.DataFrame, synth: np.ndarray) -> float:
    real = real.values if hasattr(real, "values") else real
    synth = synth if isinstance(synth, np.ndarray) else synth.values
    nearest_dist = pairwise_distances(synth, real).min(axis=1)
    score = float(nearest_dist.mean())
    return score

def compute_fidelity_score(real: pd.DataFrame, synth: np.ndarray) -> float:
    real = real.values if hasattr(real, "values") else real
    synth = synth if isinstance(synth, np.ndarray) else synth.values
    real_mean = real.mean(axis=0)
    synth_mean = synth.mean(axis=0)
    diff = np.abs(real_mean - synth_mean)
    fidelity = float(1.0 / (1.0 + diff.mean()))
    return fidelity