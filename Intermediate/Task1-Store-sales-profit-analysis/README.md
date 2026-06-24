# Store Sales & Profit Analysis

A Python data analysis project that examines retail transaction data to surface profitability gaps, discount inefficiencies, and operational patterns — delivered through interactive Plotly visualizations and a multi-section Streamlit dashboard.

---

## Overview

Retail businesses frequently generate strong top-line revenue while facing compressed margins due to aggressive discounting, unfavorable product mix, and logistics overhead. This project works through those dynamics systematically: cleaning and enriching a Superstore transactions dataset, running layered analysis across time, geography, product hierarchy, and customer segment, and presenting findings in an interactive dashboard alongside an auto-generated business report.

---

## Features

- **Data pipeline** — CSV ingestion with error handling, duplicate checks, missing value treatment, and outlier flagging via winsorization (preserving business-significant transactions)
- **Feature engineering** — time-based columns, shipping delay calculation, and operational KPIs derived from raw order fields
- **Sales & profit analytics** — trend analysis across monthly, yearly, category, sub-category, region, and segment dimensions
- **Discount impact analysis** — maps discount bands to margin outcomes to identify where discounting destroys profit
- **Shipping performance** — ship mode comparison and delay distribution by region and segment
- **Interactive dashboard** — Streamlit app with sidebar filters and six analysis sections
- **Business report** — auto-generated markdown report with findings and recommendations, written to `outputs/reports/`

---

## Tech Stack

| Layer | Library |
|---|---|
| Data manipulation | Pandas, NumPy |
| Visualisation | Plotly |
| Dashboard | Streamlit |
| Reporting | Markdown (auto-generated) |
| Python | 3.10+ |

---

## Dataset

| Field | Detail |
|---|---|
| File | `Sample - Superstore.csv` |
| Expected path | `data/Sample - Superstore.csv` |
| Key columns | Order details, customer segment, geography, product hierarchy, sales, quantity, discount, profit |

---

## Project Structure

```
store-sales-profit-analysis/
│
├── data/
│   └── Sample - Superstore.csv
│
├── app/
│   └── streamlit_app.py          # Streamlit dashboard entry point
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py            # CSV ingestion with error handling
│   ├── data_cleaning.py          # Deduplication, nulls, outlier flagging
│   ├── analysis.py               # Core sales, profit, and discount analytics
│   ├── visualizations.py         # Plotly chart builders
│   └── report_generator.py       # Markdown report writer
│
├── outputs/
│   ├── charts/                   # Exported Plotly figures
│   ├── reports/                  # Generated markdown business report
│   └── cleaned_data/             # Processed dataset snapshots
│
├── notebooks/
│   └── store_sales_profit_analysis.ipynb
│
├── main.py                       # CLI entry point for full pipeline
├── requirements.txt
├── run_project.md                # Step-by-step setup guide
└── README.md
```

---

## Key Analyses

- Monthly and yearly sales and profit trends
- Category and sub-category revenue and margin contribution
- Region and customer segment performance comparison
- Top profitable products vs. highest loss-making products
- Discount band analysis — profit margin by discount level
- Ship mode performance and shipping delay distribution
- Weak-spot identification — high sales volume with low or negative margins

---

## Getting Started

**1. Clone or extract the project**

```bash
cd store-sales-profit-analysis
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Add the dataset**

Place `Sample - Superstore.csv` in the `data/` directory.

**5. Run the full analysis pipeline**

```bash
python main.py
```

**6. Launch the dashboard**

```bash
streamlit run app/streamlit_app.py
```

> For a detailed walkthrough of Windows-specific commands, see `run_project.md`.

---

## Dashboard Sections

| Section | Content |
|---|---|
| Overview | KPI summary cards — total sales, profit, orders, and average discount |
| Sales Analysis | Trend charts and category/region breakdowns |
| Profit Analysis | Margin trends, top and bottom performers |
| Discount Impact | Profit margin vs. discount band visualisation |
| Operational Insights | Shipping delay analysis by mode, region, and segment |
| Recommendations | Data-driven action points generated from the analysis |

> Screenshots can be added to this section after running the dashboard.

---

## Business Insights

The analysis is designed to surface:

- Product and category-level profitability gaps hidden within strong revenue figures
- Discount thresholds beyond which transactions consistently generate losses
- Logistics patterns correlated with weaker profit margins
- Segment and geography combinations with higher return potential

---

## Future Improvements

- Sales and profit forecasting using time-series models
- Customer cohort behaviour and retention analysis
- Automated PDF report export
- Anomaly detection alerts for sudden margin drops

---

## Author

Portfolio analysis project — internship submission.
