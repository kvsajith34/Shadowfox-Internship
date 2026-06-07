"""Tests for data loading and preprocessing."""

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_preprocessing import (
    analyze_outliers,
    build_preprocessing_pipeline,
    clean_dataframe,
    split_features_target,
)
from src.utils import DATA_PATH, load_dataset


def test_dataset_loads():
    """Dataset should load successfully and contain the target column."""
    if not DATA_PATH.exists():
        pytest.skip("Dataset not present; skipping load test.")
    df = load_dataset()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "Loan_Status" in df.columns


def test_clean_dependents_and_drop_id():
    """Cleaning should convert '3+' to 3 and drop Loan_ID."""
    sample = pd.DataFrame({
        "Loan_ID": ["LP001"],
        "Dependents": ["3+"],
        "Credit_History": ["1"],
        "Loan_Status": ["Y"],
    })
    cleaned = clean_dataframe(sample)
    assert "Loan_ID" not in cleaned.columns
    assert cleaned["Dependents"].iloc[0] == 3
    assert cleaned["Credit_History"].iloc[0] == 1


def test_pipeline_handles_missing_values():
    """Preprocessing pipeline should impute missing values without error."""
    sample = pd.DataFrame({
        "Gender": ["Male", None],
        "Married": ["Yes", "No"],
        "Education": ["Graduate", "Not Graduate"],
        "Self_Employed": [None, "No"],
        "Property_Area": ["Urban", "Rural"],
        "Dependents": [1, None],
        "ApplicantIncome": [5000, None],
        "CoapplicantIncome": [1500, 0],
        "LoanAmount": [None, 120],
        "Loan_Amount_Term": [360, None],
        "Credit_History": [1.0, None],
    })
    pre = build_preprocessing_pipeline()
    transformed = pre.fit_transform(sample)
    assert transformed.shape[0] == 2


def test_split_features_target():
    """Target should map Y/N to 1/0."""
    sample = pd.DataFrame({
        "Gender": ["Male", "Female"],
        "Married": ["Yes", "No"],
        "Education": ["Graduate", "Not Graduate"],
        "Self_Employed": ["No", "No"],
        "Property_Area": ["Urban", "Rural"],
        "Dependents": [1, 0],
        "ApplicantIncome": [5000, 3000],
        "CoapplicantIncome": [1500, 0],
        "LoanAmount": [150, 120],
        "Loan_Amount_Term": [360, 360],
        "Credit_History": [1.0, 0.0],
        "Loan_Status": ["Y", "N"],
    })
    X, y = split_features_target(sample)
    assert list(y) == [1, 0]
    assert "Loan_Status" not in X.columns


def test_outlier_analysis_keys():
    """Outlier analysis should return expected bound keys."""
    sample = pd.DataFrame({
        "ApplicantIncome": [1000, 2000, 3000, 4000, 100000],
        "CoapplicantIncome": [0, 500, 1000, 1500, 20000],
        "LoanAmount": [100, 120, 150, 200, 700],
    })
    res = analyze_outliers(sample)
    assert "ApplicantIncome" in res
    for key in ("Q1", "Q3", "IQR", "lower_bound", "upper_bound"):
        assert key in res["ApplicantIncome"]