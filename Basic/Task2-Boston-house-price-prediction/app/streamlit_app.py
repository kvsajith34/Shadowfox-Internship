"""Streamlit web application for Boston House Price Prediction.

A simple interactive web app where users can enter feature values
and get an instant predicted house price.

Run with:
    streamlit run app/streamlit_app.py

Or:
    python -m streamlit run app/streamlit_app.py
"""

import streamlit as st
import numpy as np
import sys
from pathlib import Path

# Add project root to Python path for reliable imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.config import MODEL_PATH, FEATURE_COLUMNS

# ----- Page Configuration -----
st.set_page_config(
    page_title="Boston House Price Predictor",
    page_icon="🏠",
    layout="wide"
)

# ----- App Title and Description -----
st.title("🏠 Boston House Price Prediction")
st.markdown(
    "Predict the median value of owner-occupied homes in Boston "
    "using a trained regression model. Adjust the feature values below "
    "and click **Predict Price** to see the result."
)
st.markdown("---")

# ----- Feature Definitions -----
# Each feature: (label, description, min, max, default, step)
feature_info = {
    "CRIM": ("Crime Rate", "Per capita crime rate by town", 0.00632, 88.98, 0.00632, 0.001),
    "ZN": ("Residential Land", "Proportion of residential land zoned for lots over 25,000 sq.ft.", 0.0, 100.0, 18.0, 1.0),
    "INDUS": ("Business Acres", "Proportion of non-retail business acres per town", 0.46, 27.74, 2.31, 0.01),
    "CHAS": ("Charles River", "1 if tract bounds the Charles River; 0 otherwise", 0.0, 1.0, 0.0, 1.0),
    "NOX": ("NOx Concentration", "Nitric oxides concentration (parts per 10 million)", 0.385, 0.871, 0.538, 0.001),
    "RM": ("Avg. Rooms", "Average number of rooms per dwelling", 3.561, 8.78, 6.575, 0.01),
    "AGE": ("Old Buildings %", "Proportion of units built before 1940", 2.9, 100.0, 65.2, 0.1),
    "DIS": ("Employment Dist.", "Weighted distances to Boston employment centers", 1.13, 12.13, 4.09, 0.01),
    "RAD": ("Highway Access", "Index of accessibility to radial highways", 1.0, 24.0, 1.0, 1.0),
    "TAX": ("Property Tax", "Property-tax rate per $10,000", 187.0, 711.0, 296.0, 1.0),
    "PTRATIO": ("Pupil-Teacher Ratio", "Pupil-teacher ratio by town", 12.6, 22.0, 15.3, 0.1),
    "B": ("Demographic Score", "1000(Bk - 0.63)^2", 0.32, 396.9, 396.9, 0.1),
    "LSTAT": ("Lower Status %", "% Lower status of the population", 1.73, 37.97, 4.98, 0.01),
}


# ----- Load Model -----
@st.cache_resource
def load_model():
    """Load the saved model pipeline."""
    if not MODEL_PATH.exists():
        return None
    import joblib
    return joblib.load(MODEL_PATH)


model = load_model()

# ----- Show Error if Model Missing -----
if model is None:
    st.error("⚠️ **Model not found!**")
    st.markdown(
        "The trained model file (`models/best_model.pkl`) was not found.\n\n"
        "**To fix this, run the training script first:**\n\n"
        "```\n"
        "python -m src.train_model\n"
        "```\n\n"
        "Then refresh this page."
    )
    st.stop()

# ----- Feature Input Form -----
st.subheader("📝 Enter Feature Values")

# Create 3 columns for layout
col1, col2, col3 = st.columns(3)
columns = [col1, col2, col3]

features = {}

for i, col_name in enumerate(FEATURE_COLUMNS):
    label, desc, min_val, max_val, default, step = feature_info[col_name]
    current_col = columns[i % 3]

    with current_col:
        if col_name == "CHAS":
            # Use a selectbox for binary feature
            features[col_name] = st.selectbox(
                f"{col_name}: {label}",
                options=[0.0, 1.0],
                index=0,
                format_func=lambda x: "Yes (1) — Tract bounds river" if x == 1.0 else "No (0) — Does not bound river",
                help=desc
            )
        else:
            features[col_name] = st.number_input(
                f"{col_name}: {label}",
                min_value=min_val,
                max_value=max_val,
                value=default,
                step=step,
                help=desc,
                format="%.4f" if step < 0.01 else "%.2f" if step < 1 else "%.0f"
            )

st.markdown("---")

# ----- Predict Button -----
if st.button("🔮 Predict House Price", type="primary", use_container_width=True):
    # Prepare feature array
    feature_values = [features[col] for col in FEATURE_COLUMNS]
    features_array = np.array([feature_values])

    # Make prediction
    prediction = model.predict(features_array)[0]

    # Display result
    st.success(f"💰 **Predicted House Price: ${prediction:.2f}k**")

    with st.expander("📊 Feature Values Used"):
        for col_name in FEATURE_COLUMNS:
            st.write(f"**{col_name}**: {features[col_name]}")

# ----- Footer Note -----
st.markdown("---")
st.caption(
    "⚠️ **Educational Note:** This Boston Housing dataset is from 1978 and contains "
    "ethical concerns. This project is for **educational purposes only** and should "
    "not be used for real-world real estate pricing decisions."
)
