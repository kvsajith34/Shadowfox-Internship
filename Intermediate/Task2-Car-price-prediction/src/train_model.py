"""
Model Training Module
=====================
Trains multiple regression models, performs hyperparameter tuning
on Random Forest, and saves the best model pipeline.

Usage (run from project root):
    python -m src.train_model
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

from src.data_preprocessing import preprocess_pipeline, create_preprocessor, get_data_path

# Project root directory (one level up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "outputs", "reports")


# -------------------------------------------------------
# 1. Train Multiple Models
# -------------------------------------------------------
def train_multiple_models(X_train, X_test, y_train, y_test, preprocessor):
    """Train and compare multiple regression models.

    Args:
        X_train, X_test: Feature splits.
        y_train, y_test: Target splits.
        preprocessor: ColumnTransformer for preprocessing.

    Returns:
        Dictionary of model results.
    """
    models = {
        'Linear Regression': LinearRegression(),
        'Decision Tree': DecisionTreeRegressor(random_state=42),
        'Random Forest': RandomForestRegressor(random_state=42, n_estimators=100),
        'Gradient Boosting': GradientBoostingRegressor(random_state=42, n_estimators=100)
    }

    results = {}

    print("\n" + "=" * 60)
    print("TRAINING MULTIPLE MODELS")
    print("=" * 60)

    for name, model in models.items():
        print(f"\n🔧 Training {name}...")

        # Create full pipeline with preprocessing and model
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('model', model)
        ])

        # Train
        pipeline.fit(X_train, y_train)

        # Predict
        y_pred = pipeline.predict(X_test)

        # Evaluate
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)

        results[name] = {
            'MAE': round(mae, 4),
            'MSE': round(mse, 4),
            'RMSE': round(rmse, 4),
            'R2_Score': round(r2, 4),
            'Pipeline': pipeline
        }

        print(f"   MAE: {mae:.4f}  |  MSE: {mse:.4f}  |  RMSE: {rmse:.4f}  |  R²: {r2:.4f}")

    return results


# -------------------------------------------------------
# 2. Hyperparameter Tuning — Random Forest
# -------------------------------------------------------
def tune_random_forest(X_train, y_train, preprocessor):
    """Perform RandomizedSearchCV on Random Forest Regressor.

    Args:
        X_train: Training features.
        y_train: Training target.
        preprocessor: ColumnTransformer for preprocessing.

    Returns:
        Best fitted pipeline.
    """
    print("\n" + "=" * 60)
    print("HYPERPARAMETER TUNING — RANDOM FOREST")
    print("=" * 60)

    # Define parameter grid
    param_distributions = {
        'model__n_estimators': [100, 200, 300, 500],
        'model__max_depth': [5, 10, 15, 20, None],
        'model__min_samples_split': [2, 5, 10],
        'model__min_samples_leaf': [1, 2, 4],
        'model__max_features': ['sqrt', 'log2', 1.0]
    }

    # Create pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', RandomForestRegressor(random_state=42))
    ])

    # RandomizedSearchCV
    random_search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=param_distributions,
        n_iter=50,
        cv=5,
        scoring='r2',
        n_jobs=-1,
        random_state=42,
        verbose=1
    )

    print("🔍 Starting RandomizedSearchCV (50 iterations, 5-fold CV)...")
    random_search.fit(X_train, y_train)

    # Print best parameters
    print(f"\n🏆 Best Parameters Found:")
    for param, value in random_search.best_params_.items():
        param_name = param.replace('model__', '')
        print(f"   {param_name}: {value}")
    print(f"   Best CV R² Score: {random_search.best_score_:.4f}")

    return random_search.best_estimator_


# -------------------------------------------------------
# 3. Save Model
# -------------------------------------------------------
def save_model(pipeline, filepath: str = None) -> None:
    """Save the trained pipeline using joblib.

    Args:
        pipeline: The fitted sklearn Pipeline.
        filepath: Path to save the model. If None, uses default path.
    """
    if filepath is None:
        filepath = os.path.join(MODELS_DIR, "car_price_model.pkl")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    joblib.dump(pipeline, filepath)
    print(f"✅ Model saved to: {filepath}")


# -------------------------------------------------------
# 4. Save Results Table
# -------------------------------------------------------
def save_results_table(results, filepath: str = None) -> None:
    """Save model comparison results to CSV.

    Args:
        results: Dictionary of model results.
        filepath: Path to save the CSV. If None, uses default path.
    """
    if filepath is None:
        filepath = os.path.join(REPORTS_DIR, "model_evaluation.csv")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    comparison_data = []
    for name, metrics in results.items():
        comparison_data.append({
            'Model': name,
            'MAE': metrics['MAE'],
            'MSE': metrics['MSE'],
            'RMSE': metrics['RMSE'],
            'R2_Score': metrics['R2_Score']
        })

    df_comparison = pd.DataFrame(comparison_data)
    df_comparison = df_comparison.sort_values('R2_Score', ascending=False).reset_index(drop=True)
    df_comparison.to_csv(filepath, index=False)

    print(f"✅ Model comparison saved to: {filepath}")
    print("\n📊 Model Comparison Table:")
    print(df_comparison.to_string(index=False))


# -------------------------------------------------------
# Main
# -------------------------------------------------------
def main():
    print("\n" + "=" * 60)
    print("CAR PRICE PREDICTION — MODEL TRAINING")
    print("=" * 60)

    # Create output directories
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # Preprocess data
    X, y, preprocessor = preprocess_pipeline()
    if X is None:
        print("❌ Error: Could not preprocess data. Exiting.")
        return

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"\n📊 Train set: {X_train.shape[0]} samples")
    print(f"📊 Test set:  {X_test.shape[0]} samples")

    # Train multiple models
    results = train_multiple_models(X_train, X_test, y_train, y_test, preprocessor)

    # Save comparison table
    save_results_table(results)

    # Find best model from initial training
    best_name = max(results, key=lambda k: results[k]['R2_Score'])
    print(f"\n🏆 Best Initial Model: {best_name} (R² = {results[best_name]['R2_Score']})")

    # Hyperparameter tuning on Random Forest
    best_pipeline = tune_random_forest(X_train, y_train, preprocessor)

    # Evaluate tuned model
    y_pred_tuned = best_pipeline.predict(X_test)
    mae_tuned = mean_absolute_error(y_test, y_pred_tuned)
    rmse_tuned = np.sqrt(mean_squared_error(y_test, y_pred_tuned))
    r2_tuned = r2_score(y_test, y_pred_tuned)

    print(f"\n🏆 Tuned Random Forest Performance:")
    print(f"   MAE:  {mae_tuned:.4f}")
    print(f"   RMSE: {rmse_tuned:.4f}")
    print(f"   R²:   {r2_tuned:.4f}")

    # Save the best pipeline
    save_model(best_pipeline)

    print("\n✅ Model training complete!")
    print("   Run 'python -m src.evaluate_model' for detailed evaluation.")
    print("   Run 'streamlit run streamlit_app.py' to use the web app.")


if __name__ == "__main__":
    main()
