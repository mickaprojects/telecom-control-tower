"""Inference helpers shared by the Prefect flow and the FastAPI backend."""
from __future__ import annotations

import pandas as pd

from ai import train_anomaly_detector, train_sla_predictor
from ai.features import ANOMALY_FEATURES, SLA_RISK_FEATURES, add_time_features


def add_predictions(df: pd.DataFrame) -> pd.DataFrame:
    """Score every incident with both models and attach the results."""
    df = add_time_features(df)

    sla_model = train_sla_predictor.load_model()
    anomaly_model = train_anomaly_detector.load_model()

    df["breach_risk"] = sla_model.predict_proba(df[SLA_RISK_FEATURES])[:, 1]
    df["anomaly_flag"] = anomaly_model.predict(df[ANOMALY_FEATURES]) == -1
    df["anomaly_score"] = -anomaly_model.decision_function(df[ANOMALY_FEATURES])

    return df
