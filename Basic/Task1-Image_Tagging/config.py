"""
config.py
---------
Central configuration file for the Image Tagging project.

>>> HYPERPARAMETER TUNING <<<
Change values here to tune the model. No need to edit other files.
Keep batch size at 32 or 64 for your laptop (i5, 16GB RAM, CPU).
"""

import os

# ---------------------------------------------------------------------
# PROJECT PATHS (auto-detected — do not change unless you move folders)
# ---------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")
PLOTS_DIR = os.path.join(OUTPUTS_DIR, "plots")
REPORTS_DIR = os.path.join(OUTPUTS_DIR, "reports")
SAMPLE_IMAGES_DIR = os.path.join(PROJECT_ROOT, "sample_images")

# Best model save path
MODEL_PATH = os.path.join(MODELS_DIR, "best_cnn_model.keras")

# ---------------------------------------------------------------------
# DATASET CONFIG
# ---------------------------------------------------------------------
IMG_HEIGHT = 32          # CIFAR-10 native size
IMG_WIDTH = 32
IMG_CHANNELS = 3
NUM_CLASSES = 10

# CIFAR-10 class names (fixed order). "automobile" = car category.
CLASS_NAMES = [
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck"
]

# Validation split taken from the training data
VALIDATION_SPLIT = 0.1   # 10% of train -> validation

# ---------------------------------------------------------------------
# >>> HYPERPARAMETERS YOU CAN TUNE <<<
# ---------------------------------------------------------------------
BATCH_SIZE = 64          # Try 32 or 64. Lower = less RAM.
EPOCHS = 60              # EarlyStopping will usually stop earlier.
LEARNING_RATE = 0.001    # Adam default. Try 0.0005 or 0.0001.
DROPOUT_RATE = 0.4       # 0.3 - 0.5 recommended.
BASE_FILTERS = 32        # First conv block filters (32 or 64).
OPTIMIZER = "adam"       # "adam", "sgd", or "rmsprop".

# ---------------------------------------------------------------------
# CALLBACK CONFIG
# ---------------------------------------------------------------------
EARLY_STOPPING_PATIENCE = 12
REDUCE_LR_PATIENCE = 4
REDUCE_LR_FACTOR = 0.5
MIN_LR = 1e-6

# Reproducibility
RANDOM_SEED = 42


def ensure_dirs():
    """Create all required output directories if they don't exist."""
    for d in [MODELS_DIR, OUTPUTS_DIR, PLOTS_DIR, REPORTS_DIR, SAMPLE_IMAGES_DIR]:
        os.makedirs(d, exist_ok=True)