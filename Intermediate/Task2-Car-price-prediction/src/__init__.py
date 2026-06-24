"""
Car Selling Price Prediction
=============================
A complete Machine Learning project for predicting used car selling prices.

Modules:
    - data_preprocessing: Data loading, cleaning, and feature engineering
    - eda: Exploratory Data Analysis with visualizations
    - train_model: Model training, comparison, and hyperparameter tuning
    - evaluate_model: Model evaluation with plots and reports
    - predict: Command-line prediction using saved model

Usage (run from project root):
    python -m src.eda
    python -m src.train_model
    python -m src.evaluate_model
    python -m src.predict --present_price 7.5 --kms_driven 45000 --owner 0 --year 2016 --fuel_type Petrol --seller_type Dealer --transmission Manual
    streamlit run streamlit_app.py
"""

__version__ = "1.0.0"
__author__ = "Venkata Sai Ajith Kancheti"
