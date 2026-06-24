"""
Prediction Script
=================
Command-line prediction using the saved model.

Usage (run from project root):
    python -m src.predict --present_price 7.5 --kms_driven 45000 --owner 0 --year 2016 --fuel_type Petrol --seller_type Dealer --transmission Manual
"""

import argparse
import os
import pandas as pd
from datetime import datetime
import joblib

# Project root directory (one level up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def predict_price(present_price, kms_driven, owner, year,
                  fuel_type, seller_type, transmission):
    """Make a price prediction using the saved model.

    Args:
        present_price: Current showroom price in Lakhs.
        kms_driven: Total kilometers driven.
        owner: Number of previous owners.
        year: Manufacturing year.
        fuel_type: Petrol / Diesel / CNG.
        seller_type: Dealer / Individual.
        transmission: Manual / Automatic.

    Returns:
        Predicted selling price in Lakhs, or None on error.
    """
    model_path = os.path.join(PROJECT_ROOT, "models", "car_price_model.pkl")

    if not os.path.exists(model_path):
        print(f"❌ Error: Model file not found at {model_path}")
        print("   Train the model first: python -m src.train_model")
        return None

    try:
        model = joblib.load(model_path)
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

    # Calculate Car_Age
    current_year = datetime.now().year
    car_age = current_year - year

    # Create input DataFrame
    input_df = pd.DataFrame({
        'Present_Price': [present_price],
        'Kms_Driven': [kms_driven],
        'Owner': [owner],
        'Car_Age': [car_age],
        'Fuel_Type': [fuel_type],
        'Seller_Type': [seller_type],
        'Transmission': [transmission]
    })

    try:
        prediction = model.predict(input_df)[0]
        return round(prediction, 2)
    except Exception as e:
        print(f"❌ Error making prediction: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Car Selling Price Prediction',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  python -m src.predict --present_price 7.5 --kms_driven 45000 --owner 0 --year 2016 --fuel_type Petrol --seller_type Dealer --transmission Manual"""
    )

    parser.add_argument('--present_price', type=float, required=True,
                        help='Current showroom price in Lakhs')
    parser.add_argument('--kms_driven', type=int, required=True,
                        help='Total kilometers driven')
    parser.add_argument('--owner', type=int, required=True,
                        help='Number of previous owners (0, 1, 2, 3)')
    parser.add_argument('--year', type=int, required=True,
                        help='Manufacturing year (e.g., 2016)')
    parser.add_argument('--fuel_type', type=str, required=True,
                        choices=['Petrol', 'Diesel', 'CNG'],
                        help='Fuel type: Petrol, Diesel, or CNG')
    parser.add_argument('--seller_type', type=str, required=True,
                        choices=['Dealer', 'Individual'],
                        help='Seller type: Dealer or Individual')
    parser.add_argument('--transmission', type=str, required=True,
                        choices=['Manual', 'Automatic'],
                        help='Transmission type: Manual or Automatic')

    args = parser.parse_args()

    # Validate year
    current_year = datetime.now().year
    if args.year > current_year or args.year < 1990:
        print(f"❌ Error: Year must be between 1990 and {current_year}")
        return

    # Validate present_price
    if args.present_price <= 0:
        print("❌ Error: Present price must be positive")
        return

    # Display input
    print("\n" + "=" * 60)
    print("CAR SELLING PRICE PREDICTION")
    print("=" * 60)
    print(f"\n📋 Input Details:")
    print(f"   Present Price: ₹{args.present_price} Lakhs")
    print(f"   Kms Driven:    {args.kms_driven:,} km")
    print(f"   Previous Owners: {args.owner}")
    print(f"   Year:          {args.year} (Age: {current_year - args.year} years)")
    print(f"   Fuel Type:     {args.fuel_type}")
    print(f"   Seller Type:   {args.seller_type}")
    print(f"   Transmission:  {args.transmission}")

    # Predict
    prediction = predict_price(
        args.present_price, args.kms_driven, args.owner,
        args.year, args.fuel_type, args.seller_type, args.transmission
    )

    if prediction is not None:
        print(f"\n💰 Predicted Selling Price: {prediction} Lakhs")
    else:
        print("\n❌ Prediction failed.")


if __name__ == "__main__":
    main()
