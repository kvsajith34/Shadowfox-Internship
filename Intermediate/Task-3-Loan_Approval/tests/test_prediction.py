"""Tests for the prediction interface."""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.predict import build_input_dataframe, predict
from src.utils import MODEL_PATH


def test_build_input_dataframe_shape():
    """Input builder should produce a single-row frame with all features."""
    df = build_input_dataframe(
        "Male", "Yes", "3+", "Graduate", "No",
        5000, 1500, 150, 360, 1.0, "Urban",
    )
    assert df.shape[0] == 1
    # '3+' must become numeric 3
    assert df["Dependents"].iloc[0] == 3


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="Model not trained yet.")
def test_prediction_returns_valid_label():
    """Prediction must return Approved or Rejected with optional probability."""
    df = build_input_dataframe(
        "Male", "Yes", "1", "Graduate", "No",
        5000, 1500, 150, 360, 1.0, "Urban",
    )
    result = predict(df)
    assert result["prediction"] in ("Approved", "Rejected")
    if result["approval_probability"] is not None:
        assert 0.0 <= result["approval_probability"] <= 1.0


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="Model not trained yet.")
def test_model_file_exists_after_training():
    """Model file should exist once training has been run."""
    assert MODEL_PATH.exists()