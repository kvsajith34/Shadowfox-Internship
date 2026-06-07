"""
Command-line + importable prediction interface.

Example:
    python src/predict.py \
        --gender Male --married Yes --dependents 1 \
        --education Graduate --self_employed No \
        --applicant_income 5000 --coapplicant_income 1500 \
        --loan_amount 150 --loan_amount_term 360 \
        --credit_history 1 --property_area Urban
"""

from __future__ import annotations

import argparse

import pandas as pd

from src.data_preprocessing import ALL_FEATURES, clean_dataframe
from src.utils import load_model


def build_input_dataframe(
    gender,
    married,
    dependents,
    education,
    self_employed,
    applicant_income,
    coapplicant_income,
    loan_amount,
    loan_amount_term,
    credit_history,
    property_area,
) -> pd.DataFrame:
    """Assemble a single-row DataFrame matching the training schema."""
    row = {
        "Gender": gender,
        "Married": married,
        "Dependents": dependents,
        "Education": education,
        "Self_Employed": self_employed,
        "ApplicantIncome": applicant_income,
        "CoapplicantIncome": coapplicant_income,
        "LoanAmount": loan_amount,
        "Loan_Amount_Term": loan_amount_term,
        "Credit_History": credit_history,
        "Property_Area": property_area,
    }
    df = pd.DataFrame([row])
    df = clean_dataframe(df)  # handles '3+' etc.
    # Ensure all expected columns exist & ordered
    for col in ALL_FEATURES:
        if col not in df.columns:
            df[col] = None
    return df[ALL_FEATURES]


def predict(input_df: pd.DataFrame) -> dict:
    """
    Run prediction on a prepared input DataFrame.
    Returns dict with label and probability (if available).
    """
    model = load_model()
    pred = int(model.predict(input_df)[0])
    label = "Approved" if pred == 1 else "Rejected"

    prob = None
    if hasattr(model, "predict_proba"):
        try:
            proba = model.predict_proba(input_df)[0]
            prob = float(proba[1])  # probability of class "Approved"
        except Exception:
            prob = None

    return {"prediction": label, "approval_probability": prob}


def predict_from_args(args) -> dict:
    """Build input from CLI args and predict."""
    df = build_input_dataframe(
        gender=args.gender,
        married=args.married,
        dependents=args.dependents,
        education=args.education,
        self_employed=args.self_employed,
        applicant_income=args.applicant_income,
        coapplicant_income=args.coapplicant_income,
        loan_amount=args.loan_amount,
        loan_amount_term=args.loan_amount_term,
        credit_history=args.credit_history,
        property_area=args.property_area,
    )
    return predict(df)


def parse_args():
    p = argparse.ArgumentParser(description="Loan Approval Prediction (CLI)")
    p.add_argument("--gender", required=True, choices=["Male", "Female"])
    p.add_argument("--married", required=True, choices=["Yes", "No"])
    p.add_argument("--dependents", required=True)  # 0,1,2,3+
    p.add_argument(
        "--education", required=True, choices=["Graduate", "Not Graduate"]
    )
    p.add_argument("--self_employed", required=True, choices=["Yes", "No"])
    p.add_argument("--applicant_income", required=True, type=float)
    p.add_argument("--coapplicant_income", required=True, type=float)
    p.add_argument("--loan_amount", required=True, type=float)
    p.add_argument("--loan_amount_term", required=True, type=float)
    p.add_argument("--credit_history", required=True, type=float, choices=[0.0, 1.0])
    p.add_argument(
        "--property_area",
        required=True,
        choices=["Urban", "Semiurban", "Rural"],
    )
    return p.parse_args()


def main():
    args = parse_args()
    result = predict_from_args(args)
    print("\n" + "=" * 45)
    print(f"Loan Approval Prediction: {result['prediction']}")
    if result["approval_probability"] is not None:
        print(f"Approval Probability: {result['approval_probability'] * 100:.2f}%")
    else:
        print("Approval Probability: Not available for this model")
    print("=" * 45 + "\n")


if __name__ == "__main__":
    main()