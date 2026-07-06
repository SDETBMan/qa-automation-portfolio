"""Pydantic models for claims data diffing."""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ClaimRecord(BaseModel):
    """A single healthcare claim record for adjudication comparison."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    claim_id: str = Field(pattern=r"^CLM-\d{3,}$")
    patient_id: str = Field(pattern=r"^PAT-\d{3,}$")
    procedure_code: str = Field(pattern=r"^\d{5}$")
    billed_cents: int = Field(ge=0)
    allowed_cents: int = Field(ge=0)
    paid_cents: int = Field(ge=0)
    status: Literal["paid", "denied", "pending"]
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
