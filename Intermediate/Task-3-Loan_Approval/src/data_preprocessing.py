"""
Data cleaning and preprocessing pipeline.

Responsibilities:
- Load + clean the raw dataset (missing values, 'Dependents' 3+ handling).
- Define feature lists.
- Build a scikit-learn ColumnTransformer pipeline (imputation, encoding, scaling).
- Provide IQR-based outlier analysis used by EDA & reports.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.utils import ID_COLUMN, TARGET_COLUMN, load_dataset

# --------------------------------------------------------------------------- #
# Feature definitions
# --------------------------------------------------------------------------- #
CATEGORICAL_FEATURES = [
    "Gender",
    "Married",
    "Education",
    "Self_Employed",
    "Property_Area",
]

# Treated as numeric after cleaning (Dependents '3+' -> 3, Credit_History 0/1)
NUMERIC_FEATURES = [
    "Dependents",
    "ApplicantIncome",
    "CoapplicantIncome",
    "LoanAmount",
    "Loan_Amount_Term",
    "Credit_History",
]

ALL_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES

OUTLIER_COLUMNS = ["ApplicantIncome", "CoapplicantIncome", "LoanAmount"]


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply deterministic cleaning steps that are NOT learned from data:
    - Drop Loan_ID (identifier only).
    - Convert 'Dependents' value '3+' into numeric 3.
    - Normalize Credit_History to numeric.
    Imputation / encoding / scaling are handled by the sklearn pipeline.
    """
    df = df.copy()

    # Drop identifier column if present
    if ID_COLUMN in df.columns:
        df = df.drop(columns=[ID_COLUMN])

    # Handle '3+' in Dependents -> 3, then numeric
    if "Dependents" in df.columns:
        df["Dependents"] = (
            df["Dependents"].astype(str).str.replace("+", "", regex=False)
        )
        df["Dependents"] = pd.to_numeric(df["Dependents"], errors="coerce")

    # Ensure Credit_History is numeric (0.0 / 1.0)
    if "Credit_History" in df.columns:
        df["Credit_History"] = pd.to_numeric(
            df["Credit_History"], errors="coerce"
        )

    return df


def split_features_target(df: pd.DataFrame):
    """
    Split a cleaned dataframe into X (features) and y (encoded target 0/1).
    Loan_Status: Y -> 1 (Approved), N -> 0 (Rejected).
    """
    df = df.copy()

    if TARGET_COLUMN not in df.columns:
        raise KeyError(f"Target column '{TARGET_COLUMN}' missing from dataset.")

    # Drop rows with missing target
    df = df.dropna(subset=[TARGET_COLUMN])

    y = df[TARGET_COLUMN].map({"Y": 1, "N": 0})
    # In case the dataset already uses 1/0
    if y.isna().any():
        y = df[TARGET_COLUMN].map(
            {"Y": 1, "N": 0, 1: 1, 0: 0, "1": 1, "0": 0}
        )
    y = y.astype(int)

    # Keep only known feature columns that actually exist
    feature_cols = [c for c in ALL_FEATURES if c in df.columns]
    X = df[feature_cols]
    return X, y


def build_preprocessing_pipeline() -> ColumnTransformer:
    """
    Build a ColumnTransformer that:
    - Numeric: median imputation + standard scaling.
    - Categorical: mode imputation + one-hot encoding.
    """
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore", drop="if_binary"),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )
    return preprocessor


def get_clean_data():
    """Convenience: load raw csv, clean it, return X, y."""
    raw = load_dataset()
    cleaned = clean_dataframe(raw)
    X, y = split_features_target(cleaned)
    return X, y


# --------------------------------------------------------------------------- #
# IQR outlier analysis
# --------------------------------------------------------------------------- #
def iqr_bounds(series: pd.Series):
    """Return (Q1, Q3, IQR, lower_bound, upper_bound) for a numeric series."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return q1, q3, iqr, lower, upper


def analyze_outliers(df: pd.DataFrame, columns=OUTLIER_COLUMNS) -> dict:
    """
    Compute IQR-based outlier statistics for the requested columns.
    Returns a dictionary with bounds and outlier counts.
    """
    results = {}
    for col in columns:
        if col not in df.columns:
            continue
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        q1, q3, iqr, lower, upper = iqr_bounds(s)
        n_outliers = int(((s < lower) | (s > upper)).sum())
        results[col] = {
            "Q1": float(q1),
            "Q3": float(q3),
            "IQR": float(iqr),
            "lower_bound": float(lower),
            "upper_bound": float(upper),
            "outlier_count": n_outliers,
            "outlier_pct": round(100 * n_outliers / max(len(s), 1), 2),
        }
    return results


if __name__ == "__main__":
    X, y = get_clean_data()
    print("Features shape:", X.shape)
    print("Target distribution:\n", y.value_counts())
    raw = load_dataset()
    print("\nOutlier analysis:")
    for col, stats in analyze_outliers(clean_dataframe(raw)).items():
        print(f"  {col}: {stats}")