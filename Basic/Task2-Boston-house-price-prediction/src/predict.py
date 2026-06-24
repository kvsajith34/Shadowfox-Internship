"""Command-line prediction script for Boston House Price Prediction.

Accepts 13 feature values as command-line arguments and
prints the predicted house price.

Usage:
    python -m src.predict --CRIM 0.00632 --ZN 18 --INDUS 2.31 --CHAS 0 \\
        --NOX 0.538 --RM 6.575 --AGE 65.2 --DIS 4.09 --RAD 1 --TAX 296 \\
        --PTRATIO 15.3 --B 396.9 --LSTAT 4.98

    Or:
    python src/predict.py --CRIM 0.00632 --ZN 18 ...
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import joblib

# Add project root to Python path for reliable imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.config import MODEL_PATH, FEATURE_COLUMNS


def predict_price(features_dict):
    """Predict house price using the saved model pipeline.

    Args:
        features_dict (dict): Dictionary with feature names as keys
                              and numeric values as values.

    Returns:
        float: The predicted house price.

    Raises:
        FileNotFoundError: If the model file is not found.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"\n❌ Model not found at: {MODEL_PATH}\n"
            "Please train the model first by running:\n"
            "   python -m src.train_model\n"
            "or: python src/train_model.py"
        )

    # Load the saved pipeline (includes preprocessing + model)
    model = joblib.load(MODEL_PATH)

    # Prepare feature array in the correct column order
    features = [features_dict[col] for col in FEATURE_COLUMNS]
    features_array = np.array([features])

    # Make prediction
    prediction = model.predict(features_array)[0]
    return prediction


def main():
    """Parse command-line arguments and make a prediction."""
    parser = argparse.ArgumentParser(
        description="Predict Boston House Price using the trained model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python -m src.predict --CRIM 0.00632 --ZN 18 --INDUS 2.31 --CHAS 0 \\
      --NOX 0.538 --RM 6.575 --AGE 65.2 --DIS 4.09 --RAD 1 --TAX 296 \\
      --PTRATIO 15.3 --B 396.9 --LSTAT 4.98
        """
    )

    # Feature descriptions for help text
    feature_help = {
        "CRIM": "Per capita crime rate by town",
        "ZN": "Proportion of residential land zoned for lots over 25,000 sq.ft.",
        "INDUS": "Proportion of non-retail business acres per town",
        "CHAS": "Charles River dummy variable (0 or 1)",
        "NOX": "Nitric oxides concentration (parts per 10 million)",
        "RM": "Average number of rooms per dwelling",
        "AGE": "Proportion of owner-occupied units built prior to 1940",
        "DIS": "Weighted distances to five Boston employment centers",
        "RAD": "Index of accessibility to radial highways",
        "TAX": "Full-value property-tax rate per $10,000",
        "PTRATIO": "Pupil-teacher ratio by town",
        "B": "1000(Bk - 0.63)^2 where Bk is the proportion of Black residents",
        "LSTAT": "% Lower status of the population",
    }

    for col in FEATURE_COLUMNS:
        parser.add_argument(
            f"--{col}", type=float, required=True,
            help=feature_help.get(col, f"Value for {col}")
        )

    args = parser.parse_args()

    # Build features dictionary
    features = {col: getattr(args, col) for col in FEATURE_COLUMNS}

    try:
        prediction = predict_price(features)

        print("\n" + "=" * 55)
        print("   🏠 BOSTON HOUSE PRICE PREDICTION")
        print("=" * 55)
        print(f"   {'Feature':<12} {'Value':>10}")
        print("-" * 55)
        for col in FEATURE_COLUMNS:
            print(f"   {col:<12} {features[col]:>10.4f}")
        print("-" * 55)
        print(f"   💰 Predicted Price: {prediction:.2f}")
        print(f"   (Median value in $1,000's)")
        print("=" * 55 + "\n")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
