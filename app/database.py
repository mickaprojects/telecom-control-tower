"""SQLite persistence layer for the control tower demo.

SQLite stands in for the MongoDB/BigQuery storage used in the Renault
Control Tower — swappable for a real database without touching the rest
of the app.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models import Base, Incident

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "control_tower.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def _to_row(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "incident_id": record["incident_id"],
        "region": record["region"],
        "lat": float(record["lat"]),
        "lon": float(record["lon"]),
        "incident_type": record["incident_type"],
        "severity": record["severity"],
        "folder": record["folder"],
        "opened_at": str(record["opened_at"]),
        "sla_deadline": str(record["sla_deadline"]),
        "actual_resolution": str(record["actual_resolution"]) if record.get("actual_resolution") else None,
        "status": record["status"],
        "breach_status": record["breach_status"],
        "hours_margin": float(record["hours_margin"]),
        "breach_risk": float(record.get("breach_risk", 0.0)),
        "anomaly_flag": bool(record.get("anomaly_flag", False)),
        "anomaly_score": float(record.get("anomaly_score", 0.0)),
    }


def replace_incidents(df: pd.DataFrame) -> int:
    """Replace the incidents table with the latest flow run's output."""
    init_db()
    records = df.to_dict("records")
    with SessionLocal() as session:
        session.query(Incident).delete()
        session.bulk_insert_mappings(Incident, [_to_row(r) for r in records])
        session.commit()
    return len(records)


def add_incident(record: dict[str, Any]) -> None:
    """Insert or update a single incident, without touching the rest of the table.

    Used to drop one hand-crafted, realistic incident into the database (see
    scripts/simulate_incident.py) without replacing the full batch produced
    by the pipeline.
    """
    init_db()
    with SessionLocal() as session:
        session.merge(Incident(**_to_row(record)))
        session.commit()


def get_session() -> Session:
    return SessionLocal()
