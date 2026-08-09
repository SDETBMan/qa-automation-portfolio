"""Send QMS evidence collection metrics to DataDog."""

from __future__ import annotations

import os
import time

import requests

from .mapper import ComplianceMap

_DD_ENDPOINT = "https://api.datadoghq.com/api/v2/series"
_TAGS = ["service:qa-automation-portfolio", "env:ci", "framework:qms-evidence-collector"]


def _api_key() -> str | None:
    key = os.getenv("DD_API_KEY", "")
    return key if key else None


def _gauge(metric: str, value: float, extra_tags: list[str] | None = None) -> dict:
    tags = _TAGS + (extra_tags or [])
    return {
        "metric": metric,
        "type": 3,  # GAUGE
        "points": [{"timestamp": int(time.time()), "value": value}],
        "tags": tags,
    }


def _post(series: list[dict]) -> None:
    api_key = _api_key()
    if not api_key:
        print("[WARN] DD_API_KEY not set. Skipping DataDog metrics.")
        return

    try:
        resp = requests.post(
            _DD_ENDPOINT,
            json={"series": series},
            headers={
                "DD-API-KEY": api_key,
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        if resp.status_code == 202:
            print(f"[INFO] Sent {len(series)} metrics to DataDog.")
        else:
            print(f"[WARN] DataDog returned {resp.status_code}: {resp.text[:200]}")
    except Exception as exc:
        print(f"[ERROR] DataDog metrics failed: {exc}")


def send_evidence_metrics(compliance_map: ComplianceMap) -> None:
    """Send QMS evidence collection metrics to DataDog.

    Metrics:
        qms.clauses_covered      — total unique clauses across all standards
        qms.evidence_files        — total artifact files discovered
        qms.iso9001_clauses       — ISO 9001 clause count
        qms.soc2_controls         — SOC 2 control count
        qms.iso17025_clauses      — ISO/IEC 17025 clause count
    """
    iso_9001_count = len(set(e.clause_id for e in compliance_map.iso_9001_clauses))
    soc2_count = len(set(e.clause_id for e in compliance_map.soc2_controls))
    iso_17025_count = len(set(e.clause_id for e in compliance_map.iso_17025_clauses))

    series = [
        _gauge("qms.clauses_covered", compliance_map.unique_clause_count),
        _gauge("qms.evidence_files", compliance_map.total_evidence_files),
        _gauge("qms.iso9001_clauses", iso_9001_count),
        _gauge("qms.soc2_controls", soc2_count),
        _gauge("qms.iso17025_clauses", iso_17025_count),
    ]

    _post(series)
