"""Shared fixtures for claims-diff test suite."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from differ.loader import load_claims_csv
from differ.models import ClaimRecord

_DATASETS = Path(__file__).resolve().parent.parent / "datasets"

_CLAIM_DEFAULTS: dict[str, Any] = {
    "claim_id": "CLM-001",
    "patient_id": "PAT-101",
    "procedure_code": "99213",
    "billed_cents": 15000,
    "allowed_cents": 12000,
    "paid_cents": 9600,
    "status": "paid",
    "adjudication_date": date(2026, 1, 15),
}


@pytest.fixture()
def sample_claim():
    """Factory fixture: returns a ClaimRecord with sensible defaults.

    Call with keyword overrides to customise individual fields:
        sample_claim(status="denied", billed_cents=0)
    """
    def _factory(**overrides: Any) -> ClaimRecord:
        fields = {**_CLAIM_DEFAULTS, **overrides}
        return ClaimRecord(**fields)
    return _factory


@pytest.fixture()
def baseline_claims() -> list[ClaimRecord]:
    """Load the 20-record baseline dataset shipped with the project."""
    return load_claims_csv(_DATASETS / "baseline_claims.csv")


@pytest.fixture()
def current_claims() -> list[ClaimRecord]:
    """Load the 20-record current dataset shipped with the project."""
    return load_claims_csv(_DATASETS / "current_claims.csv")


@pytest.fixture()
def tmp_csv(tmp_path: Path):
    """Write a list of ClaimRecord objects to a temp CSV and return the path."""
    def _write(records: list[ClaimRecord], filename: str = "claims.csv") -> Path:
        path = tmp_path / filename
        if not records:
            # Header-only CSV
            path.write_text(
                "claim_id,patient_id,procedure_code,billed_cents,"
                "allowed_cents,paid_cents,status,adjudication_date\n",
                encoding="utf-8",
            )
            return path
        fieldnames = list(records[0].model_dump().keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for rec in records:
                row = rec.model_dump()
                # date must be serialised as ISO string for CSV round-trip
                row["adjudication_date"] = row["adjudication_date"].isoformat()
                writer.writerow(row)
        return path
    return _write
