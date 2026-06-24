"""Data preprocessing module for Boston House Price Prediction.

Handles data loading, feature-target splitting, train-test splitting,
and preprocessing pipeline creation.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from src.config import (
    DATA_PATH, FEATURE_COLUMNS, TARGET_COLUMN,
    MISSING_COLUMNS, TEST_SIZE, RANDOM_STATE
)


def load_data():
    """Load the Boston Housing dataset from CSV file.

    Returns:
        pd.DataFrame: The loaded dataset.

    Raises:
        FileNotFoundError: If HousingData.csv is not found in data/ folder.
    """
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"\n❌ Dataset not found at: {DATA_PATH}\n"
            "Please place 'HousingData.csv' inside the 'data/' folder.\n"
            "Expected path: Boston-House-Price-Prediction/data/HousingData.csv"
        )

    data = pd.read_csv(DATA_PATH)
    print(f"✅ Dataset loaded successfully: {data.shape[0]} rows, {data.shape[1]} columns")

    # Display basic info
    print(f"   Columns: {list(data.columns)}")
    print(f"   Target column: '{TARGET_COLUMN}'")

    # Check and report missing values
    missing = data.isnull().sum()
    missing_cols = missing[missing > 0]
    if not missing_cols.empty:
        print(f"   ⚠️  Missing values found:")
        for col, count in missing_cols.items():
            print(f"       {col}: {count} missing values")
        print(f"   → Will be handled with median imputation.")
    else:
        print(f"   ✅ No missing values found.")

    return data


def split_features_target(data):
    """Split dataset into features (X) and target (y).

    Args:
        data (pd.DataFrame): The full dataset.

    Returns:
        tuple: (X, y) where X is features and y is target.
    """
    if TARGET_COLUMN not in data.columns:
        raise ValueError(
            f"Target column '{TARGET_COLUMN}' not found in dataset. "
            f"Available columns: {list(data.columns)}"
        )

    X = data[FEATURE_COLUMNS]
    y = data[TARGET_COLUMN]

    print(f"✅ Features shape: {X.shape}, Target shape: {y.shape}")
    return X, y


def train_test_split_data(X, y):
    """Split data into training and testing sets.

    Uses test_size=0.2 and random_state=42 for reproducibility.

    Args:
        X (pd.DataFrame): Feature data.
        y (pd.Series): Target data.

    Returns:
        tuple: (X_train, X_test, y_train, y_test)
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    print(f"✅ Train-test split complete:")
    print(f"   Training samples: {X_train.shape[0]}")
    print(f"   Testing samples:  {X_test.shape[0]}")
    print(f"   Test size: {TEST_SIZE} | Random state: {RANDOM_STATE}")

    return X_train, X_test, y_train, y_test


def get_preprocessor():
    """Create a preprocessing pipeline with median imputation and standardization.

    The pipeline includes:
    1. SimpleImputer with median strategy (handles missing values)
    2. StandardScaler (normalizes features for better model performance)

    Returns:
        Pipeline: A sklearn Pipeline with imputation and scaling steps.
    """
    preprocessor = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    print("✅ Preprocessing pipeline created:")
    print("   Step 1: SimpleImputer(strategy='median')")
    print("   Step 2: StandardScaler()")

    return preprocessor
