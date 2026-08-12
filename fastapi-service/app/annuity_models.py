"""
annuity_models.py — Pydantic v2 models for MYGA (Multi-Year Guaranteed Annuity) endpoints.

Domain context:
  A MYGA is a fixed annuity with a guaranteed interest rate for a set term
  (typically 3, 5, 7, or 10 years).  All monetary values are stored as
  integer cents to prevent IEEE 754 floating-point contamination — the same
  invariant enforced by every production insurance ledger.

Models:
  AnnuityCreate       — POST request body (principal, rate, term, schedule)
  Annuity             — full policy record with computed maturity_date
  AccrualProjection   — projected value at a given date
  SurrenderQuote      — surrender value with charge and free-withdrawal breakdown
"""

from datetime import date

from pydantic import BaseModel, field_validator, model_validator


class AnnuityCreate(BaseModel):
    """Request body for POST /annuities."""

    principal_cents: int
    rate_bps: int
    term_years: int
    effective_date: date
    surrender_schedule_bps: list[int]

    @field_validator("principal_cents")
    @classmethod
    def principal_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("principal_cents must be positive")
        return v

    @field_validator("rate_bps")
    @classmethod
    def rate_in_range(cls, v: int) -> int:
        if v < 0 or v > 1000:
            raise ValueError("rate_bps must be between 0 and 1000")
        return v

    @field_validator("term_years")
    @classmethod
    def term_valid(cls, v: int) -> int:
        if v not in {3, 5, 7, 10}:
            raise ValueError("term_years must be one of 3, 5, 7, 10")
        return v

    @model_validator(mode="after")
    def schedule_matches_term(self) -> "AnnuityCreate":
        if len(self.surrender_schedule_bps) != self.term_years:
            raise ValueError(
                f"surrender_schedule_bps length ({len(self.surrender_schedule_bps)}) "
                f"must equal term_years ({self.term_years})"
            )
        return self


class Annuity(BaseModel):
    """Full policy record returned by GET/POST /annuities."""

    policy_id: str
    principal_cents: int
    rate_bps: int
    term_years: int
    effective_date: date
    maturity_date: date
    surrender_schedule_bps: list[int]


class AccrualProjection(BaseModel):
    """Projected accrued value at a specific date."""

    policy_id: str
    as_of_date: date
    principal_cents: int
    accrued_interest_cents: int
    accrued_value_cents: int
    completed_years: int

    @model_validator(mode="after")
    def guaranteed_minimum(self) -> "AccrualProjection":
        if self.accrued_value_cents < self.principal_cents:
            raise ValueError(
                "accrued_value_cents must be >= principal_cents (guaranteed minimum)"
            )
        return self


class SurrenderQuote(BaseModel):
    """Surrender value breakdown at a specific date."""

    policy_id: str
    as_of_date: date
    accrued_value_cents: int
    policy_year: int
    surrender_charge_bps: int
    surrender_charge_cents: int
    free_withdrawal_cents: int
    surrender_value_cents: int
