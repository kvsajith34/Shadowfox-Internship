"""
Streamlit App — Car Selling Price Prediction
==============================================
A simple, professional Streamlit web app that loads the trained
model and allows users to predict used car selling prices.

Run (from project root):
    streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import joblib


# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


# -------------------------------------------------------
# Page Config
# -------------------------------------------------------
st.set_page_config(
    page_title="Car Price Predictor",
    page_icon="🚗",
    layout="centered"
)


# -------------------------------------------------------
# Load Model
# -------------------------------------------------------
@st.cache_resource
def load_model():
    """Load the saved model pipeline."""
    model_path = os.path.join(PROJECT_ROOT, "models", "car_price_model.pkl")
    if not os.path.exists(model_path):
        return None
    try:
        return joblib.load(model_path)
    except Exception:
        return None


# -------------------------------------------------------
# Main App
# -------------------------------------------------------
def main():
    # Title
    st.title("🚗 Car Selling Price Predictor")
    st.markdown("---")

    # Problem Statement
    st.markdown("""
    ### Problem Statement
    Predict the **selling price** of a used car based on its details such as
    showroom price, kilometers driven, age, fuel type, seller type,
    transmission, and number of previous owners.

    This app uses a **Random Forest Regressor** trained on the CarDekho dataset.
    """)

    st.markdown("---")

    # Check if model exists
    model = load_model()

    if model is None:
        st.warning("⚠️ Model not found! Please train the model first.")
        st.code("python -m src.train_model", language="bash")
        st.stop()

    # Input Form
    st.subheader("📋 Enter Car Details")

    col1, col2 = st.columns(2)

    with col1:
        year = st.number_input(
            "Manufacturing Year",
            min_value=2000, max_value=datetime.now().year,
            value=2016, step=1,
            help="Year the car was manufactured"
        )
        present_price = st.number_input(
            "Present Showroom Price (Lakhs)",
            min_value=0.1, max_value=100.0,
            value=7.5, step=0.1,
            help="Current showroom/ex-showroom price in Lakhs"
        )
        kms_driven = st.number_input(
            "Kilometers Driven",
            min_value=0, max_value=500000,
            value=45000, step=1000,
            help="Total kilometers the car has been driven"
        )

    with col2:
        owner = st.selectbox(
            "Number of Previous Owners",
            options=[0, 1, 2, 3],
            index=0,
            format_func=lambda x: f"{x} — {'First' if x == 0 else 'Second' if x == 1 else 'Third' if x == 2 else 'Fourth+'} Owner",
            help="Number of previous owners of the car"
        )
        fuel_type = st.selectbox(
            "Fuel Type",
            options=["Petrol", "Diesel", "CNG"],
            index=0,
            help="Type of fuel the car uses"
        )
        seller_type = st.selectbox(
            "Seller Type",
            options=["Dealer", "Individual"],
            index=0,
            help="Whether the seller is a dealer or an individual"
        )

    transmission = st.selectbox(
        "Transmission Type",
        options=["Manual", "Automatic"],
        index=0,
        help="Transmission type of the car"
    )

    st.markdown("---")

    # Predict Button
    if st.button("🚗 Predict Selling Price", type="primary", use_container_width=True):
        # Calculate Car_Age
        current_year = datetime.now().year
        car_age = current_year - year

        # Create input DataFrame
        input_data = pd.DataFrame({
            'Present_Price': [present_price],
            'Kms_Driven': [kms_driven],
            'Owner': [owner],
            'Car_Age': [car_age],
            'Fuel_Type': [fuel_type],
            'Seller_Type': [seller_type],
            'Transmission': [transmission]
        })

        try:
            prediction = model.predict(input_data)[0]
            predicted_price = round(prediction, 2)

            # Display result
            st.success(f"💰 **Estimated Selling Price: {predicted_price} Lakhs**")

            # Additional info
            depreciation = ((1 - predicted_price / present_price) * 100)
            retained = ((predicted_price / present_price) * 100)
            st.info(f"📊 Car Age: {car_age} years | Depreciation: {depreciation:.1f}% | Value Retained: {retained:.1f}%")

        except Exception as e:
            st.error(f"❌ Prediction error: {e}")

    # Note
    st.markdown("---")
    st.caption("📌 **Note:** This is an approximate ML-based estimate and not a guaranteed market value. Actual prices may vary based on market conditions, car condition, location, and other factors.")


if __name__ == "__main__":
    main()
