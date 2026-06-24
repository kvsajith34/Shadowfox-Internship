from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd


def _safe_group_sum(df: pd.DataFrame, group_cols: List[str], value_col: str) -> pd.DataFrame:
    if value_col not in df.columns:
        return pd.DataFrame(columns=group_cols + [value_col])
    group_df = (
        df.groupby(group_cols, dropna=False)[value_col]
        .sum()
        .reset_index()
        .sort_values(value_col, ascending=False)
    )
    return group_df


def _safe_margin(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    if "Sales" not in df.columns or "Profit" not in df.columns or group_col not in df.columns:
        return pd.DataFrame(columns=[group_col, "Sales", "Profit", "Profit Margin"])

    result = (
        df.groupby(group_col, dropna=False)[["Sales", "Profit"]]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=False)
    )
    result["Profit Margin"] = np.where(
        result["Sales"] != 0,
        (result["Profit"] / result["Sales"]) * 100,
        np.nan,
    )
    return result


def generate_recommendations(analysis: Dict[str, object]) -> List[str]:
    recommendations: List[str] = []

    category_profit = analysis.get("category_profit", pd.DataFrame())
    loss_products = analysis.get("top_10_loss_products", pd.DataFrame())
    discount_level_profit = analysis.get("profit_by_discount_level", pd.DataFrame())
    weak_areas = analysis.get("weak_sales_high_loss_areas", pd.DataFrame())
    ship_mode_profit = analysis.get("ship_mode_performance", pd.DataFrame())
    yearly_profit = analysis.get("yearly_profit", pd.DataFrame())
    segment_profit = analysis.get("segment_profit", pd.DataFrame())

    if not category_profit.empty:
        worst_cat = category_profit.sort_values("Profit", ascending=True).iloc[0]
        best_cat = category_profit.sort_values("Profit", ascending=False).iloc[0]
        recommendations.append(
            f"Prioritize profitability recovery in '{worst_cat['Category']}' while scaling successful plays from '{best_cat['Category']}'."
        )

    if not loss_products.empty:
        product_count = int((loss_products["Profit"] < 0).sum())
        recommendations.append(
            f"Review pricing and discount rules for the top {product_count} loss-making products to control recurring negative margins."
        )

    if not discount_level_profit.empty and "Discount Level" in discount_level_profit.columns:
        high_discount = discount_level_profit.loc[
            discount_level_profit["Discount Level"] == "High"
        ]
        if not high_discount.empty and high_discount["Profit"].iloc[0] < 0:
            recommendations.append(
                "Cap or re-approve high discount deals because the current high-discount bucket is eroding profit."
            )
        else:
            recommendations.append(
                "Use medium discounts as a controlled growth lever and monitor high-discount orders weekly."
            )

    if not weak_areas.empty:
        top_weak = weak_areas.iloc[0]
        recommendations.append(
            f"The '{top_weak['Sub-Category']}' sub-category has high sales but low margins; redesign sourcing or pricing there first."
        )

    if not ship_mode_profit.empty:
        worst_ship = ship_mode_profit.sort_values("Profit", ascending=True).iloc[0]
        recommendations.append(
            f"Optimize logistics for '{worst_ship['Ship Mode']}' because it contributes the weakest profit performance."
        )

    if not yearly_profit.empty and len(yearly_profit) >= 2:
        recent = yearly_profit.sort_values("Order Year").tail(2)
        latest, prev = recent.iloc[-1], recent.iloc[-2]
        if latest["Profit"] < prev["Profit"]:
            recommendations.append(
                "Profit has declined in the latest year; run a quarterly margin protection program focused on discount and freight control."
            )
        else:
            recommendations.append(
                "Latest yearly profit is improving; replicate high-margin product bundles and regional tactics from top performers."
            )

    if not segment_profit.empty:
        best_segment = segment_profit.sort_values("Profit", ascending=False).iloc[0]
        recommendations.append(
            f"Increase account-based campaigns in the '{best_segment['Segment']}' segment where profitability is strongest."
        )

    base_recommendations = [
        "Create a monthly profitability review combining discount level, ship mode, and sub-category margin in one leadership dashboard.",
        "Define an approval threshold for deep discounts on low-margin categories before order confirmation.",
        "Set alerts for high-sales low-profit combinations so corrective action happens before month-end closure.",
        "Use city and state-level opportunity mapping to focus inventory and promotions where both sales and margins are healthy.",
    ]

    for rec in base_recommendations:
        if len(recommendations) >= 12:
            break
        recommendations.append(rec)

    return recommendations[:12]


def run_full_analysis(df: pd.DataFrame) -> Dict[str, object]:
    analysis: Dict[str, object] = {}

    analysis["total_sales"] = float(df.get("Sales", pd.Series(dtype=float)).sum())
    analysis["total_profit"] = float(df.get("Profit", pd.Series(dtype=float)).sum())
    analysis["total_orders"] = int(df["Order ID"].nunique()) if "Order ID" in df.columns else int(len(df))
    analysis["total_quantity"] = int(df.get("Quantity", pd.Series(dtype=float)).sum())
    if "Profit Margin" in df.columns:
        analysis["avg_profit_margin"] = float(df["Profit Margin"].mean())
    else:
        analysis["avg_profit_margin"] = float("nan")

    if "Order Date" in df.columns and "Sales" in df.columns:
        monthly_sales = (
            df.groupby(df["Order Date"].dt.to_period("M"))["Sales"]
            .sum()
            .reset_index(name="Sales")
        )
        monthly_sales["Year-Month"] = monthly_sales["Order Date"].astype(str)
        analysis["monthly_sales"] = monthly_sales[["Year-Month", "Sales"]]
    else:
        analysis["monthly_sales"] = pd.DataFrame(columns=["Year-Month", "Sales"])

    if "Order Date" in df.columns and "Profit" in df.columns:
        monthly_profit = (
            df.groupby(df["Order Date"].dt.to_period("M"))["Profit"]
            .sum()
            .reset_index(name="Profit")
        )
        monthly_profit["Year-Month"] = monthly_profit["Order Date"].astype(str)
        analysis["monthly_profit"] = monthly_profit[["Year-Month", "Profit"]]
    else:
        analysis["monthly_profit"] = pd.DataFrame(columns=["Year-Month", "Profit"])

    analysis["yearly_sales"] = _safe_group_sum(df, ["Order Year"], "Sales") if "Order Year" in df.columns else pd.DataFrame()
    analysis["yearly_profit"] = _safe_group_sum(df, ["Order Year"], "Profit") if "Order Year" in df.columns else pd.DataFrame()

    analysis["category_sales"] = _safe_group_sum(df, ["Category"], "Sales")
    analysis["subcategory_sales"] = _safe_group_sum(df, ["Sub-Category"], "Sales")
    analysis["region_sales"] = _safe_group_sum(df, ["Region"], "Sales")
    analysis["segment_sales"] = _safe_group_sum(df, ["Segment"], "Sales")
    analysis["top_10_products_sales"] = _safe_group_sum(df, ["Product Name"], "Sales").head(10)
    analysis["top_10_states_sales"] = _safe_group_sum(df, ["State"], "Sales").head(10)
    analysis["top_10_cities_sales"] = _safe_group_sum(df, ["City"], "Sales").head(10)

    analysis["category_profit"] = _safe_group_sum(df, ["Category"], "Profit")
    analysis["subcategory_profit"] = _safe_group_sum(df, ["Sub-Category"], "Profit")
    analysis["region_profit"] = _safe_group_sum(df, ["Region"], "Profit")
    analysis["segment_profit"] = _safe_group_sum(df, ["Segment"], "Profit")
    analysis["top_10_profitable_products"] = _safe_group_sum(df, ["Product Name"], "Profit").head(10)
    analysis["top_10_loss_products"] = _safe_group_sum(df, ["Product Name"], "Profit").sort_values("Profit", ascending=True).head(10)

    analysis["profit_margin_by_category"] = _safe_margin(df, "Category")
    analysis["profit_margin_by_subcategory"] = _safe_margin(df, "Sub-Category")

    if "Sales" in df.columns and "Profit" in df.columns and "Category" in df.columns:
        ratio_df = df.groupby("Category", dropna=False)[["Sales", "Profit"]].sum().reset_index()
        ratio_df["Sales to Profit Ratio"] = np.where(
            ratio_df["Profit"] != 0,
            ratio_df["Sales"] / ratio_df["Profit"],
            np.nan,
        )
        analysis["sales_to_profit_ratio"] = ratio_df.sort_values("Sales to Profit Ratio", ascending=False)
    else:
        analysis["sales_to_profit_ratio"] = pd.DataFrame(
            columns=["Category", "Sales", "Profit", "Sales to Profit Ratio"]
        )

    analysis["profit_by_discount_level"] = _safe_group_sum(df, ["Discount Level"], "Profit")
    analysis["sales_by_discount_level"] = _safe_group_sum(df, ["Discount Level"], "Sales")

    if all(col in df.columns for col in ["Discount Level", "Sub-Category", "Sales", "Profit"]):
        high_discount_losses = (
            df[df["Discount Level"] == "High"]
            .groupby("Sub-Category", dropna=False)[["Sales", "Profit"]]
            .sum()
            .reset_index()
            .sort_values("Profit", ascending=True)
        )
        analysis["high_discount_loss_subcategories"] = high_discount_losses
    else:
        analysis["high_discount_loss_subcategories"] = pd.DataFrame(
            columns=["Sub-Category", "Sales", "Profit"]
        )

    if all(col in df.columns for col in ["Ship Mode", "Sales", "Profit", "Shipping Days"]):
        ship_mode_perf = (
            df.groupby("Ship Mode", dropna=False)[["Sales", "Profit", "Shipping Days"]]
            .agg({"Sales": "sum", "Profit": "sum", "Shipping Days": "mean"})
            .reset_index()
            .rename(columns={"Shipping Days": "Avg Shipping Days"})
            .sort_values("Profit", ascending=False)
        )
        analysis["ship_mode_performance"] = ship_mode_perf
    else:
        analysis["ship_mode_performance"] = pd.DataFrame(
            columns=["Ship Mode", "Sales", "Profit", "Avg Shipping Days"]
        )

    if all(col in df.columns for col in ["Sub-Category", "Sales", "Profit"]):
        weak_areas = (
            df.groupby("Sub-Category", dropna=False)[["Sales", "Profit"]]
            .sum()
            .reset_index()
        )
        weak_areas["Profit Margin"] = np.where(
            weak_areas["Sales"] != 0,
            (weak_areas["Profit"] / weak_areas["Sales"]) * 100,
            np.nan,
        )
        sales_cutoff = weak_areas["Sales"].quantile(0.75)
        margin_cutoff = weak_areas["Profit Margin"].quantile(0.25)
        weak_areas = weak_areas[
            (weak_areas["Sales"] >= sales_cutoff) & (weak_areas["Profit Margin"] <= margin_cutoff)
        ].sort_values("Profit Margin")
        analysis["weak_sales_high_loss_areas"] = weak_areas
    else:
        analysis["weak_sales_high_loss_areas"] = pd.DataFrame(
            columns=["Sub-Category", "Sales", "Profit", "Profit Margin"]
        )

    if all(col in df.columns for col in ["Sales", "Profit", "State"]):
        analysis["state_sales_profit"] = (
            df.groupby("State", dropna=False)[["Sales", "Profit"]]
            .sum()
            .reset_index()
            .sort_values("Sales", ascending=False)
            .head(15)
        )
    else:
        analysis["state_sales_profit"] = pd.DataFrame(columns=["State", "Sales", "Profit"])

    analysis["recommendations"] = generate_recommendations(analysis)
    return analysis
