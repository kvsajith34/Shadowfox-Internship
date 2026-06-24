from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.analysis import run_full_analysis
from src.data_cleaning import clean_store_data, save_cleaned_data
from src.data_loader import load_superstore_data
from src.visualizations import build_figures


st.set_page_config(page_title="Store Sales and Profit Dashboard", layout="wide")


@st.cache_data
def get_clean_data():
    data_path = PROJECT_ROOT / "data" / "Sample - Superstore.csv"
    cleaned_path = PROJECT_ROOT / "outputs" / "cleaned_data" / "cleaned_superstore.csv"

    raw_df = load_superstore_data(data_path)
    clean_df, cleaning_summary = clean_store_data(raw_df)
    save_cleaned_data(clean_df, cleaned_path)
    return clean_df, cleaning_summary


def apply_filters(df):
    st.sidebar.header("Filters")

    years = sorted([int(y) for y in df["Order Year"].dropna().unique()]) if "Order Year" in df.columns else []
    selected_years = st.sidebar.multiselect("Year", years, default=years)

    regions = sorted(df["Region"].dropna().unique().tolist()) if "Region" in df.columns else []
    selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

    categories = sorted(df["Category"].dropna().unique().tolist()) if "Category" in df.columns else []
    selected_categories = st.sidebar.multiselect("Category", categories, default=categories)

    segments = sorted(df["Segment"].dropna().unique().tolist()) if "Segment" in df.columns else []
    selected_segments = st.sidebar.multiselect("Segment", segments, default=segments)

    ship_modes = sorted(df["Ship Mode"].dropna().unique().tolist()) if "Ship Mode" in df.columns else []
    selected_ship_modes = st.sidebar.multiselect("Ship Mode", ship_modes, default=ship_modes)

    filtered_df = df.copy()
    if selected_years and "Order Year" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Order Year"].isin(selected_years)]
    if selected_regions and "Region" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Region"].isin(selected_regions)]
    if selected_categories and "Category" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]
    if selected_segments and "Segment" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Segment"].isin(selected_segments)]
    if selected_ship_modes and "Ship Mode" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Ship Mode"].isin(selected_ship_modes)]

    return filtered_df


def render_overview(analysis):
    st.subheader("Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Sales", f"${analysis['total_sales']:,.2f}")
    col2.metric("Total Profit", f"${analysis['total_profit']:,.2f}")
    col3.metric("Total Orders", f"{analysis['total_orders']:,}")
    col4.metric("Avg Profit Margin", f"{analysis['avg_profit_margin']:.2f}%")
    col5.metric("Total Quantity", f"{analysis['total_quantity']:,}")


def main():
    st.title("Store Sales and Profit Analysis Dashboard")
    st.caption("Interactive retail performance dashboard built with Streamlit, Plotly, and Pandas.")

    df, cleaning_summary = get_clean_data()
    filtered_df = apply_filters(df)

    if filtered_df.empty:
        st.warning("No data available for the selected filters. Please adjust the filter values.")
        return

    analysis = run_full_analysis(filtered_df)
    figures = build_figures(analysis, filtered_df)

    render_overview(analysis)

    st.markdown("---")
    st.header("Sales Analysis")
    st.plotly_chart(figures["monthly_sales_trend"], use_container_width=True)
    col1, col2 = st.columns(2)
    col1.plotly_chart(figures["category_sales"], use_container_width=True)
    col2.plotly_chart(figures["region_sales_profit"], use_container_width=True)
    st.plotly_chart(figures["subcategory_sales_profit"], use_container_width=True)

    st.markdown("---")
    st.header("Profit Analysis")
    st.plotly_chart(figures["monthly_profit_trend"], use_container_width=True)
    col3, col4 = st.columns(2)
    col3.plotly_chart(figures["category_profit"], use_container_width=True)
    col4.plotly_chart(figures["profit_margin_by_category"], use_container_width=True)
    col5, col6 = st.columns(2)
    col5.plotly_chart(figures["top_profitable_products"], use_container_width=True)
    col6.plotly_chart(figures["top_loss_products"], use_container_width=True)

    st.markdown("---")
    st.header("Discount Impact")
    st.plotly_chart(figures["discount_vs_profit"], use_container_width=True)
    if not analysis["profit_by_discount_level"].empty:
        st.dataframe(analysis["profit_by_discount_level"], use_container_width=True)
    st.subheader("High Discount Loss Areas")
    st.dataframe(analysis["high_discount_loss_subcategories"].head(10), use_container_width=True)

    st.markdown("---")
    st.header("Operational Insights")
    col7, col8 = st.columns(2)
    col7.plotly_chart(figures["ship_mode_performance"], use_container_width=True)
    col8.plotly_chart(figures["segment_profitability"], use_container_width=True)
    st.plotly_chart(figures["state_sales_profit"], use_container_width=True)

    if "Shipping Days" in filtered_df.columns:
        ship_delay_fig = px.histogram(
            filtered_df,
            x="Shipping Days",
            nbins=20,
            title="Shipping Days Distribution",
            template="plotly_white",
        )
        st.plotly_chart(ship_delay_fig, use_container_width=True)

    st.markdown("---")
    st.header("Final Business Recommendations")
    for idx, rec in enumerate(analysis["recommendations"], start=1):
        st.write(f"{idx}. {rec}")

    with st.expander("Data Cleaning Summary"):
        st.json(cleaning_summary)


if __name__ == "__main__":
    main()
