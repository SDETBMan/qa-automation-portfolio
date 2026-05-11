"""Pydantic models for claims data diffing."""

from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict


class ClaimRecord(BaseModel):
    """A single healthcare claim record for adjudication comparison."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    claim_id: str
    patient_id: str
    procedure_code: str
    billed_cents: int
    allowed_cents: int
    paid_cents: int
    status: str
    adjudication_date: date


class FieldDiff(BaseModel):
    """A single field-level difference between two versions of a claim."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    field: str
    baseline_value: Any
    current_value: Any


class ClaimDiff(BaseModel):
    """Diff result for a single claim."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    claim_id: str
    change_type: str  # "added", "removed", "modified"
    field_diffs: list[FieldDiff] = []


class DiffReport(BaseModel):
    """Aggregate diff report across all claims."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    total_baseline: int
    total_current: int
    added: int
    removed: int
    modified: int
    unchanged: int
    diffs: list[ClaimDiff]
