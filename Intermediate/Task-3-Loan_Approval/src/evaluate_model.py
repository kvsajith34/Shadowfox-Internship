"""
Evaluation utilities: classification report, confusion matrix plot,
feature importance plot, and a markdown model report.

Can be imported by train_model.py or run standalone:
    python src/evaluate_model.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")  # headless-safe
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
)

from src.data_preprocessing import get_clean_data
from src.utils import REPORTS_DIR, ensure_dirs, load_model

CLASS_NAMES = ["Rejected", "Approved"]


def _feature_names_from_pipeline(pipeline) -> list[str]:
    """Extract output feature names from the fitted ColumnTransformer."""
    pre = pipeline.named_steps["preprocessor"]
    try:
        return list(pre.get_feature_names_out())
    except Exception:
        return []


def plot_confusion_matrix(y_true, y_pred, path):
    """Save a confusion matrix heatmap."""
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm, display_labels=CLASS_NAMES
    )
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title("Confusion Matrix")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def plot_feature_importance(pipeline, path):
    """
    Save a feature importance / coefficient plot if the model supports it.
    Falls back gracefully for models without importances.
    """
    model = pipeline.named_steps["model"]
    feat_names = _feature_names_from_pipeline(pipeline)

    importances = None
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_).ravel()

    if importances is None or len(feat_names) != len(importances):
        # Create a placeholder note image
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(
            0.5,
            0.5,
            "Feature importance not available\nfor the selected model.",
            ha="center",
            va="center",
            fontsize=11,
        )
        ax.axis("off")
        fig.savefig(path, dpi=120)
        plt.close(fig)
        return

    imp_df = (
        pd.DataFrame({"feature": feat_names, "importance": importances})
        .sort_values("importance", ascending=False)
        .head(15)
    )

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(data=imp_df, x="importance", y="feature", ax=ax, palette="viridis")
    ax.set_title("Top Feature Importances")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def generate_reports(pipeline, X_test, y_test, all_results, model_name):
    """Generate all evaluation artifacts into reports/."""
    ensure_dirs()
    y_pred = pipeline.predict(X_test)

    # Classification report (txt)
    report_txt = classification_report(
        y_test, y_pred, target_names=CLASS_NAMES, zero_division=0
    )
    (REPORTS_DIR / "classification_report.txt").write_text(report_txt)

    # Confusion matrix plot
    plot_confusion_matrix(
        y_test, y_pred, REPORTS_DIR / "confusion_matrix.png"
    )

    # Feature importance plot
    plot_feature_importance(pipeline, REPORTS_DIR / "feature_importance.png")

    # Markdown model report
    acc = accuracy_score(y_test, y_pred)
    results_df = pd.DataFrame(all_results)
    md = []
    md.append("# Model Report\n")
    md.append(f"**Best Model:** {model_name}\n")
    md.append(f"**Test Accuracy:** {acc:.4f}\n")
    md.append("## Model Comparison\n")
    md.append(results_df.to_markdown(index=False))
    md.append("\n\n## Classification Report\n")
    md.append("```\n" + report_txt + "\n```\n")
    md.append("## Artifacts\n")
    md.append("- `confusion_matrix.png`\n")
    md.append("- `feature_importance.png`\n")
    md.append("- `classification_report.txt`\n")
    (REPORTS_DIR / "model_report.md").write_text("\n".join(md))

    print(f"Evaluation reports written to: {REPORTS_DIR}")


if __name__ == "__main__":
    from sklearn.model_selection import train_test_split

    X, y = get_clean_data()
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    pipe = load_model()
    y_pred = pipe.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=CLASS_NAMES))
    generate_reports(pipe, X_test, y_test, [], "Loaded Model")