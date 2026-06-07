"""
Train multiple classification models, evaluate them, select the best
(by F1-score), and save the full pipeline + metadata.

Run:
    python src/train_model.py
"""

from __future__ import annotations

from datetime import datetime

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from src.data_preprocessing import (
    ALL_FEATURES,
    build_preprocessing_pipeline,
    get_clean_data,
)
from src.utils import (
    METADATA_PATH,
    MODEL_PATH,
    PIPELINE_PATH,
    TARGET_COLUMN,
    ensure_dirs,
    save_json,
    save_model,
)

# Optional XGBoost (only if installed)
try:
    from xgboost import XGBClassifier

    XGB_AVAILABLE = True
except Exception:  # pragma: no cover
    XGB_AVAILABLE = False


def get_candidate_models() -> dict:
    """Return dictionary of candidate classifiers."""
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(
            n_estimators=200, random_state=42
        ),
        "Support Vector Classifier": SVC(probability=True, random_state=42),
        "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=7),
        "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    }
    if XGB_AVAILABLE:
        models["XGBoost"] = XGBClassifier(
            n_estimators=200,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,
            eval_metric="logloss",
        )
    return models


def train_and_select():
    """Train all candidate models and select the best by F1-score."""
    ensure_dirs()
    X, y = get_clean_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    preprocessor = build_preprocessing_pipeline()
    candidates = get_candidate_models()

    results = []
    best = None

    print("=" * 60)
    print("Training and evaluating models")
    print("=" * 60)

    for name, clf in candidates.items():
        pipe = Pipeline(steps=[("preprocessor", preprocessor), ("model", clf)])
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)

        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds, zero_division=0)
        rec = recall_score(y_test, preds, zero_division=0)
        f1 = f1_score(y_test, preds, zero_division=0)

        # Cross-validation (on full data) for reliability
        cv = cross_val_score(pipe, X, y, cv=5, scoring="f1").mean()

        row = {
            "model": name,
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "cv_f1": round(cv, 4),
        }
        results.append(row)

        print(
            f"{name:28s} | acc={acc:.3f} prec={prec:.3f} "
            f"rec={rec:.3f} f1={f1:.3f} cv_f1={cv:.3f}"
        )

        # Selection score: blend F1 + CV F1 for reliability
        score = 0.5 * f1 + 0.5 * cv
        if best is None or score > best["score"]:
            best = {
                "name": name,
                "pipeline": pipe,
                "score": score,
                "metrics": row,
            }

    print("=" * 60)
    print(f"Best model: {best['name']} (blended F1 score={best['score']:.4f})")
    print("=" * 60)

    # Save best model (full pipeline incl. preprocessing)
    save_model(best["pipeline"], MODEL_PATH)
    # Save standalone preprocessing pipeline (fitted on training data)
    fitted_preprocessor = best["pipeline"].named_steps["preprocessor"]
    save_model(fitted_preprocessor, PIPELINE_PATH)

    # Metadata
    metadata = {
        "best_model": best["name"],
        "accuracy": best["metrics"]["accuracy"],
        "precision": best["metrics"]["precision"],
        "recall": best["metrics"]["recall"],
        "f1_score": best["metrics"]["f1"],
        "cv_f1": best["metrics"]["cv_f1"],
        "training_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "feature_columns": [c for c in ALL_FEATURES if c in X.columns],
        "target_column": TARGET_COLUMN,
        "dataset_size": int(len(X)),
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "all_model_results": results,
    }
    save_json(metadata, METADATA_PATH)

    print(f"Saved model     -> {MODEL_PATH}")
    print(f"Saved pipeline  -> {PIPELINE_PATH}")
    print(f"Saved metadata  -> {METADATA_PATH}")

    # Generate evaluation artifacts (reports + plots)
    try:
        from src.evaluate_model import generate_reports

        generate_reports(best["pipeline"], X_test, y_test, results, best["name"])
    except Exception as e:  # pragma: no cover
        print(f"[warn] Could not generate evaluation reports: {e}")

    return best


if __name__ == "__main__":
    train_and_select()