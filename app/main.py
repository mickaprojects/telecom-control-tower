"""FastAPI backend exposing the control tower's latest flow-run results."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import case, func

from app.database import get_session, init_db
from app.models import Incident
from app.schemas import FolderSummary, IncidentOut, Stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("control_tower.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("API started, database ready")
    yield


app = FastAPI(title="Telecom SLA Control Tower", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/incidents", response_model=list[IncidentOut])
def list_incidents(
    folder: str | None = None,
    status_: str | None = Query(default=None, alias="status"),
    breach_status: str | None = None,
    limit: int = 200,
):
    with get_session() as session:
        q = session.query(Incident)
        if folder:
            q = q.filter(Incident.folder == folder)
        if status_:
            q = q.filter(Incident.status == status_)
        if breach_status:
            q = q.filter(Incident.breach_status == breach_status)
        return q.limit(limit).all()


@app.get("/incidents/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: str):
    with get_session() as session:
        incident = session.get(Incident, incident_id)
        if incident is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        return incident


@app.get("/folders", response_model=list[FolderSummary])
def list_folders():
    with get_session() as session:
        rows = (
            session.query(
                Incident.folder,
                func.count(Incident.incident_id),
                func.sum(case((Incident.breach_status == "breached", 1), else_=0)),
                func.sum(case((Incident.breach_status == "at_risk", 1), else_=0)),
            )
            .group_by(Incident.folder)
            .all()
        )
        return [
            FolderSummary(folder=f, total=t, breached=b or 0, at_risk=a or 0)
            for f, t, b, a in rows
        ]


@app.get("/alerts", response_model=list[IncidentOut])
def list_alerts():
    with get_session() as session:
        return (
            session.query(Incident)
            .filter((Incident.breach_status == "breached") | (Incident.anomaly_flag.is_(True)))
            .all()
        )


@app.get("/stats", response_model=Stats)
def get_stats():
    with get_session() as session:
        total = session.query(func.count(Incident.incident_id)).scalar() or 0
        breached = (
            session.query(func.count(Incident.incident_id))
            .filter(Incident.breach_status == "breached")
            .scalar()
            or 0
        )
        at_risk = (
            session.query(func.count(Incident.incident_id))
            .filter(Incident.breach_status == "at_risk")
            .scalar()
            or 0
        )
        on_time = (
            session.query(func.count(Incident.incident_id))
            .filter(Incident.breach_status == "on_time")
            .scalar()
            or 0
        )
        anomalies = (
            session.query(func.count(Incident.incident_id))
            .filter(Incident.anomaly_flag.is_(True))
            .scalar()
            or 0
        )
    return Stats(
        total_incidents=total,
        breached=breached,
        at_risk=at_risk,
        on_time=on_time,
        anomalies=anomalies,
    )
