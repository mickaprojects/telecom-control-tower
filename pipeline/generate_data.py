"""Synthetic telecom incident/ticket generator — stands in for a real ingestion source.

Mirrors the shape of the Renault Control Tower "trajets" feed (an entity
with a planned deadline that may or may not be met), applied to telecom
SLA tickets instead of transport ETAs.
"""
from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta

import pandas as pd

REGIONS = {
    "Paris (FR)": (48.8566, 2.3522),
    "Berlin (DE)": (52.5200, 13.4050),
    "Madrid (ES)": (40.4168, -3.7038),
    "Rome (IT)": (41.9028, 12.4964),
    "Brussels (BE)": (50.8503, 4.3517),
    "Warsaw (PL)": (52.2297, 21.0122),
    "Amsterdam (NL)": (52.3676, 4.9041),
    "Vienna (AT)": (48.2082, 16.3738),
    "Lisbon (PT)": (38.7223, -9.1393),
    "Prague (CZ)": (50.0755, 14.4378),
}

INCIDENT_TYPES = [
    "Network Outage",
    "Service Degradation",
    "Equipment Failure",
    "Congestion",
    "Customer Complaint",
    "Fiber Cut",
    "Power Failure",
]

SEVERITY_SLA_HOURS = {
    "critical": 4,
    "high": 8,
    "medium": 24,
    "low": 72,
}

FOLDERS = [
    "Storm Alert - Benelux",
    "Planned Maintenance - Core Network",
    "Black Friday Traffic Surge",
    "Fiber Cut - A1 Motorway",
    "Routine Monitoring",
    "Unassigned",
]


def _pick_severity(rng: random.Random) -> str:
    return rng.choices(list(SEVERITY_SLA_HOURS), weights=[0.1, 0.25, 0.4, 0.25], k=1)[0]


def generate_incidents(n: int = 500, seed: int | None = 42, now: datetime | None = None) -> pd.DataFrame:
    """Generate a synthetic batch of telecom incidents/tickets."""
    rng = random.Random(seed)
    now = now or datetime.utcnow()
    rows = []
    for _ in range(n):
        region = rng.choice(list(REGIONS))
        incident_type = rng.choice(INCIDENT_TYPES)
        severity = _pick_severity(rng)
        sla_hours = SEVERITY_SLA_HOURS[severity]

        opened_at = now - timedelta(hours=rng.uniform(0, sla_hours * 3))
        sla_deadline = opened_at + timedelta(hours=sla_hours)

        outcome = rng.random()
        actual_resolution = None
        status = "open"
        if outcome < 0.55:
            actual_resolution = opened_at + timedelta(hours=rng.uniform(0.2, sla_hours * 0.85))
            status = "resolved"
        elif outcome < 0.75:
            actual_resolution = opened_at + timedelta(hours=rng.uniform(sla_hours * 1.05, sla_hours * 2))
            status = "resolved"
        else:
            status = "in_progress" if rng.random() < 0.7 else "open"

        lat, lon = REGIONS[region]
        rows.append(
            {
                "incident_id": str(uuid.uuid4()),
                "region": region,
                "lat": lat + rng.uniform(-0.3, 0.3),
                "lon": lon + rng.uniform(-0.3, 0.3),
                "incident_type": incident_type,
                "severity": severity,
                "folder": rng.choice(FOLDERS),
                "opened_at": opened_at,
                "sla_deadline": sla_deadline,
                "actual_resolution": actual_resolution,
                "status": status,
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate_incidents()
    print(df.head())
    print(f"Generated {len(df)} incidents")
