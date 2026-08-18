"""Prefect flow: generate -> Beam transform -> AI inference -> persist.

Runs entirely locally, no Prefect Cloud account needed. This is the
explicit "workflow automation" piece the offer calls out, sitting on top
of the Beam data-engineering pipeline and the scikit-learn models.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from prefect import flow, get_run_logger, task

from ai import predict, train_anomaly_detector, train_sla_predictor
from app.database import init_db, replace_incidents
from pipeline.beam_pipeline import load_classified, run_beam_transform
from pipeline.generate_data import generate_incidents

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@task(retries=2, retry_delay_seconds=5)
def generate_data_task(n: int = 500) -> pd.DataFrame:
    logger = get_run_logger()
    df = generate_incidents(n=n)
    logger.info("Generated %d synthetic incidents", len(df))
    return df


@task(retries=2, retry_delay_seconds=5)
def beam_transform_task(df: pd.DataFrame) -> pd.DataFrame:
    logger = get_run_logger()
    prefix = run_beam_transform(df, output_dir=str(DATA_DIR / "batch"))
    classified = load_classified(prefix)
    logger.info("Beam pipeline classified %d incidents", len(classified))
    return classified


@task
def ensure_models_task(df: pd.DataFrame) -> None:
    logger = get_run_logger()
    if not train_sla_predictor.MODEL_PATH.exists():
        logger.info("No SLA-risk model found - training one now")
        train_sla_predictor.train(df)
    if not train_anomaly_detector.MODEL_PATH.exists():
        logger.info("No anomaly-detection model found - training one now")
        train_anomaly_detector.train(df)


@task
def predict_task(df: pd.DataFrame) -> pd.DataFrame:
    logger = get_run_logger()
    scored = predict.add_predictions(df)
    breaches = int((scored["breach_status"] == "breached").sum())
    anomalies = int(scored["anomaly_flag"].sum())
    logger.info("%d incidents breached, %d flagged as anomalies", breaches, anomalies)
    return scored


@task(retries=2, retry_delay_seconds=5)
def persist_task(df: pd.DataFrame) -> int:
    logger = get_run_logger()
    init_db()
    count = replace_incidents(df)
    logger.info("Persisted %d incidents to the local database", count)
    return count


@flow(name="telecom-control-tower-flow")
def control_tower_flow(n: int = 500) -> int:
    raw = generate_data_task(n=n)
    classified = beam_transform_task(raw)
    ensure_models_task(classified)
    scored = predict_task(classified)
    return persist_task(scored)


if __name__ == "__main__":
    control_tower_flow(n=800)
