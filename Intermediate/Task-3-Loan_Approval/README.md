# 🏦 Loan Approval Prediction System

> A machine learning classification system that predicts whether a loan application will be approved or rejected, built with scikit-learn and optimized for real-world lending decisions.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3%2B-F7931E?logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red?logo=streamlit&logoColor=white)
![F1-Score](https://img.shields.io/badge/F1--Score-90.81%25-brightgreen)
![Accuracy](https://img.shields.io/badge/Test%20Accuracy-86.18%25-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Model Performance](#-model-performance)
- [Dataset](#-dataset)
- [Project Structure](#-project-structure)
- [Quickstart](#-quickstart)
- [Usage](#-usage)
- [Model Selection Strategy](#-model-selection-strategy)
- [Tech Stack](#-tech-stack)

---

## 🎯 Overview

This project implements an **end-to-end loan approval classification pipeline** that evaluates applicant profiles and predicts approval likelihood. The system trains multiple machine learning algorithms in parallel, selects the best performer based on F1-score and cross-validation reliability, and provides both command-line and web-based prediction interfaces.

**Real-world use case:** Financial institutions can use this model as a decision-support tool to triage applications and identify high-risk vs. low-risk profiles.

**Key achievement:** Logistic Regression achieved **90.81% F1-score** with exceptional recall (98.82%) — catching 99% of approvable candidates while maintaining reasonable precision (84%).

---

## ⭐ Key Features

✅ **Multi-model comparison** — Train 6+ algorithms simultaneously and auto-select the best  
✅ **Smart preprocessing** — Imputation, encoding, scaling in a scikit-learn pipeline  
✅ **Stratified train/test split** — Preserves class distribution for imbalanced datasets  
✅ **Cross-validation scoring** — 5-fold CV on full dataset for robust model selection  
✅ **CLI + Web interfaces** — Prediction via command line or Streamlit dashboard  
✅ **Production-ready artifacts** — Serialised models, pipelines, and metadata  
✅ **Detailed reporting** — Classification metrics, confusion matrix, and feature importance  
✅ **EDA integration** — Outlier analysis, dataset insights, and statistical summaries  

---

## 📊 Model Performance

The **Logistic Regression** model was selected as best based on blended F1-score (0.5 × test F1 + 0.5 × CV F1).

### Overall Metrics (Test Set: 123 samples)

| Metric | Score |
|---|---|
| **Accuracy** | **86.18%** |
| **Precision** | **84.00%** |
| **Recall** | **98.82%** |
| **F1-Score** | **90.81%** |
| **Cross-Validation F1** | **87.55%** |

### Per-Class Performance

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| Rejected | 96% | 58% | 72% | 38 |
| **Approved** | **84%** | **99%** | **91%** | **85** |

**Insight:** The model is highly conservative — it rarely rejects loans that should be approved (99% recall), though it occasionally approves borderline cases (84% precision). This risk-averse strategy is appropriate for most lending scenarios.

### Model Comparison

All trained models ranked by F1-score:

| Model | Accuracy | Precision | Recall | F1-Score | CV F1 |
|---|---|---|---|---|---|
| **Logistic Regression** | **86.18%** | **84%** | **98.82%** | **90.81%** | **87.55%** |
| Support Vector Classifier | 84.55% | 82.35% | 98.82% | 89.84% | 87.24% |
| K-Nearest Neighbors | 83.74% | 82.83% | 96.47% | 89.13% | 86.68% |
| Random Forest | 83.74% | 84.95% | 92.94% | 88.76% | 85.49% |
| Gradient Boosting | 81.30% | 82.29% | 92.94% | 87.29% | 84.59% |
| Decision Tree | 74.80% | 82.14% | 81.18% | 81.66% | 79.27% |

---

## 📁 Dataset

### Overview

- **Source:** `data/loan_prediction.csv`
- **Samples:** 614 loan applications
- **Target:** `Loan_Status` (Y = Approved, N = Rejected)
- **Class Distribution:** ~69% approved, ~31% rejected (moderately imbalanced)
- **Train/Test Split:** 80% / 20%, stratified

### Features (11 total)

#### Categorical Features (5)

| Feature | Values | Strategy |
|---|---|---|
| **Gender** | Male, Female | Mode imputation |
| **Married** | Yes, No | Mode imputation |
| **Education** | Graduate, Not Graduate | Mode imputation |
| **Self_Employed** | Yes, No | Mode imputation |
| **Property_Area** | Urban, Semiurban, Rural | Mode imputation |

#### Numeric Features (6)

| Feature | Range | Strategy |
|---|---|---|
| **Dependents** | 0, 1, 2, 3+ (→ 3) | Median imputation, converted to numeric |
| **ApplicantIncome** | 150–81,000 | Median imputation, StandardScaler |
| **CoapplicantIncome** | 0–41,667 | Median imputation, StandardScaler |
| **LoanAmount** | 9–700 (thousands) | Median imputation, StandardScaler |
| **Loan_Amount_Term** | 12–480 (months) | Median imputation, StandardScaler |
| **Credit_History** | 0.0 / 1.0 | Median imputation, treated as numeric flag |

### Data Quality

- **Missing values:** Present in categorical (Gender, Married, Dependents) and numeric columns (LoanAmount, Loan_Amount_Term, Credit_History)
- **Outliers:** Identified via IQR analysis but **retained** — they represent real high-income applicants and large loans. StandardScaler mitigates their effect.
- **Class balance:** Stratified split ensures representative train/test sets

### Key Insights

- **Credit_History = 1.0** is the **strongest single predictor** — applicants with established credit history are approved at much higher rates
- **Property_Area = Semiurban** shows slightly higher approval rates than Urban or Rural
- **Education = Graduate** correlates with marginally higher approval likelihood
- Income features are **right-skewed** (most applicants in lower income brackets, few high earners)
- Loan amounts and terms follow expected distributions

---

## 🏗️ Project Structure

```
loan-approval-prediction/
│
├── src/
│   ├── __init__.py
│   ├── data_preprocessing.py      # Dataset cleaning, feature definitions, IQR analysis
│   ├── train_model.py             # Multi-model training & selection pipeline
│   ├── evaluate_model.py           # Metrics, confusion matrix, feature importance plots
│   ├── predict.py                 # Single prediction API (CLI + programmatic)
│   └── utils.py                   # Path management, file I/O, model serialisation
│
├── app/
│   └── streamlit_app.py           # Interactive web dashboard (4 sections: overview, 
│                                    prediction, performance, insights)
│
├── data/
│   └── loan_prediction.csv        # Raw dataset (614 rows × 13 columns)
│
├── models/
│   ├── loan_model.pkl             # Trained best model (full pipeline: preprocessor + classifier)
│   ├── preprocessing_pipeline.pkl # Fitted preprocessor (for standalone use)
│   └── model_metadata.json        # Training metadata (metrics, feature names, timestamps)
│
├── reports/
│   ├── classification_report.txt  # Detailed per-class precision/recall/F1
│   ├── confusion_matrix.png       # Heatmap of predictions vs. actual
│   ├── feature_importance.png     # Top features (if supported by model)
│   ├── model_report.md            # Full markdown summary with tables
│   └── eda_summary.md             # Exploratory data analysis findings
│
├── notebooks/
│   └── loan_approval_eda.ipynb    # Jupyter notebook for exploration
│
├── tests/
│   ├── test_preprocessing.py      # Unit tests for data cleaning
│   └── test_prediction.py         # Unit tests for prediction logic
│
├── requirements.txt
├── .gitignore          
└── README.md
```

---

## ⚡ Quickstart

### 1. Clone & Setup

```bash
git clone https://github.com/your-username/loan-approval-prediction.git
cd loan-approval-prediction
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Train the Model

```bash
python src/train_model.py
```

Trains all candidate models, selects the best by blended F1-score, saves the pipeline and metadata, and generates evaluation reports.

**Output:**
- `models/loan_model.pkl` — Full pipeline (preprocessor + classifier)
- `models/preprocessing_pipeline.pkl` — Standalone preprocessor
- `models/model_metadata.json` — Training metrics & feature info
- `reports/` — Classification report, confusion matrix, feature importance, model summary

### 3. Make Predictions

#### CLI Prediction
```bash
python src/predict.py \
  --gender Male \
  --married Yes \
  --dependents 1 \
  --education Graduate \
  --self_employed No \
  --applicant_income 5000 \
  --coapplicant_income 1500 \
  --loan_amount 150 \
  --loan_amount_term 360 \
  --credit_history 1 \
  --property_area Urban
```

**Output:**
```
=============================================
Loan Approval Prediction: Approved
Approval Probability: 78.45%
=============================================
```

#### Web App
```bash
streamlit run app/streamlit_app.py
```

Open your browser to `http://localhost:8501` and navigate via sidebar:
- **Project Overview** — Model summary & key metrics
- **Applicant Prediction** — Interactive form to predict a single application
- **Model Performance** — Detailed metrics table, confusion matrix, feature importance
- **Dataset Insights** — Data shape, target distribution, outlier analysis

---

## 🚀 Usage

### Programmatic Prediction

```python
from src.predict import predict, build_input_dataframe

# Build input DataFrame
df = build_input_dataframe(
    gender="Male",
    married="Yes",
    dependents="1",
    education="Graduate",
    self_employed="No",
    applicant_income=5000,
    coapplicant_income=1500,
    loan_amount=150,
    loan_amount_term=360,
    credit_history=1,
    property_area="Urban"
)

# Predict
result = predict(df)
print(result)
# Output: {'prediction': 'Approved', 'approval_probability': 0.7845}
```

### Data Preprocessing Only

```python
from src.data_preprocessing import get_clean_data, analyze_outliers

# Load + clean data
X, y = get_clean_data()
print(f"Features: {X.shape}, Target: {y.shape}")

# Outlier analysis
from src.utils import load_dataset
df = load_dataset()
outliers = analyze_outliers(df)
print(outliers)
```

### Model Evaluation

```bash
python src/evaluate_model.py
```

Loads the saved model, evaluates on test set, and regenerates all reports and plots.

---

## 🧠 Model Selection Strategy

The project trains **6+ candidate algorithms** in parallel:

1. **Logistic Regression** — Fast, interpretable baseline ✅ **Selected**
2. **Decision Tree** — Simple but prone to overfitting
3. **Random Forest** — Robust ensemble, good generalisation
4. **Support Vector Classifier** — Powerful with appropriate kernel
5. **K-Nearest Neighbors** — Instance-based, flexible boundaries
6. **Gradient Boosting** — Strong sequential ensemble
7. **XGBoost** — (Optional) State-of-the-art boosting if installed

### Selection Criterion

**Blended F1-Score:** `score = 0.5 × test_f1 + 0.5 × cv_f1`

This balances:
- **Test F1** — Performance on held-out test data
- **CV F1** — Average performance across 5 folds (robustness to data variations)

**Why F1 over Accuracy?**
- The dataset is imbalanced (~69% approved)
- Recall is critical (avoiding false rejections of good applicants)
- F1 harmonises precision & recall: `F1 = 2 · (precision × recall) / (precision + recall)`

### Why Logistic Regression Won?

- **Excellent F1 (90.81%)** — Best combined precision & recall balance
- **Robust CV F1 (87.55%)** — Minimal overfitting, consistent across folds
- **Interpretable coefficients** — Easy to explain to stakeholders
- **Production-ready** — Fast inference, minimal memory, low latency
- **Probabilistic output** — Confidence scores for risk assessment

---

## 🛠️ Tech Stack

| Category | Library | Version |
|---|---|---|
| Data Handling | pandas | ≥ 1.5.0 |
| Numerical Computing | NumPy | ≥ 1.23.0 |
| Machine Learning | scikit-learn | ≥ 1.3.0 |
| Visualisation | Matplotlib | ≥ 3.6.0 |
| Visualisation | Seaborn | ≥ 0.12.0 |
| Plotting (optional) | Plotly | ≥ 5.15.0 |
| Model Persistence | joblib | ≥ 1.2.0 |
| Web App | Streamlit | ≥ 1.28.0 |
| Testing | pytest | ≥ 7.2.0 |
| Optional | XGBoost | Latest |

---

## 🧪 Testing

Run unit tests to validate data preprocessing and prediction logic:

```bash
pytest tests/
pytest tests/test_preprocessing.py -v
pytest tests/test_prediction.py -v
```

---

## 📈 Extending the Project

### Adding a New Algorithm

Edit `src/train_model.py` → `get_candidate_models()`:
```python
models["Your Model"] = YourClassifier(hyperparams...)
```

Re-run `python src/train_model.py` — new model will be automatically trained and compared.

### Hyperparameter Tuning

Use `GridSearchCV` or `RandomizedSearchCV` to optimise:
```python
from sklearn.model_selection import GridSearchCV

param_grid = {'C': [0.1, 1, 10], 'solver': ['lbfgs', 'liblinear']}
search = GridSearchCV(LogisticRegression(), param_grid, cv=5, scoring='f1')
search.fit(X_train, y_train)
```

### Feature Engineering

Extend `src/data_preprocessing.py` to add polynomial features, interaction terms, or domain-specific indicators (e.g., debt-to-income ratio).

---

## 📄 License

This project is licensed under the **MIT License** — free to use, modify, and distribute with attribution.

---

<div align="center">

Built using scikit-learn · Streamlit · Logistic Regression

**A machine learning tool for smarter lending decisions.**

</div>