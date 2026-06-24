from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pandas as pd


def _fmt_currency(value: float) -> str:
    return f"${value:,.2f}"


def _df_to_markdown(df: pd.DataFrame, max_rows: int = 5) -> str:
    if df.empty:
        return "No data available."
    return df.head(max_rows).to_markdown(index=False)


def generate_markdown_report(
    analysis: Dict[str, object],
    cleaning_summary: Dict[str, object],
    output_path: Path,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    recommendations: List[str] = analysis.get("recommendations", [])

    report = f"""# Store Sales and Profit Analysis using Python

## Dataset Overview
- Records before cleaning: {cleaning_summary['original_shape'][0]}
- Columns before cleaning: {cleaning_summary['original_shape'][1]}
- Records after cleaning: {cleaning_summary['cleaned_shape'][0]}
- Columns after cleaning: {cleaning_summary['cleaned_shape'][1]}

## Data Cleaning Summary
- Duplicate rows removed: {cleaning_summary['duplicate_rows_removed']}
- Total rows removed: {cleaning_summary['rows_removed']}
- Outlier flags: {cleaning_summary['outlier_flags']}

## Key Sales Insights
- Total Sales: {_fmt_currency(analysis['total_sales'])}
- Total Orders: {analysis['total_orders']}
- Total Quantity Sold: {analysis['total_quantity']}

Top Categories by Sales:

{_df_to_markdown(analysis['category_sales'])}

Top Products by Sales:

{_df_to_markdown(analysis['top_10_products_sales'])}

## Key Profit Insights
- Total Profit: {_fmt_currency(analysis['total_profit'])}
- Average Profit Margin: {analysis['avg_profit_margin']:.2f}%

Top Profitable Products:

{_df_to_markdown(analysis['top_10_profitable_products'])}

Top Loss-making Products:

{_df_to_markdown(analysis['top_10_loss_products'])}

## Discount Impact
Profit by Discount Level:

{_df_to_markdown(analysis['profit_by_discount_level'])}

Sub-categories affected by high discounting:

{_df_to_markdown(analysis['high_discount_loss_subcategories'])}

## Operational Insights
Ship Mode Performance:

{_df_to_markdown(analysis['ship_mode_performance'])}

High Sales but Low Margin Areas:

{_df_to_markdown(analysis['weak_sales_high_loss_areas'])}

## Business Recommendations
"""

    for idx, recommendation in enumerate(recommendations, start=1):
        report += f"\n{idx}. {recommendation}"

    report += """

## Conclusion
This project combines robust data cleaning, exploratory analysis, business insight generation, and interactive visualization for decision support in retail operations. The findings can guide pricing, discount strategy, inventory focus, and logistics optimization.
"""

    output_path.write_text(report, encoding="utf-8")
    return output_path
