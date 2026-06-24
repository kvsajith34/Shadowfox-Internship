# 🚀 How to Run This Project

A simple, beginner-friendly guide to run the Car Selling Price Prediction project.

All commands must be run from the **project root folder**.

---

## Step 1: Install Python

Make sure **Python 3.8 or higher** is installed.

```
python --version
```

Download from: https://www.python.org/downloads/

---

## Step 2: Open Terminal

Open **Command Prompt** (cmd) or **PowerShell** in the project folder.

Tip: In File Explorer, type `cmd` in the address bar and press Enter.

---

## Step 3: Create Virtual Environment

```
python -m venv venv
```

---

## Step 4: Activate Virtual Environment

**Windows:**
```
venv\Scripts\activate
```

**Mac/Linux:**
```
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal line.

---

## Step 5: Install Dependencies

```
pip install -r requirements.txt
```

This installs: pandas, numpy, matplotlib, seaborn, scikit-learn, joblib, streamlit

---

## Step 6: Place the Dataset

Ensure `car.csv` is inside the `data/` folder.

Path: `data/car.csv`

---

## Step 7: Run EDA

```
python -m src.eda
```

This generates 8 plots in `outputs/plots/` folder.

---

## Step 8: Train the Model

```
python -m src.train_model
```

This trains all 4 models and saves the best one to `models/car_price_model.pkl`

---

## Step 9: Evaluate the Model

```
python -m src.evaluate_model
```

This generates evaluation plots in `outputs/plots/` folder.

---

## Step 10: Test Prediction from Terminal

```
python -m src.predict --present_price 7.5 --kms_driven 45000 --owner 0 --year 2016 --fuel_type Petrol --seller_type Dealer --transmission Manual
```

Expected output:
```
Predicted Selling Price: X.XX Lakhs
```

---

## Step 11: Run the Streamlit App

```
streamlit run streamlit_app.py
```

A browser window will open automatically. If not, go to:

**http://localhost:8501**

Enter car details and click **"Predict Selling Price"**!

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Make sure venv is activated and requirements installed |
| `No module named src` | Run commands from the project root folder |
| `File not found: car.csv` | Check that `car.csv` is in the `data/` folder |
| `Model not found` | Run `python -m src.train_model` first |
| `Port 8501 in use` | Streamlit will suggest a different port automatically |
| `Permission error` | Run terminal as administrator |

---

Enjoy predicting car prices! 🚗💰
