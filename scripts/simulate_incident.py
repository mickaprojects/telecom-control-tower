"""Add hand-crafted, realistic incidents to the local database, so they show
up immediately on the frontend/dashboard alongside existing data.

Each entry in `INCIDENTS` below is a real-world scenario (a dropped call, a
base station with no coverage, network congestion...). Edit the list, or add
your own entries, then run:

    python -m scripts.simulate_incident

Re-running with the same incident_id updates that same incident instead of
creating a duplicate.
"""
from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

from ai.predict import add_predictions
from app.database import add_incident
from pipeline.beam_pipeline import _classify, _to_jsonable
from pipeline.generate_data import REGIONS

NOW = datetime.utcnow()

# ---------------------------------------------------------------------------
# One entry per real-world scenario. Edit freely, or add new ones.
INCIDENTS = [
    {
        # "I call someone and the call drops"
        "incident_id": "demo-dropped-call-paris",
        "region": "Paris (FR)",
        "incident_type": "Service Degradation",
        "severity": "high",
        "folder": "Routine Monitoring",
        "opened_at": NOW - timedelta(hours=3),
        "sla_deadline": NOW + timedelta(minutes=45),  # closing in -> "at risk"
        "actual_resolution": None,
        "status": "in_progress",
    },
    {
        # "My phone has no network coverage at all" (site down / power cut)
        "incident_id": "demo-no-coverage-berlin",
        "region": "Berlin (DE)",
        "incident_type": "Power Failure",
        "severity": "critical",
        "folder": "Storm Alert - Benelux",
        "opened_at": NOW - timedelta(hours=3, minutes=50),
        "sla_deadline": NOW - timedelta(minutes=10),  # already missed -> "breached"
        "actual_resolution": None,
        "status": "in_progress",
    },
    {
        # "Mobile internet is very slow at certain hours" (peak-time overload)
        "incident_id": "demo-congestion-madrid",
        "region": "Madrid (ES)",
        "incident_type": "Congestion",
        "severity": "medium",
        "folder": "Black Friday Traffic Surge",
        "opened_at": NOW - timedelta(hours=20),
        "sla_deadline": NOW - timedelta(hours=4),
        "actual_resolution": NOW - timedelta(hours=10),  # fixed well before deadline
        "status": "resolved",
    },
    {
        # "A fiber cut takes out a whole neighbourhood"
        "incident_id": "demo-fiber-cut-warsaw",
        "region": "Warsaw (PL)",
        "incident_type": "Fiber Cut",
        "severity": "critical",
        "folder": "Fiber Cut - A1 Motorway",
        "opened_at": NOW - timedelta(hours=10),
        "sla_deadline": NOW - timedelta(hours=6),
        "actual_resolution": NOW - timedelta(hours=2),  # fixed, but after the deadline
        "status": "resolved",
    },
    {
        # "A piece of network hardware fails"
        "incident_id": "demo-equipment-failure-rome",
        "region": "Rome (IT)",
        "incident_type": "Equipment Failure",
        "severity": "high",
        "folder": "Routine Monitoring",
        "opened_at": NOW - timedelta(hours=1),
        "sla_deadline": NOW + timedelta(hours=5),  # plenty of margin -> "on time"
        "actual_resolution": None,
        "status": "in_progress",
    },
    {
        # "A customer calls support to complain about a recurring issue"
        "incident_id": "demo-customer-complaint-amsterdam",
        "region": "Amsterdam (NL)",
        "incident_type": "Customer Complaint",
        "severity": "low",
        "folder": "Routine Monitoring",
        "opened_at": NOW - timedelta(hours=30),
        "sla_deadline": NOW - timedelta(hours=6),
        "actual_resolution": NOW - timedelta(hours=20),
        "status": "resolved",
    },
]
# ---------------------------------------------------------------------------

for incident in INCIDENTS:
    lat, lon = REGIONS[incident["region"]]
    incident = {**incident, "lat": lat, "lon": lon}

    classified = _classify(_to_jsonable(incident), NOW.isoformat())
    scored = add_predictions(pd.DataFrame([classified])).iloc[0].to_dict()
    add_incident(scored)

    print(
        f"{scored['incident_id']:<32} {scored['incident_type']:<20} "
        f"{scored['breach_status']:<10} breach risk {scored['breach_risk'] * 100:5.1f}%  "
        f"anomaly={scored['anomaly_flag']}"
    )

print(f"\n{len(INCIDENTS)} scenario(s) added.")
print("Refresh the frontend (http://localhost:5173) or the Streamlit dashboard to see them.")
