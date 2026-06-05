"""
evaluate.py
-----------
Evaluates the saved best model on the test set:
- Accuracy, Precision, Recall, F1-score
- Classification report (saved to outputs/reports)
- Confusion matrix (saved to outputs/plots)
- Sample prediction grid (saved to outputs/plots)

Run from project root:
    python src/evaluate.py
"""

import os
import sys
import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    classification_report, confusion_matrix,
    accuracy_score, precision_score, recall_score, f1_score
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.data_loader import load_cifar10
from src.utils import (
    plot_confusion_matrix, plot_sample_predictions, save_text_report
)


def main():
    print("=" * 60)
    print(" IMAGE TAGGING WITH TENSORFLOW — EVALUATION")
    print("=" * 60)

    config.ensure_dirs()

    if not os.path.exists(config.MODEL_PATH):
        print(f"[evaluate] ERROR: Model not found at {config.MODEL_PATH}")
        print("[evaluate] Please run: python src/train.py first.")
        return

    # 1. Load data + model
    (_, _), (_, _), (x_test, y_test), class_names = load_cifar10()
    model = tf.keras.models.load_model(config.MODEL_PATH)
    print("[evaluate] Model loaded successfully.")

    # 2. Predict
    print("[evaluate] Running predictions on test set...")
    probs = model.predict(x_test, batch_size=config.BATCH_SIZE, verbose=1)
    y_pred = np.argmax(probs, axis=1)

    # 3. Core metrics
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="macro", zero_division=0)
    rec = recall_score(y_test, y_pred, average="macro", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)

    print("\n----- OVERALL METRICS (macro-averaged) -----")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall   : {rec:.4f}")
    print(f"F1-score : {f1:.4f}")

    # 4. Classification report
    report = classification_report(
        y_test, y_pred, target_names=class_names, digits=4
    )
    print("\n----- CLASSIFICATION REPORT -----")
    print(report)

    summary = (
        "IMAGE TAGGING - EVALUATION REPORT\n"
        "==================================\n\n"
        f"Test Accuracy : {acc:.4f}\n"
        f"Precision     : {prec:.4f}\n"
        f"Recall        : {rec:.4f}\n"
        f"F1-score      : {f1:.4f}\n\n"
        "Per-class report:\n"
        f"{report}\n"
    )
    save_text_report(summary, os.path.join(config.REPORTS_DIR, "classification_report.txt"))

    # 5. Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plot_confusion_matrix(
        cm, class_names,
        os.path.join(config.PLOTS_DIR, "confusion_matrix.png")
    )
    # Also save CM as text
    np.savetxt(
        os.path.join(config.REPORTS_DIR, "confusion_matrix.csv"),
        cm, fmt="%d", delimiter=","
    )

    # 6. Sample predictions grid
    plot_sample_predictions(
        x_test, y_test, y_pred, class_names,
        os.path.join(config.PLOTS_DIR, "sample_predictions.png"),
        num=16
    )

    print("\n[evaluate] All reports & plots saved in outputs/.")
    print("[evaluate] Done!\n")


if __name__ == "__main__":
    main()