"""Tests for the SLA-risk classifier and the anomaly detector."""
from __future__ import annotations

from ai import train_anomaly_detector, train_sla_predictor
from pipeline.beam_pipeline import load_classified, run_beam_transform
from pipeline.generate_data import generate_incidents


def _classified_batch(tmp_path, n=300, seed=3):
    df = generate_incidents(n=n, seed=seed)
    prefix = run_beam_transform(df, output_dir=str(tmp_path))
    return load_classified(prefix)


def test_sla_predictor_trains_and_scores(tmp_path, monkeypatch):
    monkeypatch.setattr(train_sla_predictor, "MODEL_DIR", tmp_path)
    monkeypatch.setattr(train_sla_predictor, "MODEL_PATH", tmp_path / "sla.joblib")

    classified = _classified_batch(tmp_path / "data")
    model = train_sla_predictor.train(classified)
    assert hasattr(model, "predict_proba")


def test_anomaly_detector_trains_and_flags(tmp_path, monkeypatch):
    monkeypatch.setattr(train_anomaly_detector, "MODEL_DIR", tmp_path)
    monkeypatch.setattr(train_anomaly_detector, "MODEL_PATH", tmp_path / "anomaly.joblib")

    classified = _classified_batch(tmp_path / "data")
    model = train_anomaly_detector.train(classified)
    predictions = model.predict(
        classified[train_anomaly_detector.CATEGORICAL + train_anomaly_detector.NUMERIC]
    )
    assert set(predictions).issubset({-1, 1})
