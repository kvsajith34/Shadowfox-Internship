"""
Loan Approval Prediction System - Streamlit Web App.

Run:
    streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make 'src' importable when run via Streamlit
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from src.data_preprocessing import analyze_outliers, clean_dataframe
from src.predict import build_input_dataframe, predict
from src.utils import (
    METADATA_PATH,
    REPORTS_DIR,
    load_dataset,
    load_json,
)

# --------------------------------------------------------------------------- #
# Page configuration & theme
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="Loan Approval Prediction System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .main-title { font-size: 2.3rem; font-weight: 800; color: #1f4e79; }
    .sub-title  { font-size: 1.05rem; color: #555; margin-bottom: 1.2rem; }
    .result-approved {
        background-color: #e6f4ea; border-left: 6px solid #2e7d32;
        padding: 1rem 1.2rem; border-radius: 8px; font-size: 1.1rem;
    }
    .result-rejected {
        background-color: #fdecea; border-left: 6px solid #c62828;
        padding: 1rem 1.2rem; border-radius: 8px; font-size: 1.1rem;
    }
    .metric-card {
        background: #f5f7fa; padding: 1rem; border-radius: 10px;
        text-align: center; border: 1px solid #e0e0e0;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# Cached loaders
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner=False)
def _load_metadata():
    return load_json(METADATA_PATH)


@st.cache_data(show_spinner=False)
def _load_data():
    try:
        return load_dataset()
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Sections
# --------------------------------------------------------------------------- #
def section_overview():
    st.markdown('<div class="main-title">🏦 Loan Approval Prediction System</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">An intelligent machine learning system that '
        'predicts whether a loan application is likely to be approved or '
        'rejected based on applicant financial and demographic details.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Project Overview")
    st.write(
        """
        This application uses a trained classification model to estimate loan
        approval outcomes. The model was trained on historical loan application
        data and selected based on F1-score and cross-validation reliability.

        **How to use:** Go to **Applicant Prediction** in the sidebar, fill in
        the applicant details, and click **Predict**.
        """
    )
    meta = _load_metadata()
    if meta:
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="metric-card"><b>Model</b><br>{meta.get("best_model","-")}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><b>Accuracy</b><br>{meta.get("accuracy","-")}</div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><b>F1-score</b><br>{meta.get("f1_score","-")}</div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="metric-card"><b>Dataset size</b><br>{meta.get("dataset_size","-")}</div>', unsafe_allow_html=True)
    else:
        st.info("Train the model first: `python src/train_model.py`")


def section_prediction():
    st.markdown("## 📝 Applicant Input Form")
    with st.form("applicant_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            gender = st.selectbox("Gender", ["Male", "Female"])
            married = st.selectbox("Married", ["Yes", "No"])
            dependents = st.selectbox("Dependents", ["0", "1", "2", "3+"])
            education = st.selectbox("Education", ["Graduate", "Not Graduate"])
        with c2:
            self_employed = st.selectbox("Self Employed", ["No", "Yes"])
            applicant_income = st.number_input("Applicant Income", min_value=0.0, value=5000.0, step=100.0)
            coapplicant_income = st.number_input("Coapplicant Income", min_value=0.0, value=1500.0, step=100.0)
            loan_amount = st.number_input("Loan Amount (in thousands)", min_value=0.0, value=150.0, step=10.0)
        with c3:
            loan_amount_term = st.number_input("Loan Amount Term (days)", min_value=0.0, value=360.0, step=12.0)
            credit_history = st.selectbox("Credit History", [1.0, 0.0])
            property_area = st.selectbox("Property Area", ["Urban", "Semiurban", "Rural"])

        submitted = st.form_submit_button("🔮 Predict")

    if submitted:
        try:
            df = build_input_dataframe(
                gender, married, dependents, education, self_employed,
                applicant_income, coapplicant_income, loan_amount,
                loan_amount_term, credit_history, property_area,
            )
            result = predict(df)
            st.markdown("## 📊 Prediction Result")

            label = result["prediction"]
            prob = result["approval_probability"]

            if label == "Approved":
                msg = ("✅ **Loan Approval Prediction: Approved**<br>"
                       "The applicant profile appears suitable for loan approval "
                       "based on the trained model.")
                st.markdown(f'<div class="result-approved">{msg}</div>', unsafe_allow_html=True)
            else:
                msg = ("❌ **Loan Approval Prediction: Rejected**<br>"
                       "The applicant profile may not satisfy the learned approval "
                       "patterns. Consider improving credit history or financial profile.")
                st.markdown(f'<div class="result-rejected">{msg}</div>', unsafe_allow_html=True)

            if prob is not None:
                st.metric("Approval Probability", f"{prob * 100:.2f}%")
                st.progress(min(max(prob, 0.0), 1.0))
                st.caption(
                    "Risk note: This probability is a model estimate, not a "
                    "guaranteed lending decision. Use as a supporting tool only."
                )
        except FileNotFoundError:
            st.error("Model not found. Run `python src/train_model.py` first.")
        except Exception as e:
            st.error(f"Prediction failed: {e}")


def section_performance():
    st.markdown("## 📈 Model Performance")
    meta = _load_metadata()
    if not meta:
        st.info("No metadata found. Train the model first.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Accuracy", meta.get("accuracy", "-"))
    c2.metric("Precision", meta.get("precision", "-"))
    c3.metric("Recall", meta.get("recall", "-"))
    c4.metric("F1-score", meta.get("f1_score", "-"))

    st.caption(f"Best model: **{meta.get('best_model','-')}** | "
               f"Trained: {meta.get('training_date','-')}")

    if "all_model_results" in meta:
        st.markdown("### Model Comparison")
        st.dataframe(pd.DataFrame(meta["all_model_results"]), use_container_width=True)

    cm_path = REPORTS_DIR / "confusion_matrix.png"
    fi_path = REPORTS_DIR / "feature_importance.png"
    cols = st.columns(2)
    if cm_path.exists():
        cols[0].image(str(cm_path), caption="Confusion Matrix")
    if fi_path.exists():
        cols[1].image(str(fi_path), caption="Feature Importance")


def section_insights():
    st.markdown("## 🔍 Dataset Insights")
    df = _load_data()
    if df is None:
        st.info("Dataset not found in data/loan_prediction.csv")
        return

    st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
    st.dataframe(df.head(10), use_container_width=True)

    if "Loan_Status" in df.columns:
        st.markdown("### Target Distribution (Approved vs Rejected)")
        st.bar_chart(df["Loan_Status"].value_counts())

    st.markdown("### IQR Outlier Analysis")
    outliers = analyze_outliers(clean_dataframe(df))
    st.dataframe(pd.DataFrame(outliers).T, use_container_width=True)


# --------------------------------------------------------------------------- #
# Sidebar navigation
# --------------------------------------------------------------------------- #
def main():
    st.sidebar.title("🏦 Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Project Overview", "Applicant Prediction", "Model Performance",
         "Dataset Insights"],
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("Loan Approval Prediction • Machine Learning Project")

    if page == "Project Overview":
        section_overview()
    elif page == "Applicant Prediction":
        section_prediction()
    elif page == "Model Performance":
        section_performance()
    elif page == "Dataset Insights":
        section_insights()


if __name__ == "__main__":
    main()