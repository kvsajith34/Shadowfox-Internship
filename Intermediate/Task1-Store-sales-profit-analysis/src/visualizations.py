from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PLOT_THEME = "plotly_white"


def _line_chart(df: pd.DataFrame, x: str, y: str, title: str):
    if df.empty:
        return go.Figure()
    fig = px.line(df, x=x, y=y, markers=True, title=title, template=PLOT_THEME)
    fig.update_layout(xaxis_title=x, yaxis_title=y)
    return fig


def _bar_chart(df: pd.DataFrame, x: str, y: str, title: str, color: str | None = None, horizontal: bool = False):
    if df.empty:
        return go.Figure()
    if horizontal:
        fig = px.bar(df, x=y, y=x, orientation="h", color=color, title=title, template=PLOT_THEME)
    else:
        fig = px.bar(df, x=x, y=y, color=color, title=title, template=PLOT_THEME)
    return fig


def build_figures(analysis: Dict[str, object], df: pd.DataFrame) -> Dict[str, go.Figure]:
    figures: Dict[str, go.Figure] = {}

    figures["monthly_sales_trend"] = _line_chart(
        analysis["monthly_sales"], "Year-Month", "Sales", "Monthly Sales Trend"
    )
    figures["monthly_profit_trend"] = _line_chart(
        analysis["monthly_profit"], "Year-Month", "Profit", "Monthly Profit Trend"
    )
    figures["category_sales"] = _bar_chart(
        analysis["category_sales"], "Category", "Sales", "Category-wise Sales", "Category"
    )
    figures["category_profit"] = _bar_chart(
        analysis["category_profit"], "Category", "Profit", "Category-wise Profit", "Category"
    )

    sub_sales = analysis["subcategory_sales"].rename(columns={"Sales": "Value"}).copy()
    sub_sales["Metric"] = "Sales"
    sub_profit = analysis["subcategory_profit"].rename(columns={"Profit": "Value"}).copy()
    sub_profit["Metric"] = "Profit"
    sub_comp = pd.concat([sub_sales[["Sub-Category", "Value", "Metric"]], sub_profit[["Sub-Category", "Value", "Metric"]]])
    figures["subcategory_sales_profit"] = px.bar(
        sub_comp,
        x="Sub-Category",
        y="Value",
        color="Metric",
        barmode="group",
        template=PLOT_THEME,
        title="Sub-Category Sales vs Profit",
    )

    region_join = analysis["region_sales"].merge(analysis["region_profit"], on="Region", how="outer").fillna(0)
    figures["region_sales_profit"] = px.bar(
        region_join,
        x="Region",
        y=["Sales", "Profit"],
        barmode="group",
        template=PLOT_THEME,
        title="Region-wise Sales and Profit",
    )

    segment_join = analysis["segment_sales"].merge(analysis["segment_profit"], on="Segment", how="outer").fillna(0)
    figures["segment_profitability"] = px.scatter(
        segment_join,
        x="Sales",
        y="Profit",
        size="Sales",
        color="Segment",
        template=PLOT_THEME,
        title="Segment-wise Profitability",
    )

    if all(col in df.columns for col in ["Discount", "Profit", "Category"]):
        figures["discount_vs_profit"] = px.scatter(
            df,
            x="Discount",
            y="Profit",
            color="Category",
            template=PLOT_THEME,
            title="Discount vs Profit",
            opacity=0.6,
        )
    else:
        figures["discount_vs_profit"] = go.Figure()

    figures["profit_margin_by_category"] = _bar_chart(
        analysis["profit_margin_by_category"],
        "Category",
        "Profit Margin",
        "Profit Margin by Category",
        "Category",
    )

    figures["top_profitable_products"] = _bar_chart(
        analysis["top_10_profitable_products"],
        "Product Name",
        "Profit",
        "Top 10 Profitable Products",
        horizontal=True,
    )

    figures["top_loss_products"] = _bar_chart(
        analysis["top_10_loss_products"],
        "Product Name",
        "Profit",
        "Top 10 Loss-making Products",
        horizontal=True,
    )

    if all(col in df.columns for col in ["Sales", "Profit", "Profit Status"]):
        figures["sales_vs_profit"] = px.scatter(
            df,
            x="Sales",
            y="Profit",
            color="Profit Status",
            template=PLOT_THEME,
            title="Sales vs Profit",
            opacity=0.6,
        )
    else:
        figures["sales_vs_profit"] = go.Figure()

    ship_mode = analysis["ship_mode_performance"]
    figures["ship_mode_performance"] = px.bar(
        ship_mode,
        x="Ship Mode",
        y=["Sales", "Profit"],
        barmode="group",
        template=PLOT_THEME,
        title="Ship Mode Performance",
    )

    figures["state_sales_profit"] = px.bar(
        analysis["state_sales_profit"],
        x="State",
        y=["Sales", "Profit"],
        barmode="group",
        template=PLOT_THEME,
        title="Top States by Sales and Profit",
    )

    return figures


def save_figures_as_html(figures: Dict[str, go.Figure], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, fig in figures.items():
        fig.write_html(output_dir / f"{name}.html", include_plotlyjs="cdn")
