# 🏠 Boston House Price Prediction

**A comprehensive Machine Learning regression project** that demonstrates end-to-end model development using the classic Boston Housing dataset.

---

## 📋 Project Overview

This project builds and compares multiple regression models to predict the median value of owner-occupied homes in Boston suburbs. It features a complete ML pipeline — including data preprocessing, model training, evaluation, visualization, and deployment-ready components such as a command-line interface and an interactive Streamlit web application.

The project is designed to be clean, well-documented, and portfolio-ready for internships and entry-level Machine Learning roles.

---

## 🎯 Problem Statement

Given 13 features describing various aspects of Boston suburbs (crime rate, number of rooms, accessibility to highways, etc.), predict the **median value of owner-occupied homes (MEDV)** in $1,000s.

---

## 📊 Dataset Description

- **Source**: UCI Machine Learning Repository (via scikit-learn)
- **Rows**: 506
- **Columns**: 14 (13 features + 1 target)
- **Target Variable**: `MEDV` — Median value of owner-occupied homes in $1,000s

### Feature Columns

| Column   | Description                                                      | Type        |
|----------|------------------------------------------------------------------|-------------|
| CRIM     | Per capita crime rate by town                                    | Continuous  |
| ZN       | Proportion of residential land zoned for lots over 25,000 sq.ft. | Continuous  |
| INDUS    | Proportion of non-retail business acres per town                 | Continuous  |
| CHAS     | Charles River dummy variable (1 if tract bounds river)           | Binary      |
| NOX      | Nitric oxides concentration (parts per 10 million)               | Continuous  |
| RM       | Average number of rooms per dwelling                             | Continuous  |
| AGE      | Proportion of units built prior to 1940                          | Continuous  |
| DIS      | Weighted distances to five Boston employment centers             | Continuous  |
| RAD      | Index of accessibility to radial highways                        | Integer     |
| TAX      | Full-value property-tax rate per $10,000                         | Continuous  |
| PTRATIO  | Pupil-teacher ratio by town                                      | Continuous  |
| B        | 1000(Bk - 0.63)² where Bk is the proportion of Black residents   | Continuous  |
| LSTAT    | % lower status of the population                                 | Continuous  |

**Target**: `MEDV` (Continuous)

---

## 🔧 Data Preprocessing

- **Missing Values**: Present in `CRIM`, `ZN`, `INDUS`, `CHAS`, `AGE`, and `LSTAT`. Handled using **median imputation** via `SimpleImputer`.
- **Pipeline**: All preprocessing steps are integrated into scikit-learn Pipelines to prevent data leakage.
- **Train-Test Split**: 80/20 split with `random_state=42`.

---

## 🔄 ML Workflow

1. Load and explore the dataset
2. Handle missing values using median imputation
3. Split features and target
4. Build preprocessing + model pipelines
5. Train five regression models
6. Perform 5-fold cross-validation
7. Evaluate using MAE, MSE, RMSE, and R²
8. Select the best model based on highest R² and lowest RMSE
9. Save the complete pipeline (preprocessing + model) as a `.pkl` file
10. Generate evaluation visualizations
11. Support CLI predictions and Streamlit web interface

---

## 🤖 Models Trained

- **Linear Regression** (Baseline)
- **Ridge Regression** (L2 Regularization)
- **Decision Tree Regressor**
- **Random Forest Regressor**
- **Gradient Boosting Regressor**

---

## 📈 Model Performance

| Model                        | MAE     | MSE      | RMSE    | R² Score | CV R² Mean |
|-----------------------------|---------|----------|---------|----------|------------|
| Linear Regression           | 3.1476 | 24.9834 | 4.9983 | 0.6593  | 0.7135    |
| Ridge Regression            | 3.1446 | 24.9870 | 4.9987 | 0.6593  | 0.7136    |
| Decision Tree Regressor     | 2.7927 | 13.7519 | 3.7083 | 0.8125  | 0.6567    |
| Random Forest Regressor     | 2.1538 | 10.2137 | 3.1959 | 0.8607  | 0.8056    |
| **Gradient Boosting Regressor** | **1.8141** | **5.6252** | **2.3717** | **0.9233** | **0.8333** |

**Best Model**: **Gradient Boosting Regressor** — selected for its superior balance of accuracy and generalization.

---

## 🔮 Prediction Example

Using the best model pipeline:

```bash
python -m src.predict \
  --CRIM 0.00632 --ZN 18 --INDUS 2.31 --CHAS 0 --NOX 0.538 \
  --RM 6.575 --AGE 65.2 --DIS 4.09 --RAD 1 --TAX 296 \
  --PTRATIO 15.3 --B 396.9 --LSTAT 4.98
  Predicted Price: $25,840
  ```
## 📁 Project Structure
```
Boston-house-price-prediction/
│
├── app/
│   └── streamlit_app.py                 # Interactive web application
│
├── data/
│   ├── .gitkeep
│   └── HousingData.csv                  # Dataset
│
├── models/
│   ├── .gitkeep
│   └── best_model.pkl                   # Saved full pipeline
│
├── outputs/
│   ├── .gitkeep
│   ├── metrics.json                     # Evaluation metrics
│   ├── model_comparison.csv             # Model comparison table
│   └── plots/
│       ├── .gitkeep
│       ├── actual_vs_predicted.png
│       ├── residuals_plot.png
│       └── feature_importance.png
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── data_preprocessing.py
│   ├── train_model.py
│   ├── evaluate_model.py
│   └── predict.py
│
├── .gitignore
├── README.md
├── requirements.txt
└── run_project.md
```
## 🚀 Installation & Setup

 1. Clone the repository:

 ```Bash
 git clone https://github.com/kvsajith34/Shadow-fox-Internship
 cd Basic/Task2-Boston-house-price-prediction
 ```
 2. Create a virtual environment:

 ```Bash
 python -m venv venv
 ```
 3. Activate the virtual environment:
 
 ```Bash
 venv\Scripts\activate
 ```
 4. Install dependencies:

 ```Bash
 pip install -r requirements.txt
 ```
 --> Place HousingData.csv in the data/ folder.


 5. 🏋️ Training the Models

 ```Bash
 python -m src.train_model
 ```
 This script trains all models, performs cross-validation, selects the best model, and saves the pipeline.

 6.  📊 Evaluation & Visualization

 ```Bash
 python -m src.evaluate_model
 ```
 Generates performance metrics, comparison tables, and plots (actual vs predicted, residuals, feature importance).

 7.  🔍 Command-Line Prediction

 ```Bash
 python -m src.predict --CRIM 0.00632 --ZN 18 --INDUS 2.31 --CHAS 0 --NOX 0.538 --RM 6.575 --AGE 65.2 --DIS 4.09 --RAD 1 --TAX 296 --PTRATIO 15.3 --B 396.9 --LSTAT 4.98
 ```

 8.  🌐 Streamlit Web Application

 ```Bash
 python -m streamlit run app/streamlit_app.py
 ```
 Interactive interface for real-time price predictions with input sliders and visualization.

### 📤 Generated Output Files
```
models/best_model.pkl — Complete preprocessing + Gradient Boosting pipeline
outputs/metrics.json — Detailed evaluation metrics
outputs/model_comparison.csv — Performance comparison of all models
outputs/plots/ — Visualization charts
```
---

## 📚 Key Learnings

End-to-end ML pipeline development with scikit-learn
Proper use of Pipelines to avoid data leakage
Model comparison and automatic best-model selection
Cross-validation for robust performance estimation
Model serialization and deployment strategies
Creating user-friendly interfaces with Streamlit

---

## ⚠️ Educational Note
The Boston Housing dataset is from 1978 and contains known ethical concerns, particularly with the B feature related to demographic data. This project is for educational and portfolio purposes only and should not be used for real-world real estate decisions. Always consider fairness, bias, and ethical implications in machine learning applications.

---

## 👤 Author
Venkata Sai Ajith Kancheti

GitHub: https://github.com/kvsajith34

LinkedIn: www.linkedin.com/in/venkata-sai-ajith-kancheti
