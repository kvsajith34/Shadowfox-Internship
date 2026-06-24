"""
Model Evaluation Module
=======================
Evaluates the saved model and generates evaluation plots.

Usage (run from project root):
    python -m src.evaluate_model
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.data_preprocessing import preprocess_pipeline

# Project root directory (one level up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PLOTS_DIR = os.path.join(PROJECT_ROOT, "outputs", "plots")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 100


# -------------------------------------------------------
# 1. Load Model
# -------------------------------------------------------
def load_model(filepath: str = None):
    """Load the saved model pipeline.

    Args:
        filepath: Path to the saved model. If None, uses default path.

    Returns:
        Loaded pipeline or None if not found.
    """
    if filepath is None:
        filepath = os.path.join(MODELS_DIR, "car_price_model.pkl")

    try:
        model = joblib.load(filepath)
        print(f"✅ Model loaded from: {filepath}")
        return model
    except FileNotFoundError:
        print(f"❌ Model file not found: {filepath}")
        print("   Run 'python -m src.train_model' first.")
        return None
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None


# -------------------------------------------------------
# 2. Actual vs Predicted Plot
# -------------------------------------------------------
def plot_actual_vs_predicted(y_test, y_pred) -> None:
    """Scatter plot of actual vs predicted values."""
    fig, ax = plt.subplots(figsize=(8, 8))

    ax.scatter(y_test, y_pred, alpha=0.6, color='#4F46E5', s=60, edgecolor='white', linewidth=0.5)

    # Perfect prediction line
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')

    ax.set_title('Actual vs Predicted Selling Price', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Actual Price (Lakhs)', fontsize=12)
    ax.set_ylabel('Predicted Price (Lakhs)', fontsize=12)
    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "09_actual_vs_predicted.png"), bbox_inches='tight')
    plt.close()
    print("✅ Saved: 09_actual_vs_predicted.png")


# -------------------------------------------------------
# 3. Residual Plot
# -------------------------------------------------------
def plot_residuals(y_test, y_pred) -> None:
    """Plot residuals vs predicted values and residual distribution."""
    residuals = y_test - y_pred

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Residual scatter plot
    axes[0].scatter(y_pred, residuals, alpha=0.6, color='#4F46E5', s=60)
    axes[0].axhline(y=0, color='red', linestyle='--', linewidth=2)
    axes[0].set_title('Residual Plot', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Predicted Price (Lakhs)', fontsize=11)
    axes[0].set_ylabel('Residual (Actual - Predicted)', fontsize=11)

    # Residual distribution
    sns.histplot(residuals, bins=20, kde=True, color='#4F46E5', ax=axes[1])
    axes[1].set_title('Residual Distribution', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Residual Value', fontsize=11)

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "10_residual_plot.png"), bbox_inches='tight')
    plt.close()
    print("✅ Saved: 10_residual_plot.png")


# -------------------------------------------------------
# 4. Feature Importance Plot
# -------------------------------------------------------
def plot_feature_importance(model_pipeline) -> None:
    """Plot feature importance from the Random Forest model."""
    try:
        model = model_pipeline.named_steps['model']
        preprocessor = model_pipeline.named_steps['preprocessor']

        # Get feature names
        numerical_features = ['Present_Price', 'Kms_Driven', 'Owner', 'Car_Age']
        categorical_features = ['Fuel_Type', 'Seller_Type', 'Transmission']

        # Get one-hot encoded feature names
        cat_encoder = preprocessor.named_transformers_['cat'].named_steps['encoder']
        cat_feature_names = cat_encoder.get_feature_names_out(categorical_features).tolist()

        all_features = numerical_features + cat_feature_names
        importances = model.feature_importances_

        # Sort by importance
        feature_importance = sorted(zip(all_features, importances), key=lambda x: x[1], reverse=True)
        features, values = zip(*feature_importance)

        fig, ax = plt.subplots(figsize=(10, 8))
        colors = ['#4F46E5' if i < 3 else '#94A3B8' for i in range(len(features))]
        ax.barh(range(len(features)), values, color=colors)
        ax.set_yticks(range(len(features)))
        ax.set_yticklabels(features, fontsize=11)
        ax.set_xlabel('Importance', fontsize=12)
        ax.set_title('Feature Importance (Random Forest)', fontsize=16, fontweight='bold', pad=15)
        ax.invert_yaxis()

        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, "11_feature_importance.png"), bbox_inches='tight')
        plt.close()
        print("✅ Saved: 11_feature_importance.png")

    except Exception as e:
        print(f"⚠️  Could not plot feature importance: {e}")


# -------------------------------------------------------
# Main Evaluation
# -------------------------------------------------------
def evaluate():
    """Run complete model evaluation."""
    print("\n" + "=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    # Create output directory
    os.makedirs(PLOTS_DIR, exist_ok=True)

    # Preprocess data (same split as training)
    X, y, _ = preprocess_pipeline()
    if X is None:
        return

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Load saved model
    model = load_model()
    if model is None:
        return

    # Predict
    y_pred = model.predict(X_test)

    # Calculate metrics
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    print(f"\n📊 Final Model Performance:")
    print(f"   MAE:  {mae:.4f}")
    print(f"   MSE:  {mse:.4f}")
    print(f"   RMSE: {rmse:.4f}")
    print(f"   R²:   {r2:.4f}")

    # Generate evaluation plots
    print("\n📈 Generating Evaluation Plots...")
    print("-" * 40)
    plot_actual_vs_predicted(y_test, y_pred)
    plot_residuals(y_test, y_pred)
    plot_feature_importance(model)

    print("\n✅ Evaluation complete!")


if __name__ == "__main__":
    evaluate()
