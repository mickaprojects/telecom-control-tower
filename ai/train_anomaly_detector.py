"""Unsupervised anomaly detection over incident patterns (Isolation Forest).

Flags incidents that don't fit the usual profile for their category (e.g.
an unusually long-running low-severity ticket) — the kind of signal that
would warrant a closer look, similar to how the Renault dashboard surfaced
ad-hoc "crisis" folders (e.g. "Crise neige Auvergne").
"""
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from ai.features import ANOMALY_FEATURES, CATEGORICAL_FEATURES

MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "anomaly_detector.joblib"

CATEGORICAL = CATEGORICAL_FEATURES
NUMERIC = ["hours_margin"]


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL)],
        remainder="passthrough",
    )
    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("detector", IsolationForest(n_estimators=200, contamination=0.08, random_state=42)),
        ]
    )


def train(df: pd.DataFrame) -> Pipeline:
    X = df[ANOMALY_FEATURES].copy()
    pipeline = build_pipeline()
    pipeline.fit(X)

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
