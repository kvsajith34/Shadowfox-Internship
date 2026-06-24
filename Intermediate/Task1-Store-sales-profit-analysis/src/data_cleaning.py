from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd


NUMERIC_COLUMNS = ["Sales", "Quantity", "Discount", "Profit", "Postal Code"]
DATE_COLUMNS = ["Order Date", "Ship Date"]
CATEGORICAL_FALLBACK = "Unknown"


def _discount_bucket(discount: float) -> str:
    if pd.isna(discount):
        return "Unknown"
    if discount == 0:
        return "No Discount"
    if discount <= 0.10:
        return "Low"
    if discount <= 0.30:
        return "Medium"
    return "High"


def clean_store_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, object]]:
    """Clean and enrich store data without dropping business-significant outliers."""
    clean_df = df.copy()
    clean_df.columns = [col.strip() for col in clean_df.columns]

    original_shape = clean_df.shape

    for col in DATE_COLUMNS:
        if col in clean_df.columns:
            clean_df[col] = pd.to_datetime(clean_df[col], errors="coerce")

    for col in NUMERIC_COLUMNS:
        if col in clean_df.columns:
            clean_df[col] = pd.to_numeric(clean_df[col], errors="coerce")

    missing_before = clean_df.isna().sum().to_dict()

    duplicate_rows = int(clean_df.duplicated().sum())
    if duplicate_rows > 0:
        clean_df = clean_df.drop_duplicates().copy()

    if "Order Date" in clean_df.columns:
        clean_df = clean_df.dropna(subset=["Order Date"]).copy()

    if "Ship Date" in clean_df.columns and "Order Date" in clean_df.columns:
        clean_df["Ship Date"] = clean_df["Ship Date"].fillna(clean_df["Order Date"])

    for col in clean_df.columns:
        if clean_df[col].dtype == "object":
            clean_df[col] = clean_df[col].fillna(CATEGORICAL_FALLBACK)

    for col in ["Sales", "Quantity", "Discount", "Profit"]:
        if col in clean_df.columns:
            clean_df[col] = clean_df[col].fillna(clean_df[col].median())

    outlier_summary: Dict[str, int] = {}
    for col in ["Sales", "Profit", "Quantity"]:
        if col not in clean_df.columns:
            continue
        q1 = clean_df[col].quantile(0.25)
        q3 = clean_df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        flag_column = f"{col} Outlier"
        clean_df[flag_column] = (clean_df[col] < lower) | (clean_df[col] > upper)
        outlier_summary[col] = int(clean_df[flag_column].sum())

        # Keep original values but provide clipped values for stable trend visualizations.
        clip_col = f"{col} Winsorized"
        low_clip = clean_df[col].quantile(0.01)
        high_clip = clean_df[col].quantile(0.99)
        clean_df[clip_col] = clean_df[col].clip(lower=low_clip, upper=high_clip)

    if "Order Date" in clean_df.columns:
        clean_df["Order Year"] = clean_df["Order Date"].dt.year.astype("Int64")
        clean_df["Order Month"] = clean_df["Order Date"].dt.month.astype("Int64")
        clean_df["Month Name"] = clean_df["Order Date"].dt.strftime("%B")
        clean_df["Year-Month"] = clean_df["Order Date"].dt.to_period("M").astype(str)

    if "Ship Date" in clean_df.columns and "Order Date" in clean_df.columns:
        clean_df["Shipping Days"] = (clean_df["Ship Date"] - clean_df["Order Date"]).dt.days
        clean_df["Shipping Days"] = clean_df["Shipping Days"].fillna(0)
        clean_df["Shipping Days"] = clean_df["Shipping Days"].clip(lower=0)

    if "Sales" in clean_df.columns and "Profit" in clean_df.columns:
        clean_df["Profit Margin"] = np.where(
            clean_df["Sales"] != 0,
            (clean_df["Profit"] / clean_df["Sales"]) * 100,
            np.nan,
        )

    if "Sales" in clean_df.columns and "Quantity" in clean_df.columns:
        clean_df["Sales per Quantity"] = np.where(
            clean_df["Quantity"] != 0,
            clean_df["Sales"] / clean_df["Quantity"],
            np.nan,
        )

    if "Profit" in clean_df.columns:
        clean_df["Profit Status"] = np.where(clean_df["Profit"] >= 0, "Profitable", "Loss")

    if "Discount" in clean_df.columns:
        clean_df["Discount Level"] = clean_df["Discount"].apply(_discount_bucket)

    missing_after = clean_df.isna().sum().to_dict()

    cleaning_summary: Dict[str, object] = {
        "original_shape": original_shape,
        "cleaned_shape": clean_df.shape,
        "rows_removed": int(original_shape[0] - clean_df.shape[0]),
        "duplicate_rows_removed": duplicate_rows,
        "missing_before": missing_before,
        "missing_after": missing_after,
        "outlier_flags": outlier_summary,
    }

    return clean_df, cleaning_summary


def save_cleaned_data(df: pd.DataFrame, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path
