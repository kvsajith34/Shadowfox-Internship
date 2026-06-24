"""Model evaluation and visualization module for Boston House Price Prediction.

Loads the saved best model, evaluates it on test data,
and generates diagnostic plots.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root to Python path for reliable imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.config import (
    MODEL_PATH, PLOTS_DIR, METRICS_PATH, FEATURE_COLUMNS
)
from src.data_preprocessing import (
    load_data, split_features_target, train_test_split_data
)


def load_model():
    """Load the saved best model pipeline.

    Returns:
        Pipeline: The saved sklearn Pipeline object.

    Raises:
        FileNotFoundError: If best_model.pkl is not found.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"\n❌ Model not found at: {MODEL_PATH}\n"
            "Please train the model first by running:\n"
            "   python -m src.train_model\n"
            "or: python src/train_model.py"
        )
    model = joblib.load(MODEL_PATH)
    print(f"✅ Model loaded from: {MODEL_PATH}")
    return model


def plot_actual_vs_predicted(model, X_test, y_test):
    """Generate and save the actual vs predicted scatter plot.

    Args:
        model: Trained model pipeline.
        X_test: Test features.
        y_test: Actual target values.
    """
    y_pred = model.predict(X_test)

    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, y_pred, alpha=0.6, color="#4F46E5",
                edgecolors="white", linewidth=0.5, s=60)
    plt.plot([y_test.min(), y_test.max()],
             [y_test.min(), y_test.max()],
             "r--", linewidth=2, label="Perfect Prediction")
    plt.xlabel("Actual Prices (MEDV in $1000's)", fontsize=12)
    plt.ylabel("Predicted Prices (MEDV in $1000's)", fontsize=12)
    plt.title("Actual vs Predicted House Prices", fontsize=14, fontweight="bold")
    plt.legend(fontsize=10)
    plt.tight_layout()

    plot_path = PLOTS_DIR / "actual_vs_predicted.png"
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ Plot saved: {plot_path}")


def plot_residuals(model, X_test, y_test):
    """Generate and save the residuals plot.

    Args:
        model: Trained model pipeline.
        X_test: Test features.
        y_test: Actual target values.
    """
    y_pred = model.predict(X_test)
    residuals = y_test - y_pred

    plt.figure(figsize=(8, 6))
    plt.scatter(y_pred, residuals, alpha=0.6, color="#DC2626",
                edgecolors="white", linewidth=0.5, s=60)
    plt.axhline(y=0, color="black", linestyle="--", linewidth=2)
    plt.xlabel("Predicted Prices (MEDV in $1000's)", fontsize=12)
    plt.ylabel("Residuals (Actual - Predicted)", fontsize=12)
    plt.title("Residuals Plot", fontsize=14, fontweight="bold")
    plt.tight_layout()

    plot_path = PLOTS_DIR / "residuals_plot.png"
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ Plot saved: {plot_path}")


def plot_feature_importance(model):
    """Generate and save the feature importance plot.

    If the best model supports feature_importances_ (tree-based),
    create a bar chart. If it supports coef_ (linear), use absolute
    coefficients. Otherwise, display a text message.

    Args:
        model: Trained model pipeline.
    """
    # Get the regressor from the pipeline
    regressor = model.named_steps["regressor"]

    if hasattr(regressor, "feature_importances_"):
        importances = regressor.feature_importances_
        title = "Feature Importance (Tree-based)"
    elif hasattr(regressor, "coef_"):
        importances = np.abs(regressor.coef_)
        title = "Feature Importance (|Coefficients|)"
    else:
        print("⚠️  Feature importance is not available for this model type.")
        print(f"   Model: {type(regressor).__name__} does not support feature importance.")
        return

    plt.figure(figsize=(10, 6))
    indices = np.argsort(importances)[::-1]
    sorted_features = [FEATURE_COLUMNS[i] for i in indices]
    sorted_importances = importances[indices]

    # Create color gradient
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(sorted_features)))

    plt.barh(range(len(sorted_importances)),
             sorted_importances[::-1],
             color=colors[::-1], edgecolor="white", linewidth=0.5)
    plt.yticks(range(len(sorted_features)),
               sorted_features[::-1], fontsize=10)
    plt.xlabel("Importance", fontsize=12)
    plt.title(title, fontsize=14, fontweight="bold")
    plt.tight_layout()

    plot_path = PLOTS_DIR / "feature_importance.png"
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ Plot saved: {plot_path}")


def evaluate():
    """Main evaluation function — loads model and generates all plots."""
    # Ensure output directories exist
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    # Print header
    print("\n" + "=" * 65)
    print("   MODEL EVALUATION & VISUALIZATION")
    print("=" * 65 + "\n")

    # Load the saved model
    print("📦 Loading saved model...")
    model = load_model()

    # Reload data and recreate the same split
    print("\n📂 Loading dataset...")
    data = load_data()

    print("\n✂️  Recreating train-test split...")
    X, y = split_features_target(data)
    X_train, X_test, y_train, y_test = train_test_split_data(X, y)

    # Print model evaluation metrics
    print("\n📊 Evaluation Results:")
    if METRICS_PATH.exists():
        with open(METRICS_PATH, "r") as f:
            metrics = json.load(f)
        print(f"   Best Model: {metrics['best_model']}")
        print(f"   R2 Score:   {metrics['best_r2']}")
        print(f"   RMSE:       {metrics['best_rmse']}")
        print(f"   MAE:        {metrics['best_mae']}")
        print(f"   MSE:        {metrics['best_mse']}")
        print(f"   CV R² Mean: {metrics['best_cv_r2_mean']}")
    else:
        # Calculate metrics if file doesn't exist
        y_pred = model.predict(X_test)
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        print(f"   R2 Score:  {r2:.4f}")
        print(f"   RMSE:      {rmse:.4f}")
        print(f"   MAE:       {mae:.4f}")
        print(f"   MSE:       {mse:.4f}")

    # Generate all plots
    print("\n📈 Generating plots...")
    plot_actual_vs_predicted(model, X_test, y_test)
    plot_residuals(model, X_test, y_test)
    plot_feature_importance(model)

    print("\n" + "=" * 65)
    print("   ✅ All evaluation plots saved successfully!")
    print("=" * 65 + "\n")


# Allow running with: python src/evaluate_model.py
if __name__ == "__main__":
    evaluate()
