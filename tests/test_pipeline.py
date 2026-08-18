"""Tests for the synthetic data generator and the Beam transform stage."""
from __future__ import annotations

from pipeline.beam_pipeline import load_classified, run_beam_transform
from pipeline.generate_data import generate_incidents


def test_generate_incidents_shape():
    df = generate_incidents(n=50, seed=1)
    assert len(df) == 50
    assert {"incident_id", "region", "sla_deadline", "status"}.issubset(df.columns)


def test_beam_transform_classifies_breach_status(tmp_path):
    df = generate_incidents(n=30, seed=2)
    prefix = run_beam_transform(df, output_dir=str(tmp_path))
    classified = load_classified(prefix)

    assert len(classified) == 30
    assert set(classified["breach_status"]).issubset({"on_time", "at_risk", "breached"})
    assert "hours_margin" in classified.columns
