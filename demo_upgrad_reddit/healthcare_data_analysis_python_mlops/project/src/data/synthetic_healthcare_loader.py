import pandas as pd
from typing import Any

def load_healthcare_dataset() -> pd.DataFrame:
    """
    Loads a synthetic healthcare dataset for model training and evaluation.
    """
    data = pd.read_csv("data/healthcare_synthetic.csv")
    return data