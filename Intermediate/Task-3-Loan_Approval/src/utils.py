"""
Utility helpers: robust project paths, file loading, and small shared
functions used across preprocessing, training, evaluation and prediction.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

# --------------------------------------------------------------------------- #
# Robust project paths (works regardless of current working directory)
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

DATA_PATH = DATA_DIR / "loan_prediction.csv"
MODEL_PATH = MODELS_DIR / "loan_model.pkl"
PIPELINE_PATH = MODELS_DIR / "preprocessing_pipeline.pkl"
METADATA_PATH = MODELS_DIR / "model_metadata.json"

TARGET_COLUMN = "Loan_Status"
ID_COLUMN = "Loan_ID"


def ensure_dirs() -> None:
    """Create output directories if they do not exist."""
    for d in (DATA_DIR, MODELS_DIR, REPORTS_DIR):
        d.mkdir(parents=True, exist_ok=True)


def load_dataset(path: Path | str = DATA_PATH) -> pd.DataFrame:
    """
    Load the loan dataset from CSV.

    Raises a clear error if the file is missing.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at '{path}'. "
            f"Place 'loan_prediction.csv' inside the 'data/' folder."
        )
    return pd.read_csv(path)


def save_json(data: dict, path: Path | str = METADATA_PATH) -> None:
    """Save a dictionary as a nicely formatted JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, default=str)


def load_json(path: Path | str = METADATA_PATH) -> dict:
    """Load a JSON file into a dictionary."""
    path = Path(path)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_model(path: Path | str = MODEL_PATH):
    """Load a saved model (full pipeline) using joblib."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Model not found at '{path}'. Train the model first:\n"
            f"    python src/train_model.py"
        )
    return joblib.load(path)


def save_model(model, path: Path | str = MODEL_PATH) -> None:
    """Persist a model to disk using joblib."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)