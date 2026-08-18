"""Train a scikit-learn classifier that predicts SLA-breach risk.

Trained on resolved incidents (where the true outcome — on_time vs
breached — is already known), then applied to open/in-progress incidents
to score their risk of breaching SLA. This is the "AI-driven automation"
piece requested by the offer, on top of the Renault-style breach-status
logic (`date de rupture < ETA`).
"""
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from ai.features import CATEGORICAL_FEATURES, SLA_RISK_FEATURES, add_time_features

MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "sla_predictor.joblib"

TARGET = "breached"


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES)],
        remainder="passthrough",
    )
    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("classifier", RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)),
        ]
    )


def train(df: pd.DataFrame) -> Pipeline:
    """Train on resolved incidents only (ground truth is known for those)."""
    resolved = df[df["breach_status"].isin(["on_time", "breached"])].copy()
    resolved = add_time_features(resolved)
    resolved[TARGET] = resolved["breach_status"] == "breached"

    X = resolved[SLA_RISK_FEATURES]
    y = resolved[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    print(classification_report(y_test, pipeline.predict(X_test)))

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    return pipeline


def load_model() -> Pipeline:
    return joblib.load(MODEL_PATH)


if __name__ == "__main__":
    from pipeline.beam_pipeline import load_classified, run_beam_transform
    from pipeline.generate_data import generate_incidents

    raw = generate_incidents(n=1000)
    prefix = run_beam_transform(raw, output_dir="data/tmp_train")
    classified = load_classified(prefix)
    train(classified)
