"""Tests for the FastAPI backend."""
from __future__ import annotations

from fastapi.testclient import TestClient

import app.database as db
from app.database import init_db, replace_incidents
from app.main import app
from pipeline.beam_pipeline import load_classified, run_beam_transform
from pipeline.generate_data import generate_incidents
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _seed_database(tmp_path, monkeypatch):
    test_db_path = tmp_path / "test.db"
    test_engine = create_engine(f"sqlite:///{test_db_path}", connect_args={"check_same_thread": False})
    monkeypatch.setattr(db, "engine", test_engine)
    monkeypatch.setattr(db, "SessionLocal", sessionmaker(bind=test_engine))
    init_db()

    raw = generate_incidents(n=50, seed=7)
    prefix = run_beam_transform(raw, output_dir=str(tmp_path / "batch"))
    classified = load_classified(prefix)
    classified["breach_risk"] = 0.5
    classified["anomaly_flag"] = False
    classified["anomaly_score"] = 0.0
    replace_incidents(classified)


def test_stats_endpoint(tmp_path, monkeypatch):
    _seed_database(tmp_path, monkeypatch)
    client = TestClient(app)
    response = client.get("/stats")
    assert response.status_code == 200
    body = response.json()
    assert body["total_incidents"] == 50


def test_incidents_endpoint(tmp_path, monkeypatch):
    _seed_database(tmp_path, monkeypatch)
    client = TestClient(app)
    response = client.get("/incidents", params={"limit": 5})
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_folders_endpoint(tmp_path, monkeypatch):
    _seed_database(tmp_path, monkeypatch)
    client = TestClient(app)
    response = client.get("/folders")
    assert response.status_code == 200
    assert len(response.json()) > 0
