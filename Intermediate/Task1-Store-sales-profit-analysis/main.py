from pathlib import Path

from src.analysis import run_full_analysis
from src.data_cleaning import clean_store_data, save_cleaned_data
from src.data_loader import load_superstore_data
from src.report_generator import generate_markdown_report
from src.visualizations import build_figures, save_figures_as_html


def main() -> None:
    project_root = Path(__file__).resolve().parent
    data_path = project_root / "data" / "Sample - Superstore.csv"
    cleaned_output = project_root / "outputs" / "cleaned_data" / "cleaned_superstore.csv"
    report_output = project_root / "outputs" / "reports" / "final_analysis_report.md"
    charts_output = project_root / "outputs" / "charts"

    print("Loading data...")
    raw_df = load_superstore_data(data_path)

    print("Cleaning data...")
    clean_df, cleaning_summary = clean_store_data(raw_df)
    saved_clean_path = save_cleaned_data(clean_df, cleaned_output)

    print("Running analysis...")
    analysis = run_full_analysis(clean_df)

    print("Generating visual outputs...")
    figures = build_figures(analysis, clean_df)
    save_figures_as_html(figures, charts_output)

    print("Generating markdown report...")
    report_path = generate_markdown_report(analysis, cleaning_summary, report_output)

    print("Pipeline completed successfully.")
    print(f"Cleaned data saved at: {saved_clean_path}")
    print(f"Report saved at: {report_path}")
    print(f"Charts saved in: {charts_output}")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as file_err:
        print(f"ERROR: {file_err}")
    except Exception as err:
        print(f"Unexpected error while running the project: {err}")
