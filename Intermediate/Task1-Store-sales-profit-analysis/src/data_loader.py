from pathlib import Path

import pandas as pd


def load_superstore_data(file_path: Path) -> pd.DataFrame:
    """Load Superstore CSV data with clear file validation and parsing safety."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {file_path}. Please add 'Sample - Superstore.csv' to the data folder."
        )

    try:
        df = pd.read_csv(file_path, encoding="utf-8")
    except UnicodeDecodeError:
        # Fallback for datasets saved with legacy encoding.
        df = pd.read_csv(file_path, encoding="latin-1")
    except Exception as exc:
        raise RuntimeError(f"Failed to read dataset: {exc}") from exc

    if df.empty:
        raise ValueError("Loaded dataset is empty. Please verify the CSV file content.")

    return df
