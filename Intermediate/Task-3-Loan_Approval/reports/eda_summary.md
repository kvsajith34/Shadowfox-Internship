# EDA Summary — Loan Approval Prediction

## Dataset
- File: `data/loan_prediction.csv`
- Target: `Loan_Status` (Y = Approved, N = Rejected)
- Identifier dropped: `Loan_ID`

## Structure
- ~614 rows, 13 columns (typical for this dataset).
- Mixed categorical and numeric features.

## Missing Values (typical)
| Column | Strategy |
|---|---|
| Gender, Married, Dependents, Self_Employed | Mode (most frequent) |
| LoanAmount, Loan_Amount_Term | Median |
| Credit_History | Median (treated as important numeric flag) |

## Key Findings
- **Credit_History** is the strongest predictor: applicants with credit history (1.0) are approved far more often.
- **Property_Area = Semiurban** shows higher approval rates.
- **Education = Graduate** correlates with slightly higher approval.
- Income features are right-skewed.

## IQR Outlier Analysis
For each of `ApplicantIncome`, `CoapplicantIncome`, `LoanAmount`:
- Q1 = 25th percentile, Q3 = 75th percentile, IQR = Q3 − Q1
- Lower bound = Q1 − 1.5·IQR, Upper bound = Q3 + 1.5·IQR

**Decision:** Outliers were **retained**, not deleted. They represent real high-income applicants/large loans. StandardScaler mitigates their effect for scale-sensitive models (Logistic Regression, SVM, KNN), while tree-based models are naturally robust.

## Class Balance
The target is moderately imbalanced (more approvals than rejections). We use **stratified** train/test split and prioritize **F1-score** over raw accuracy.