"""Pydantic response schemas for the API."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incident_id: str
    region: str
    lat: float
    lon: float
    incident_type: str
    severity: str
    folder: str
    opened_at: str
    sla_deadline: str
    actual_resolution: str | None
    status: str
    breach_status: str
    hours_margin: float
    breach_risk: float
    anomaly_flag: bool
    anomaly_score: float


class FolderSummary(BaseModel):
    folder: str
    total: int
    breached: int
    at_risk: int


class Stats(BaseModel):
    total_incidents: int
    breached: int
    at_risk: int
    on_time: int
    anomalies: int
