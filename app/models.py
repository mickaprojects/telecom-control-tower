"""SQLAlchemy ORM models."""
from __future__ import annotations

from sqlalchemy import Boolean, Column, Float, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Incident(Base):
    __tablename__ = "incidents"

    incident_id = Column(String, primary_key=True)
    region = Column(String, index=True)
    lat = Column(Float)
    lon = Column(Float)
    incident_type = Column(String, index=True)
    severity = Column(String, index=True)
    folder = Column(String, index=True)
    opened_at = Column(String)
    sla_deadline = Column(String)
    actual_resolution = Column(String, nullable=True)
    status = Column(String, index=True)
    breach_status = Column(String, index=True)
    hours_margin = Column(Float)
    breach_risk = Column(Float)
    anomaly_flag = Column(Boolean, index=True)
    anomaly_score = Column(Float)
