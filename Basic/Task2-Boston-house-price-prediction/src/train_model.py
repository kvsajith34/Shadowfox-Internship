"""Model training module for Boston House Price Prediction.

Trains multiple regression models, evaluates them, compares performance,
and saves the best model pipeline.
"""

import json
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Add project root to Python path for reliable imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.config import (
    MODEL_PATH, OUTPUT_DIR, METRICS_PATH,
    MODEL_COMPARISON_PATH, RANDOM_STATE, CV_FOLDS,
    ensure_directories
)
from src.data_preprocessing import (
    load_data, split_features_target,
    train_test_split_data, get_preprocessor
)


def get_models():
    """Return a dictionary of regression models to train and compare.

    Includes simple hyperparameter tuning for ensemble models
    while keeping things beginner-friendly.

    Returns:
        dict: Model name -> sklearn estimator instance.
    """
    models = {
        "Linear Regression": LinearRegression(),

        "Ridge Regression": Ridge(alpha=1.0, random_state=RANDOM_STATE),

        "Decision Tree": DecisionTreeRegressor(
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=RANDOM_STATE
        ),

        "Random Forest": RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=RANDOM_STATE,
            n_jobs=-1
        ),

        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.1,
            min_samples_split=5,
            min_samples_leaf=2,
            subsample=0.8,
            random_state=RANDOM_STATE
        )
    }
    return models


def calculate_metrics(y_true, y_pred):
    """Calculate evaluation metrics for a model.

    Args:
        y_true: Actual target values.
        y_pred: Predicted target values.

    Returns:
        dict: Dictionary with MAE, MSE, RMSE, and R2 scores.
    """
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)

    return {
        "MAE": round(mae, 4),
        "MSE": round(mse, 4),
        "RMSE": round(rmse, 4),
        "R2": round(r2, 4)
    }


def train_and_evaluate():
    """Main function: train all models, evaluate, and save the best one.

    This function:
    1. Loads the dataset
    2. Preprocesses and splits the data
    3. Trains each model using a full Pipeline (preprocessing + model)
    4. Evaluates each model on the test set
    5. Performs cross-validation for robust evaluation
    6. Saves model comparison results to CSV
    7. Saves the best model pipeline to a .pkl file
    8. Saves metrics to a JSON file
    """
    # Create required directories
    ensure_directories()

    # Print header
    print("\n" + "=" * 65)
    print("   BOSTON HOUSE PRICE PREDICTION - MODEL TRAINING")
    print("=" * 65 + "\n")

    # Step 1: Load and prepare data
    print("📂 Step 1: Loading dataset...")
    data = load_data()

    print("\n📋 Step 2: Splitting features and target...")
    X, y = split_features_target(data)

    print("\n✂️  Step 3: Train-test split...")
    X_train, X_test, y_train, y_test = train_test_split_data(X, y)

    print("\n🔧 Step 4: Creating preprocessing pipeline...")
    preprocessor = get_preprocessor()

    # Step 2: Train and evaluate each model
    models = get_models()
    results = []

    print("\n" + "-" * 65)
    print("   🏋️  TRAINING & EVALUATING MODELS")
    print("-" * 65 + "\n")

    for name, model in models.items():
        # Create a full pipeline with preprocessing + model
        full_pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", model)
        ])

        # Train the model
        full_pipeline.fit(X_train, y_train)

        # Predict on test set (unseen data)
        y_pred = full_pipeline.predict(X_test)

        # Calculate test metrics
        test_metrics = calculate_metrics(y_test, y_pred)

        # Cross-validation score (on training data)
        cv_scores = cross_val_score(
            full_pipeline, X_train, y_train,
            cv=CV_FOLDS, scoring="r2", n_jobs=-1
        )
        cv_mean = round(cv_scores.mean(), 4)
        cv_std = round(cv_scores.std(), 4)

        # Store results
        results.append({
            "Model": name,
            "MAE": test_metrics["MAE"],
            "MSE": test_metrics["MSE"],
            "RMSE": test_metrics["RMSE"],
            "R2": test_metrics["R2"],
            "CV_R2_Mean": cv_mean,
            "CV_R2_Std": cv_std,
            "Pipeline": full_pipeline
        })

        # Print results for this model
        print(f"  📊 {name}:")
        print(f"     MAE:       {test_metrics['MAE']:.4f}")
        print(f"     MSE:       {test_metrics['MSE']:.4f}")
        print(f"     RMSE:      {test_metrics['RMSE']:.4f}")
        print(f"     R2 Score:  {test_metrics['R2']:.4f}")
        print(f"     CV R² Mean: {cv_mean:.4f} (± {cv_std:.4f})")
        print()

    # Step 3: Find the best model
    # Primary: highest R2, Secondary: lowest RMSE
    best_result = max(results, key=lambda x: (x["R2"], -x["RMSE"]))
    best_model_name = best_result["Model"]
    best_pipeline = best_result["Pipeline"]

    print("=" * 65)
    print(f"  🏆 BEST MODEL: {best_model_name}")
    print(f"     R2 Score:  {best_result['R2']:.4f}")
    print(f"     RMSE:      {best_result['RMSE']:.4f}")
    print(f"     MAE:       {best_result['MAE']:.4f}")
    print(f"     CV R² Mean: {best_result['CV_R2_Mean']:.4f}")
    print("=" * 65 + "\n")

    # Step 4: Save the best model pipeline (includes preprocessing)
    joblib.dump(best_pipeline, MODEL_PATH)
    print(f"✅ Best model pipeline saved to: {MODEL_PATH}")
    print(f"   (Includes preprocessing + {best_model_name})")

    # Step 5: Save model comparison to CSV
    comparison_df = pd.DataFrame([
        {k: v for k, v in r.items() if k != "Pipeline"}
        for r in results
    ])
    comparison_df = comparison_df.sort_values("R2", ascending=False).reset_index(drop=True)
    comparison_df.to_csv(MODEL_COMPARISON_PATH, index=False)
    print(f"✅ Model comparison saved to: {MODEL_COMPARISON_PATH}")

    # Step 6: Save metrics to JSON
    metrics_data = {
        "best_model": best_model_name,
        "best_r2": best_result["R2"],
        "best_rmse": best_result["RMSE"],
        "best_mae": best_result["MAE"],
        "best_mse": best_result["MSE"],
        "best_cv_r2_mean": best_result["CV_R2_Mean"],
        "best_cv_r2_std": best_result["CV_R2_Std"],
        "all_models": [
            {k: v for k, v in r.items() if k != "Pipeline"}
            for r in results
        ]
    }
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics_data, f, indent=4)
    print(f"✅ Metrics saved to: {METRICS_PATH}")

    print("\n✅ Training complete! Run 'python -m src.evaluate_model' to generate plots.\n")

    return best_pipeline, results


# Allow running with: python src/train_model.py
if __name__ == "__main__":
    train_and_evaluate()
