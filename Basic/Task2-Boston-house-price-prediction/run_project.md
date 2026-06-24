# 🚀 Run Project Guide — Step by Step

A beginner-friendly guide to set up and run the **Boston House Price Prediction** project on Windows.

---

## Step 1: Open CMD in the Project Folder

1. Open File Explorer
2. Navigate to the `Boston-House-Price-Prediction` folder
3. Click in the address bar, type `cmd`, and press Enter

OR:

1. Open Command Prompt
2. Navigate to the project folder:

```cmd
cd path\to\Boston-House-Price-Prediction
```

---

## Step 2: Create a Virtual Environment

A virtual environment keeps your project dependencies isolated from other Python projects.

```cmd
python -m venv venv
```

> This creates a `venv` folder in your project directory.

---

## Step 3: Activate the Virtual Environment (Windows)

```cmd
venv\Scripts\activate
```

You should see `(venv)` appear at the beginning of your command prompt.

> **macOS/Linux:**
> ```bash
> source venv/bin/activate
> ```

To deactivate later:
```cmd
deactivate
```

---

## Step 4: Install Requirements

Make sure your virtual environment is active (you see `(venv)`), then run:

```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- pandas
- numpy
- scikit-learn
- matplotlib
- seaborn
- joblib
- streamlit

> ⏳ This may take 1-2 minutes depending on your internet speed.

---

## Step 5: Place `HousingData.csv` in the `data/` Folder

1. Download or obtain `HousingData.csv`
2. Place it in the `data/` folder inside the project
3. The full path should be: `Boston-House-Price-Prediction/data/HousingData.csv`

The CSV file must have 14 columns: CRIM, ZN, INDUS, CHAS, NOX, RM, AGE, DIS, RAD, TAX, PTRATIO, B, LSTAT, MEDV

---

## Step 6: Train the Model

```cmd
python -m src.train_model
```

**OR:**

```cmd
python src/train_model.py
```

**Expected Output:**

```
=================================================================
   BOSTON HOUSE PRICE PREDICTION - MODEL TRAINING
=================================================================

📂 Step 1: Loading dataset...
✅ Dataset loaded successfully: 506 rows, 14 columns
   Columns: ['CRIM', 'ZN', ..., 'MEDV']
   Target column: 'MEDV'
   ⚠️  Missing values found:
       CRIM: 20 missing values
       ZN: 20 missing values
       ...
   → Will be handled with median imputation.

📋 Step 2: Splitting features and target...
✅ Features shape: (506, 13), Target shape: (506,)

✂️  Step 3: Train-test split...
✅ Train-test split complete:
   Training samples: 404
   Testing samples:  102

🔧 Step 4: Creating preprocessing pipeline...
✅ Preprocessing pipeline created:
   Step 1: SimpleImputer(strategy='median')
   Step 2: StandardScaler()

   🏋️  TRAINING & EVALUATING MODELS

  📊 Linear Regression:
     MAE:       3.19
     MSE:       23.30
     RMSE:      4.83
     R2 Score:  0.68

  📊 Gradient Boosting:
     MAE:       2.04
     MSE:       9.87
     RMSE:      3.14
     R2 Score:  0.87

=================================================================
  🏆 BEST MODEL: Gradient Boosting
     R2 Score:  0.8650
     RMSE:      3.14
=================================================================

✅ Best model pipeline saved to: models/best_model.pkl
✅ Model comparison saved to: outputs/model_comparison.csv
✅ Metrics saved to: outputs/metrics.json
```

---

## Step 7: Evaluate the Model and Generate Plots

```cmd
python -m src.evaluate_model
```

**OR:**

```cmd
python src/evaluate_model.py
```

This will generate 3 plots in `outputs/plots/`:
- `actual_vs_predicted.png` — Scatter plot of actual vs predicted prices
- `residuals_plot.png` — Residuals distribution
- `feature_importance.png` — Feature importance bar chart

---

## Step 8: Test Prediction (Command Line)

```cmd
python -m src.predict --CRIM 0.00632 --ZN 18 --INDUS 2.31 --CHAS 0 --NOX 0.538 --RM 6.575 --AGE 65.2 --DIS 4.09 --RAD 1 --TAX 296 --PTRATIO 15.3 --B 396.9 --LSTAT 4.98
```

**Expected Output:**

```
=======================================================
   🏠 BOSTON HOUSE PRICE PREDICTION
=======================================================
   Feature         Value
-------------------------------------------------------
   CRIM          0.0063
   ZN           18.0000
   ...
-------------------------------------------------------
   💰 Predicted Price: 28.54
   (Median value in $1,000's)
=======================================================
```

---

## Step 9: Run the Streamlit App

```cmd
streamlit run app/streamlit_app.py
```

**OR:**

```cmd
python -m streamlit run app/streamlit_app.py
```

This will open a web browser with an interactive prediction interface where you can:
- Adjust feature values using number inputs
- Click "Predict House Price"
- See the predicted price instantly

---

## 🔧 Troubleshooting

### ❌ `ModuleNotFoundError: No module named 'src'`

**Fix:**
- Make sure you are running the command from the **project root folder**
- Use `python -m src.train_model` (recommended) instead of `python src/train_model.py`
- The scripts include `sys.path` handling, so this should work either way

---

### ❌ `FileNotFoundError: HousingData.csv not found`

**Fix:**
- Make sure `HousingData.csv` is placed in the `data/` folder
- The file path should be: `Boston-House-Price-Prediction/data/HousingData.csv`
- Check the file name is exactly `HousingData.csv` (not `housingdata.csv` or `HousingData (1).csv`)

---

### ❌ `FileNotFoundError: best_model.pkl not found`

**Fix:**
- You need to train the model first
- Run: `python -m src.train_model`
- Then try your command again
- The model file is saved to `models/best_model.pkl`

---

### ❌ `'streamlit' is not recognized as an internal or external command`

**Fix:**
- Make sure your virtual environment is activated (you see `(venv)`)
- Try: `python -m streamlit run app/streamlit_app.py`
- Or reinstall: `pip install streamlit`

---

### ❌ Running from the wrong folder

**Fix:**
- Make sure you are in the project root folder
- You should see `src/`, `app/`, `data/` folders when you type `dir`
- If not, navigate to the correct folder:
  ```cmd
  cd path\to\Boston-House-Price-Prediction
  ```

---

### ❌ `ModuleNotFoundError: No module named 'sklearn'`

**Fix:**
- Activate your virtual environment: `venv\Scripts\activate`
- Install requirements: `pip install -r requirements.txt`
- Verify: `python -c "import sklearn; print(sklearn.__version__)"`

---

### ❌ Python not found

**Fix:**
- Install Python 3.8 or higher from [python.org](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"
- Try using `python3` instead of `python` if needed

---

**Happy Learning! 🎉**
