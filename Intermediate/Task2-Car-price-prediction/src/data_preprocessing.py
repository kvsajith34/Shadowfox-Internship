"""
Data Preprocessing Module
=========================
Handles loading, cleaning, feature engineering, and preprocessing
of the car dataset for machine learning.

Usage (run from project root):
    python -m src.data_preprocessing
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer


# Project root directory (one level up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_data_path(filename: str = "car.csv") -> str:
    """Get the full path to a data file.

    Args:
        filename: Name of the file in the data/ directory.

    Returns:
        Absolute path to the data file.
    """
    return os.path.join(PROJECT_ROOT, "data", filename)


# -------------------------------------------------------
# 1. Load Dataset
# -------------------------------------------------------
def load_data(filepath: str) -> pd.DataFrame:
    """Load the car dataset from CSV file.

    Args:
        filepath: Path to the car.csv file.

    Returns:
        pandas DataFrame with the loaded data.
    """
    try:
        df = pd.read_csv(filepath)
        print(f"✅ Dataset loaded successfully from: {filepath}")
        print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        return df
    except FileNotFoundError:
        print(f"❌ Error: File not found at '{filepath}'")
        print("   Please ensure 'car.csv' is placed in the 'data/' folder.")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return pd.DataFrame()


# -------------------------------------------------------
# 2. Inspect Dataset
# -------------------------------------------------------
def inspect_data(df: pd.DataFrame) -> None:
    """Print basic information about the dataset.

    Args:
        df: The pandas DataFrame to inspect.
    """
    print("\n" + "=" * 60)
    print("DATASET OVERVIEW")
    print("=" * 60)
    print(f"\n📐 Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print("\n📋 Column Info:")
    for i, (col, dtype) in enumerate(zip(df.columns, df.dtypes), 1):
        print(f"   {i}. {col:20s} ({dtype})")

    print("\n🔍 First 5 Rows:")
    print(df.head().to_string())

    print("\n📊 Missing Values:")
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("   ✅ No missing values found!")
    else:
        print(missing[missing > 0].to_string())

    print(f"\n🔁 Duplicate Rows: {df.duplicated().sum()}")


# -------------------------------------------------------
# 3. Clean Dataset
# -------------------------------------------------------
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates and handle missing values.

    Args:
        df: The pandas DataFrame to clean.

    Returns:
        Cleaned pandas DataFrame.
    """
    df_clean = df.copy()

    # Remove duplicates
    duplicates = df_clean.duplicated().sum()
    if duplicates > 0:
        df_clean = df_clean.drop_duplicates()
        df_clean = df_clean.reset_index(drop=True)
        print(f"🗑️  Removed {duplicates} duplicate row(s)")
    else:
        print("✅ No duplicate rows found")

    # Handle missing values
    missing = df_clean.isnull().sum()
    if missing.sum() > 0:
        # Fill numerical columns with median
        num_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            if df_clean[col].isnull().sum() > 0:
                df_clean[col].fillna(df_clean[col].median(), inplace=True)

        # Fill categorical columns with mode
        cat_cols = df_clean.select_dtypes(include=['object']).columns
        for col in cat_cols:
            if df_clean[col].isnull().sum() > 0:
                df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)

        print("✅ Missing values handled")
    else:
        print("✅ No missing values to handle")

    return df_clean


# -------------------------------------------------------
# 4. Feature Engineering
# -------------------------------------------------------
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create new features from existing columns.

    - Creates Car_Age = current_year - Year
    - Drops Car_Name (used only for display/EDA)
    - Drops Year (replaced by Car_Age)

    Args:
        df: The pandas DataFrame to transform.

    Returns:
        DataFrame with engineered features.
    """
    df_fe = df.copy()

    # Create Car_Age
    current_year = datetime.now().year
    df_fe['Car_Age'] = current_year - df_fe['Year']
    print(f"🆕 Created 'Car_Age' feature (Current Year: {current_year})")

    # Drop Car_Name (not useful for modeling)
    if 'Car_Name' in df_fe.columns:
        df_fe = df_fe.drop('Car_Name', axis=1)
        print("🗑️  Dropped 'Car_Name' column (not used for modeling)")

    # Drop Year (replaced by Car_Age)
    if 'Year' in df_fe.columns:
        df_fe = df_fe.drop('Year', axis=1)
        print("🗑️  Dropped 'Year' column (replaced by Car_Age)")

    return df_fe


# -------------------------------------------------------
# 5. Prepare Features and Target
# -------------------------------------------------------
def prepare_features_target(df: pd.DataFrame):
    """Separate features (X) and target (y).

    Final features used:
        Present_Price, Kms_Driven, Owner, Car_Age,
        Fuel_Type, Seller_Type, Transmission

    Target: Selling_Price

    Args:
        df: DataFrame with engineered features.

    Returns:
        Tuple of (X, y) where X is features and y is target.
    """
    feature_columns = [
        'Present_Price', 'Kms_Driven', 'Owner', 'Car_Age',
        'Fuel_Type', 'Seller_Type', 'Transmission'
    ]

    X = df[feature_columns]
    y = df['Selling_Price']

    print(f"\n✅ Features shape: {X.shape}")
    print(f"✅ Target shape: {y.shape}")
    print(f"   Feature columns: {feature_columns}")

    return X, y


# -------------------------------------------------------
# 6. Create Preprocessing Pipeline
# -------------------------------------------------------
def create_preprocessor() -> ColumnTransformer:
    """Create a ColumnTransformer for preprocessing.

    Numerical features → SimpleImputer(median) + StandardScaler
    Categorical features → SimpleImputer(most_frequent) + OneHotEncoder(drop=first)

    Returns:
        Sklearn ColumnTransformer object.
    """
    numerical_features = ['Present_Price', 'Kms_Driven', 'Owner', 'Car_Age']
    categorical_features = ['Fuel_Type', 'Seller_Type', 'Transmission']

    numerical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='drop'
    )

    print("✅ Preprocessing pipeline created")
    print(f"   Numerical features : {numerical_features}")
    print(f"   Categorical features: {categorical_features}")

    return preprocessor


# -------------------------------------------------------
# 7. Full Preprocessing Pipeline
# -------------------------------------------------------
def preprocess_pipeline(filepath: str = None):
    """Complete preprocessing pipeline: load → clean → engineer → split.

    Args:
        filepath: Path to the car.csv file. If None, uses data/car.csv
                  relative to the project root.

    Returns:
        Tuple of (X, y, preprocessor) or (None, None, None) on error.
    """
    if filepath is None:
        filepath = get_data_path("car.csv")

    print("\n" + "=" * 60)
    print("DATA PREPROCESSING PIPELINE")
    print("=" * 60)

    # Load data
    df = load_data(filepath)
    if df.empty:
        return None, None, None

    # Inspect data
    inspect_data(df)

    # Clean data
    print("\n--- Cleaning Data ---")
    df_clean = clean_data(df)

    # Feature engineering
    print("\n--- Feature Engineering ---")
    df_fe = engineer_features(df_clean)

    # Prepare features and target
    print("\n--- Preparing Features and Target ---")
    X, y = prepare_features_target(df_fe)

    # Create preprocessor
    print("\n--- Creating Preprocessor ---")
    preprocessor = create_preprocessor()

    print("\n✅ Preprocessing complete!")
    return X, y, preprocessor


# -------------------------------------------------------
# Main
# -------------------------------------------------------
if __name__ == "__main__":
    X, y, preprocessor = preprocess_pipeline()
    if X is not None:
        print(f"\n📈 Final dataset ready: {X.shape[0]} samples, {X.shape[1]} features")
