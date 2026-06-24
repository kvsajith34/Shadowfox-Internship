"""
Exploratory Data Analysis Module
=================================
Generates and saves EDA plots to outputs/plots/

Usage (run from project root):
    python -m src.eda
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Project root directory (one level up from this file)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Plot styling
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 100
plt.rcParams['font.size'] = 11

# Output directory
PLOTS_DIR = os.path.join(PROJECT_ROOT, "outputs", "plots")


def get_data_path(filename: str = "car.csv") -> str:
    """Get the full path to a data file."""
    return os.path.join(PROJECT_ROOT, "data", filename)


def load_and_prepare_data(filepath: str = None) -> pd.DataFrame:
    """Load data and add Car_Age feature for EDA.

    Args:
        filepath: Path to car.csv. If None, uses default data/car.csv.

    Returns:
        DataFrame with Car_Age column added.
    """
    if filepath is None:
        filepath = get_data_path("car.csv")
    df = pd.read_csv(filepath)
    current_year = datetime.now().year
    df['Car_Age'] = current_year - df['Year']
    # Remove duplicates for clean analysis
    df = df.drop_duplicates().reset_index(drop=True)
    return df


# -------------------------------------------------------
# Plot 1: Selling Price Distribution
# -------------------------------------------------------
def plot_selling_price_distribution(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df['Selling_Price'], bins=25, kde=True, color='#4F46E5', ax=ax, edgecolor='white')
    ax.set_title('Distribution of Selling Price', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Selling Price (Lakhs)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.axvline(df['Selling_Price'].mean(), color='red', linestyle='--', linewidth=1.5,
               label=f'Mean: ₹{df["Selling_Price"].mean():.2f}L')
    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "01_selling_price_distribution.png"), bbox_inches='tight')
    plt.close()
    print("✅ Saved: 01_selling_price_distribution.png")


# -------------------------------------------------------
# Plot 2: Present Price vs Selling Price
# -------------------------------------------------------
def plot_present_vs_selling_price(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df, x='Present_Price', y='Selling_Price',
                    hue='Fuel_Type', palette='Set2', s=80, ax=ax, edgecolor='white', linewidth=0.5)
    ax.set_title('Selling Price vs Present Price', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Present Price (Lakhs)', fontsize=12)
    ax.set_ylabel('Selling Price (Lakhs)', fontsize=12)
    ax.legend(title='Fuel Type', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "02_present_vs_selling_price.png"), bbox_inches='tight')
    plt.close()
    print("✅ Saved: 02_present_vs_selling_price.png")


# -------------------------------------------------------
# Plot 3: Kms Driven vs Selling Price
# -------------------------------------------------------
def plot_kms_vs_selling_price(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df, x='Kms_Driven', y='Selling_Price',
                    hue='Transmission', palette='Set1', s=80, ax=ax, edgecolor='white', linewidth=0.5)
    ax.set_title('Selling Price vs Kilometers Driven', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Kilometers Driven', fontsize=12)
    ax.set_ylabel('Selling Price (Lakhs)', fontsize=12)
    ax.legend(title='Transmission', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "03_kms_vs_selling_price.png"), bbox_inches='tight')
    plt.close()
    print("✅ Saved: 03_kms_vs_selling_price.png")


# -------------------------------------------------------
# Plot 4: Car Age vs Selling Price
# -------------------------------------------------------
def plot_car_age_vs_selling_price(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    age_avg = df.groupby('Car_Age')['Selling_Price'].mean().reset_index()
    sns.barplot(data=age_avg, x='Car_Age', y='Selling_Price', color='#4F46E5', ax=ax, edgecolor='white')
    ax.set_title('Average Selling Price by Car Age', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Car Age (Years)', fontsize=12)
    ax.set_ylabel('Average Selling Price (Lakhs)', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "04_car_age_vs_selling_price.png"), bbox_inches='tight')
    plt.close()
    print("✅ Saved: 04_car_age_vs_selling_price.png")


# -------------------------------------------------------
# Plot 5: Selling Price by Fuel Type
# -------------------------------------------------------
def plot_selling_by_fuel_type(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    order = df.groupby('Fuel_Type')['Selling_Price'].median().sort_values(ascending=False).index
    sns.boxplot(data=df, x='Fuel_Type', y='Selling_Price', order=order,
                palette='Set2', ax=ax)
    ax.set_title('Selling Price by Fuel Type', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Fuel Type', fontsize=12)
    ax.set_ylabel('Selling Price (Lakhs)', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "05_selling_by_fuel_type.png"), bbox_inches='tight')
    plt.close()
    print("✅ Saved: 05_selling_by_fuel_type.png")


# -------------------------------------------------------
# Plot 6: Selling Price by Seller Type
# -------------------------------------------------------
def plot_selling_by_seller_type(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=df, x='Seller_Type', y='Selling_Price',
                palette='Set3', ax=ax)
    ax.set_title('Selling Price by Seller Type', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Seller Type', fontsize=12)
    ax.set_ylabel('Selling Price (Lakhs)', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "06_selling_by_seller_type.png"), bbox_inches='tight')
    plt.close()
    print("✅ Saved: 06_selling_by_seller_type.png")


# -------------------------------------------------------
# Plot 7: Selling Price by Transmission
# -------------------------------------------------------
def plot_selling_by_transmission(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=df, x='Transmission', y='Selling_Price',
                palette='coolwarm', ax=ax)
    ax.set_title('Selling Price by Transmission Type', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('Transmission', fontsize=12)
    ax.set_ylabel('Selling Price (Lakhs)', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "07_selling_by_transmission.png"), bbox_inches='tight')
    plt.close()
    print("✅ Saved: 07_selling_by_transmission.png")


# -------------------------------------------------------
# Plot 8: Correlation Heatmap
# -------------------------------------------------------
def plot_correlation_heatmap(df: pd.DataFrame) -> None:
    numerical_cols = ['Selling_Price', 'Present_Price', 'Kms_Driven', 'Owner', 'Car_Age']
    corr = df[numerical_cols].corr()

    fig, ax = plt.subplots(figsize=(9, 7))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, cmap='RdYlBu_r', center=0,
                fmt='.2f', square=True, linewidths=0.8, ax=ax,
                annot_kws={'fontsize': 11, 'fontweight': 'bold'})
    ax.set_title('Correlation Heatmap', fontsize=16, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "08_correlation_heatmap.png"), bbox_inches='tight')
    plt.close()
    print("✅ Saved: 08_correlation_heatmap.png")


# -------------------------------------------------------
# EDA Report
# -------------------------------------------------------
def generate_eda_report(df: pd.DataFrame) -> None:
    """Print a text summary of the dataset."""
    print("\n" + "=" * 60)
    print("EXPLORATORY DATA ANALYSIS REPORT")
    print("=" * 60)
    print(f"\n📐 Dataset Shape: {df.shape}")
    print(f"📊 Total Records: {df.shape[0]}")
    print(f"📋 Total Features: {df.shape[1]}")

    print("\n--- Missing Values ---")
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("   ✅ No missing values")
    else:
        print(missing[missing > 0].to_string())

    print("\n--- Descriptive Statistics ---")
    print(df.describe().to_string())

    print("\n--- Selling Price Statistics ---")
    print(f"   Mean:   ₹{df['Selling_Price'].mean():.2f} Lakhs")
    print(f"   Median: ₹{df['Selling_Price'].median():.2f} Lakhs")
    print(f"   Std:    ₹{df['Selling_Price'].std():.2f} Lakhs")
    print(f"   Min:    ₹{df['Selling_Price'].min():.2f} Lakhs")
    print(f"   Max:    ₹{df['Selling_Price'].max():.2f} Lakhs")


# -------------------------------------------------------
# Main
# -------------------------------------------------------
def run_eda(filepath: str = None) -> None:
    """Run the complete EDA pipeline.

    Args:
        filepath: Path to car.csv. If None, uses default data/car.csv.
    """
    print("\n" + "=" * 60)
    print("RUNNING EXPLORATORY DATA ANALYSIS")
    print("=" * 60)

    # Create output directory
    os.makedirs(PLOTS_DIR, exist_ok=True)

    # Load data
    df = load_and_prepare_data(filepath)
    print(f"✅ Data loaded: {df.shape}")

    # Generate report
    generate_eda_report(df)

    # Generate all plots
    print("\n📈 Generating EDA Plots...")
    print("-" * 40)
    plot_selling_price_distribution(df)
    plot_present_vs_selling_price(df)
    plot_kms_vs_selling_price(df)
    plot_car_age_vs_selling_price(df)
    plot_selling_by_fuel_type(df)
    plot_selling_by_seller_type(df)
    plot_selling_by_transmission(df)
    plot_correlation_heatmap(df)
    print(f"\n✅ All EDA plots saved to: {PLOTS_DIR}/")


if __name__ == "__main__":
    run_eda()
