"""
annuity.py — MYGA (Multi-Year Guaranteed Annuity) API router.

Routes:
  POST /annuities                          — create a new policy (201)
  GET  /annuities/{policy_id}              — retrieve a policy (404 if missing)
  GET  /annuities/{policy_id}/projection   — compute accrued value at as_of_date
  GET  /annuities/{policy_id}/surrender    — compute surrender value at as_of_date

Design decisions:
  - All rate arithmetic uses Python's Decimal type to prevent IEEE 754 contamination.
  - Interest compounds annually from the effective_date (not creation date).
  - Surrender charges are indexed by 1-based policy year, not calendar year.
  - Post-maturity projections cap compounding at term_years (rate stops accruing).
  - Post-maturity surrender charges are zero (no penalty after term expires).
  - Free withdrawal is 10% of accrued value per year, penalty-free.
"""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, HTTPException, Query

from app.annuity_models import AccrualProjection, Annuity, AnnuityCreate, SurrenderQuote
from app.store import store

router = APIRouter(prefix="/annuities", tags=["annuities"])


# -- Internal helpers --------------------------------------------------------


def _completed_years(effective_date: date, as_of_date: date) -> int:
    """Full years elapsed since effective_date (for annual compounding)."""
    years = as_of_date.year - effective_date.year
    if (as_of_date.month, as_of_date.day) < (effective_date.month, effective_date.day):
        years -= 1
    return max(0, years)


def _policy_year(effective_date: date, as_of_date: date) -> int:
    """1-indexed policy year.  Year 1 starts on effective_date."""
    return _completed_years(effective_date, as_of_date) + 1


def _compute_accrued_value_cents(
    principal_cents: int, rate_bps: int, completed_years: int
) -> int:
    """principal * (1 + rate/10000)^years, rounded to integer cents."""
    principal = Decimal(principal_cents)
    rate = Decimal(rate_bps) / Decimal(10000)
    factor = (Decimal(1) + rate) ** completed_years
    return int((principal * factor).quantize(Decimal(1), rounding=ROUND_HALF_UP))


# -- Routes ------------------------------------------------------------------


@router.post("", response_model=Annuity, status_code=201)
def create_annuity(body: AnnuityCreate) -> Annuity:
    policy_id = store.next_annuity_id()
    maturity_date = body.effective_date.replace(
        year=body.effective_date.year + body.term_years
    )
    annuity = Annuity(
        policy_id=policy_id,
        principal_cents=body.principal_cents,
        rate_bps=body.rate_bps,
        term_years=body.term_years,
        effective_date=body.effective_date,
        maturity_date=maturity_date,
        surrender_schedule_bps=body.surrender_schedule_bps,
    )
    store.annuities[policy_id] = annuity
    return annuity


@router.get("/{policy_id}", response_model=Annuity)
def get_annuity(policy_id: str) -> Annuity:
    annuity = store.annuities.get(policy_id)
    if not annuity:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
    return annuity


@router.get("/{policy_id}/projection", response_model=AccrualProjection)
def get_projection(
    policy_id: str, as_of_date: date = Query(...)
) -> AccrualProjection:
    annuity = store.annuities.get(policy_id)
    if not annuity:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
    if as_of_date < annuity.effective_date:
        raise HTTPException(
            status_code=400, detail="as_of_date is before effective_date"
        )

    years = _completed_years(annuity.effective_date, as_of_date)
    capped_years = min(years, annuity.term_years)
    accrued_value = _compute_accrued_value_cents(
        annuity.principal_cents, annuity.rate_bps, capped_years
    )
    accrued_interest = accrued_value - annuity.principal_cents

    return AccrualProjection(
        policy_id=policy_id,
        as_of_date=as_of_date,
        principal_cents=annuity.principal_cents,
        accrued_interest_cents=accrued_interest,
        accrued_value_cents=accrued_value,
        completed_years=capped_years,
    )


@router.get("/{policy_id}/surrender", response_model=SurrenderQuote)
def get_surrender(
    policy_id: str, as_of_date: date = Query(...)
) -> SurrenderQuote:
    annuity = store.annuities.get(policy_id)
    if not annuity:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
    if as_of_date < annuity.effective_date:
        raise HTTPException(
            status_code=400, detail="as_of_date is before effective_date"
        )

    years = _completed_years(annuity.effective_date, as_of_date)
    capped_years = min(years, annuity.term_years)
    accrued_value = _compute_accrued_value_cents(
        annuity.principal_cents, annuity.rate_bps, capped_years
    )

    py = _policy_year(annuity.effective_date, as_of_date)

    # Post-maturity: zero surrender charge
    if py > annuity.term_years:
        surrender_charge_bps = 0
    else:
        surrender_charge_bps = annuity.surrender_schedule_bps[py - 1]

    # Free withdrawal: 10% of accrued value per year, penalty-free
    free_withdrawal_cents = int(
        (Decimal(accrued_value) * Decimal("0.10")).quantize(
            Decimal(1), rounding=ROUND_HALF_UP
        )
    )

    # Surrender charge applies to amount exceeding free withdrawal
    taxable_amount = max(0, accrued_value - free_withdrawal_cents)
    surrender_charge_cents = int(
        (Decimal(taxable_amount) * Decimal(surrender_charge_bps) / Decimal(10000))
        .quantize(Decimal(1), rounding=ROUND_HALF_UP)
    )

    surrender_value = accrued_value - surrender_charge_cents

    return SurrenderQuote(
        policy_id=policy_id,
        as_of_date=as_of_date,
        accrued_value_cents=accrued_value,
        policy_year=py,
        surrender_charge_bps=surrender_charge_bps,
        surrender_charge_cents=surrender_charge_cents,
        free_withdrawal_cents=free_withdrawal_cents,
        surrender_value_cents=surrender_value,
    )
