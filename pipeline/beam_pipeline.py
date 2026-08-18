"""Apache Beam batch transform (DirectRunner) — the data-engineering pipeline stage.

Mirrors the role Dataflow/Beam played in the Renault Control Tower project:
here it computes SLA breach status for each incident and writes the result
to a sink, exactly like a production batch job would write to GCS/BigQuery.
Swapping DirectRunner for DataflowRunner is a one-line pipeline-option
change for a real deployment.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import apache_beam as beam
import pandas as pd


def _classify(record: dict[str, Any], now_iso: str) -> dict[str, Any]:
    now = datetime.fromisoformat(now_iso)
    record = dict(record)
    sla_deadline = datetime.fromisoformat(record["sla_deadline"])
    actual_resolution = record.get("actual_resolution")
    actual_resolution = datetime.fromisoformat(actual_resolution) if actual_resolution else None
    status = record["status"]

    if status == "resolved" and actual_resolution is not None:
        breached = actual_resolution > sla_deadline
        breach_status = "breached" if breached else "on_time"
        hours_margin = (sla_deadline - actual_resolution).total_seconds() / 3600
    else:
        hours_margin = (sla_deadline - now).total_seconds() / 3600
        if hours_margin < 0:
            breach_status = "breached"
        elif hours_margin < 2:
            breach_status = "at_risk"
        else:
            breach_status = "on_time"

    record["hours_margin"] = round(hours_margin, 2)
    record["breach_status"] = breach_status
    return record


def _to_jsonable(record: dict[str, Any]) -> dict[str, Any]:
    out = dict(record)
    for key in ("opened_at", "sla_deadline", "actual_resolution"):
        value = out.get(key)
        out[key] = value.isoformat() if isinstance(value, datetime) and pd.notna(value) else None
    return out


def run_beam_transform(df: pd.DataFrame, output_dir: str, now: datetime | None = None) -> str:
    """Batch-transform incidents through an Apache Beam (DirectRunner) pipeline.

    Writes classified records as JSON lines to `output_dir` and returns the
    output-file prefix so downstream stages can read it back.
    """
    now = now or datetime.utcnow()
    now_iso = now.isoformat()
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_prefix = str(Path(output_dir) / "incidents_classified")

    records = [_to_jsonable(r) for r in df.to_dict("records")]

    with beam.Pipeline() as pipeline:
        (
            pipeline
            | "CreateRecords" >> beam.Create(records)
            | "ClassifyBreachStatus" >> beam.Map(_classify, now_iso=now_iso)
            | "ToJson" >> beam.Map(json.dumps)
            | "WriteResults" >> beam.io.WriteToText(output_prefix, file_name_suffix=".jsonl")
        )
    return output_prefix


def load_classified(output_prefix: str) -> pd.DataFrame:
    """Read the Beam pipeline output back into a DataFrame for downstream stages."""
    records: list[dict[str, Any]] = []
    prefix_path = Path(output_prefix)
    for path in sorted(prefix_path.parent.glob(prefix_path.name + "*.jsonl")):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    return pd.DataFrame(records)


if __name__ == "__main__":
    from pipeline.generate_data import generate_incidents

    raw = generate_incidents(n=20)
    prefix = run_beam_transform(raw, output_dir="data/tmp")
    result = load_classified(prefix)
    print(result[["incident_id", "status", "breach_status", "hours_margin"]].head())
