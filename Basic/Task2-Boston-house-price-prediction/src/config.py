"""Configuration file for Boston House Price Prediction project.

Stores all important paths, column names, and constants.
Uses pathlib for cross-platform compatibility.
"""

from pathlib import Path

# Base directory (project root - one level up from src/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Data path
DATA_PATH = BASE_DIR / "data" / "HousingData.csv"

# Model directory and path
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "best_model.pkl"

# Output directories
OUTPUT_DIR = BASE_DIR / "outputs"
PLOTS_DIR = OUTPUT_DIR / "plots"

# Metrics paths
METRICS_PATH = OUTPUT_DIR / "metrics.json"
MODEL_COMPARISON_PATH = OUTPUT_DIR / "model_comparison.csv"

# Feature columns (all columns except MEDV)
FEATURE_COLUMNS = [
    "CRIM", "ZN", "INDUS", "CHAS", "NOX", "RM",
    "AGE", "DIS", "RAD", "TAX", "PTRATIO", "B", "LSTAT"
]

# Target column
TARGET_COLUMN = "MEDV"

# Columns known to have missing values
MISSING_COLUMNS = ["CRIM", "ZN", "INDUS", "CHAS", "AGE", "LSTAT"]

# Train-test split parameters
TEST_SIZE = 0.2
RANDOM_STATE = 42

# Cross-validation folds
CV_FOLDS = 5


def ensure_directories():
    """Create all required directories if they do not exist."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    print("✅ All required directories verified/created.")
