"""Shared feature engineering for the SLA-risk and anomaly-detection models."""
from __future__ import annotations

import pandas as pd

SLA_HOURS_BY_SEVERITY = {"critical": 4, "high": 8, "medium": 24, "low": 72}

CATEGORICAL_FEATURES = ["region", "incident_type", "severity"]
SLA_RISK_FEATURES = CATEGORICAL_FEATURES + ["sla_hours", "open_hour", "open_weekday"]
ANOMALY_FEATURES = CATEGORICAL_FEATURES + ["hours_margin"]


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived time/SLA features used by both models."""
    df = df.copy()
    df["opened_at"] = pd.to_datetime(df["opened_at"])
    df["open_hour"] = df["opened_at"].dt.hour
    df["open_weekday"] = df["opened_at"].dt.weekday
    df["sla_hours"] = df["severity"].map(SLA_HOURS_BY_SEVERITY)
    return df
