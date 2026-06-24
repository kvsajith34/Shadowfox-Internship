# 🚗 Car Selling Price Prediction & Analysis

A complete, portfolio-ready Machine Learning project that predicts the **selling price** of a used car based on vehicle details and ownership-related features.

---

## 📌 Problem Statement

The goal of this project is to predict the **selling price** of a used car based on several features such as:

- **Present showroom price** — current ex-showroom price of the car
- **Kilometers driven** — total distance the car has traveled
- **Car age** — years since manufacture
- **Fuel type** — Petrol, Diesel, or CNG
- **Seller type** — Dealer or Individual
- **Transmission type** — Manual or Automatic
- **Number of previous owners**

This is a **supervised regression** problem. We train multiple regression models, compare their performance, and deploy the best model using a Streamlit web application.

---

## 📊 Dataset Description

| Column          | Type     | Description                          |
|-----------------|----------|--------------------------------------|
| Car_Name        | object   | Name/brand of the car model          |
| Year            | int64    | Year of manufacture                  |
| Selling_Price   | float64  | Selling price in Lakhs **(TARGET)**  |
| Present_Price   | float64  | Current showroom price in Lakhs      |
| Kms_Driven      | int64    | Total kilometers driven              |
| Fuel_Type       | object   | Petrol / Diesel / CNG               |
| Seller_Type     | object   | Dealer / Individual                 |
| Transmission    | object   | Manual / Automatic                  |
| Owner           | int64    | Number of previous owners           |

- **Source**: CarDekho dataset (`car.csv`)
- **Missing Values**: None
- **Duplicates**: Checked and removed if found

---

## 🔧 Features Used

| Feature         | Type        | Preprocessing               |
|-----------------|-------------|-----------------------------|
| Present_Price   | Numerical   | SimpleImputer(median) + StandardScaler |
| Kms_Driven      | Numerical   | SimpleImputer(median) + StandardScaler |
| Owner           | Numerical   | SimpleImputer(median) + StandardScaler |
| Car_Age         | Numerical   | SimpleImputer(median) + StandardScaler |
| Fuel_Type       | Categorical | SimpleImputer(most_frequent) + OneHotEncoder(drop=first) |
| Seller_Type     | Categorical | SimpleImputer(most_frequent) + OneHotEncoder(drop=first) |
| Transmission    | Categorical | SimpleImputer(most_frequent) + OneHotEncoder(drop=first) |

**Feature Engineering**:
- `Car_Age = Current_Year - Year`
- `Car_Name` is dropped (not useful for modeling)
- `Year` is dropped after creating `Car_Age`

---

## 🔄 ML Workflow

1. **Data Collection** — Load `car.csv` from `data/` folder
2. **Data Preprocessing** — Clean, remove duplicates, handle missing values
3. **Feature Engineering** — Create `Car_Age`, encode categoricals
4. **Exploratory Data Analysis** — Visualize distributions and relationships
5. **Data Splitting** — 80/20 train-test split (`random_state=42`)
6. **Model Training** — Train 4 regression models and compare
7. **Hyperparameter Tuning** — RandomizedSearchCV on Random Forest
8. **Model Evaluation** — MAE, MSE, RMSE, R² Score
9. **Model Saving** — Save Pipeline with ColumnTransformer using Joblib
10. **Deployment** — Streamlit web application for predictions

---

## 📁 Project Structure

```
car-price-prediction/
│
├── README.md                    # Project documentation
├── run_project.md               # Beginner-friendly run instructions
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── streamlit_app.py             # Streamlit web app
│
├── data/
│   └── car.csv                  # Dataset file
│
├── models/
│   └── car_price_model.pkl      # Saved model pipeline
│
├── outputs/
│   ├── plots/                   # EDA & evaluation plots
│   └── reports/                 # Model evaluation CSV
│
└── src/
    ├── __init__.py              # Package init
    ├── data_preprocessing.py    # Data loading & cleaning
    ├── eda.py                   # EDA visualization script
    ├── train_model.py           # Model training script
    ├── evaluate_model.py        # Model evaluation script
    └── predict.py               # CLI prediction script
```

---

## 🤖 Model Training

### Models Trained

| Model                  | Description                               |
|------------------------|-------------------------------------------|
| Linear Regression      | Basic linear model                        |
| Decision Tree          | Tree-based model with depth control       |
| Random Forest ⭐       | Ensemble of decision trees (best model)   |
| Gradient Boosting      | Sequential boosting ensemble              |

### Training Process

1. Data is split 80/20 (train/test) with `random_state=42`
2. A `ColumnTransformer` preprocesses numerical and categorical features
3. A `Pipeline` chains preprocessing with the model
4. All 4 models are trained and evaluated
5. `RandomizedSearchCV` tunes the Random Forest hyperparameters
6. The best pipeline is saved using `joblib`

### Hyperparameter Tuning (Random Forest)

Tuned parameters:
- `n_estimators`: [100, 200, 300, 500]
- `max_depth`: [5, 10, 15, 20, None]
- `min_samples_split`: [2, 5, 10]
- `min_samples_leaf`: [1, 2, 4]
- `max_features`: ['sqrt', 'log2', 1.0]

---

## 📏 Evaluation Metrics

| Metric | Description |
|--------|-------------|
| **MAE** (Mean Absolute Error) | Average absolute difference between actual and predicted prices |
| **MSE** (Mean Squared Error) | Average squared difference; penalizes larger errors |
| **RMSE** (Root Mean Squared Error) | Square root of MSE; same unit as target variable |
| **R² Score** | Proportion of variance explained (1.0 = perfect, 0.0 = baseline) |

Results are saved to `outputs/reports/model_evaluation.csv`.

---

## 🚀 How to Run

All commands must be run from the **project root directory**.

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# Step 1: Create virtual environment
python -m venv venv

# Step 2: Activate (Windows)
venv\Scripts\activate

# Step 3: Install dependencies
pip install -r requirements.txt

# Step 4: Ensure car.csv is in data/ folder
```

### Run EDA

```bash
python -m src.eda
```

Plots are saved to `outputs/plots/`.

### Train Model

```bash
python -m src.train_model
```

Model is saved to `models/car_price_model.pkl`.
Evaluation results saved to `outputs/reports/model_evaluation.csv`.

### Evaluate Model

```bash
python -m src.evaluate_model
```

Evaluation plots are saved to `outputs/plots/`.

### Test Prediction (CLI)

```bash
python -m src.predict --present_price 7.5 --kms_driven 45000 --owner 0 --year 2016 --fuel_type Petrol --seller_type Dealer --transmission Manual
```

Output: `Predicted Selling Price: X.XX Lakhs`

### Run Streamlit App

```bash
streamlit run streamlit_app.py
```

Open the URL shown in the terminal (usually `http://localhost:8501`).

---

## 🔮 Future Improvements

- Add more data sources for better generalization
- Implement XGBoost and LightGBM models
- Add cross-validation with more folds
- Build a FastAPI REST API
- Deploy on cloud (Streamlit Cloud, Heroku, Render)
- Add model monitoring and data drift detection
- Implement unit tests with pytest
- Create a CI/CD pipeline with GitHub Actions
- Add more features (location, brand, car condition)

---

## 👤 Author

**Venkata Sai Ajith Kancheti**

Machine Learning Engineer & Data Scientist

---

## 📄 License

This project is for educational and portfolio purposes.
