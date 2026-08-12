"""
test_annuity.py — MYGA annuity endpoint tests.

Covers:
  - Seed data presence after reset
  - GET / POST round-trip
  - Accrual projection with hand-computed expected values
  - Surrender schedule lookup and charge calculation
  - Integer cents invariants on all monetary fields
  - Validation: invalid term, mismatched schedule, negative principal
"""

import pytest
from decimal import Decimal, ROUND_HALF_UP


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _expected_accrued(principal_cents: int, rate_bps: int, years: int) -> int:
    """Mirror the server's Decimal math for hand-verified expected values."""
    principal = Decimal(principal_cents)
    rate = Decimal(rate_bps) / Decimal(10000)
    factor = (Decimal(1) + rate) ** years
    return int((principal * factor).quantize(Decimal(1), rounding=ROUND_HALF_UP))


# ---------------------------------------------------------------------------
# Seed data tests
# ---------------------------------------------------------------------------


class TestSeedData:
    """Verify seed policies exist after store.reset()."""

    def test_seed_myga_001_exists(self, client):
        r = client.get("/annuities/MYGA-001")
        assert r.status_code == 200
        data = r.json()
        assert data["policy_id"] == "MYGA-001"
        assert data["principal_cents"] == 10_000_000
        assert data["rate_bps"] == 450
        assert data["term_years"] == 5
        assert data["effective_date"] == "2023-01-15"
        assert data["maturity_date"] == "2028-01-15"

    def test_seed_myga_002_exists(self, client):
        r = client.get("/annuities/MYGA-002")
        assert r.status_code == 200
        data = r.json()
        assert data["principal_cents"] == 25_000_000
        assert data["rate_bps"] == 525
        assert data["term_years"] == 7

    def test_seed_myga_003_exists(self, client):
        r = client.get("/annuities/MYGA-003")
        assert r.status_code == 200
        data = r.json()
        assert data["principal_cents"] == 5_000_000
        assert data["rate_bps"] == 375
        assert data["term_years"] == 3

    def test_missing_policy_returns_404(self, client):
        r = client.get("/annuities/MYGA-999")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# POST / GET round-trip
# ---------------------------------------------------------------------------


class TestCreatePolicy:
    """POST /annuities creates a policy and GET retrieves it."""

    def test_create_returns_201(self, client):
        body = {
            "principal_cents": 20_000_000,
            "rate_bps": 400,
            "term_years": 5,
            "effective_date": "2025-01-01",
            "surrender_schedule_bps": [500, 400, 300, 200, 100],
        }
        r = client.post("/annuities", json=body)
        assert r.status_code == 201
        data = r.json()
        assert data["policy_id"].startswith("MYGA-")
        assert data["principal_cents"] == 20_000_000
        assert data["maturity_date"] == "2030-01-01"

    def test_create_then_get_round_trip(self, client):
        body = {
            "principal_cents": 7_500_000,
            "rate_bps": 350,
            "term_years": 3,
            "effective_date": "2025-06-15",
            "surrender_schedule_bps": [400, 200, 100],
        }
        created = client.post("/annuities", json=body).json()
        fetched = client.get(f"/annuities/{created['policy_id']}").json()
        assert fetched == created


# ---------------------------------------------------------------------------
# Validation (422)
# ---------------------------------------------------------------------------


class TestValidation:
    """Pydantic validators reject invalid input with 422."""

    def test_invalid_term_rejected(self, client):
        body = {
            "principal_cents": 10_000_000,
            "rate_bps": 400,
            "term_years": 4,  # not in {3, 5, 7, 10}
            "effective_date": "2025-01-01",
            "surrender_schedule_bps": [500, 400, 300, 200],
        }
        r = client.post("/annuities", json=body)
        assert r.status_code == 422

    def test_mismatched_schedule_rejected(self, client):
        body = {
            "principal_cents": 10_000_000,
            "rate_bps": 400,
            "term_years": 5,
            "effective_date": "2025-01-01",
            "surrender_schedule_bps": [500, 400, 300],  # length 3 != term 5
        }
        r = client.post("/annuities", json=body)
        assert r.status_code == 422

    def test_negative_principal_rejected(self, client):
        body = {
            "principal_cents": -100,
            "rate_bps": 400,
            "term_years": 5,
            "effective_date": "2025-01-01",
            "surrender_schedule_bps": [500, 400, 300, 200, 100],
        }
        r = client.post("/annuities", json=body)
        assert r.status_code == 422

    def test_rate_above_1000_rejected(self, client):
        body = {
            "principal_cents": 10_000_000,
            "rate_bps": 1500,  # > 1000
            "term_years": 5,
            "effective_date": "2025-01-01",
            "surrender_schedule_bps": [500, 400, 300, 200, 100],
        }
        r = client.post("/annuities", json=body)
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# Accrual projection
# ---------------------------------------------------------------------------


class TestProjection:
    """GET /annuities/{id}/projection returns correct accrued values."""

    def test_zero_years_equals_principal(self, client):
        """On effective_date, accrued value equals principal (0 years compounded)."""
        r = client.get("/annuities/MYGA-001/projection?as_of_date=2023-01-15")
        assert r.status_code == 200
        data = r.json()
        assert data["completed_years"] == 0
        assert data["accrued_value_cents"] == 10_000_000
        assert data["accrued_interest_cents"] == 0

    def test_one_year_accrual(self, client):
        """After 1 full year: $100k * 1.045 = $104,500."""
        r = client.get("/annuities/MYGA-001/projection?as_of_date=2024-01-15")
        assert r.status_code == 200
        data = r.json()
        assert data["completed_years"] == 1
        expected = _expected_accrued(10_000_000, 450, 1)
        assert data["accrued_value_cents"] == expected
        assert data["accrued_value_cents"] == 10_450_000

    def test_two_year_accrual(self, client):
        """After 2 full years: $100k * 1.045^2 = $109,202.50 → 10_920_250 cents."""
        r = client.get("/annuities/MYGA-001/projection?as_of_date=2025-01-15")
        assert r.status_code == 200
        data = r.json()
        assert data["completed_years"] == 2
        expected = _expected_accrued(10_000_000, 450, 2)
        assert data["accrued_value_cents"] == expected

    def test_mid_year_equals_last_anniversary(self, client):
        """Mid-year date should use completed years (annual compounding)."""
        # 2024-07-01 is between anniversary 1 (2024-01-15) and 2 (2025-01-15)
        r = client.get("/annuities/MYGA-001/projection?as_of_date=2024-07-01")
        assert r.status_code == 200
        data = r.json()
        assert data["completed_years"] == 1
        assert data["accrued_value_cents"] == _expected_accrued(10_000_000, 450, 1)

    def test_post_maturity_caps_at_term(self, client):
        """After maturity, compounding caps at term_years (rate stops accruing)."""
        # MYGA-001 matures 2028-01-15 (5yr).  Query 2030-01-15 = 7 years elapsed.
        r = client.get("/annuities/MYGA-001/projection?as_of_date=2030-01-15")
        assert r.status_code == 200
        data = r.json()
        assert data["completed_years"] == 5  # capped at term
        assert data["accrued_value_cents"] == _expected_accrued(10_000_000, 450, 5)

    def test_pre_effective_date_returns_400(self, client):
        r = client.get("/annuities/MYGA-001/projection?as_of_date=2022-12-31")
        assert r.status_code == 400

    def test_projection_missing_policy_returns_404(self, client):
        r = client.get("/annuities/MYGA-999/projection?as_of_date=2025-01-01")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Integer cents invariant
# ---------------------------------------------------------------------------


class TestIntegerCents:
    """Every monetary field must be an integer (no float contamination)."""

    def test_projection_fields_are_integers(self, client):
        r = client.get("/annuities/MYGA-001/projection?as_of_date=2025-01-15")
        data = r.json()
        assert isinstance(data["principal_cents"], int)
        assert isinstance(data["accrued_interest_cents"], int)
        assert isinstance(data["accrued_value_cents"], int)

    def test_surrender_fields_are_integers(self, client):
        r = client.get("/annuities/MYGA-001/surrender?as_of_date=2025-01-15")
        data = r.json()
        assert isinstance(data["accrued_value_cents"], int)
        assert isinstance(data["surrender_charge_cents"], int)
        assert isinstance(data["free_withdrawal_cents"], int)
        assert isinstance(data["surrender_value_cents"], int)

    def test_accrued_value_gte_principal(self, client):
        """Guaranteed minimum: accrued value is always >= principal."""
        r = client.get("/annuities/MYGA-001/projection?as_of_date=2025-01-15")
        data = r.json()
        assert data["accrued_value_cents"] >= data["principal_cents"]


# ---------------------------------------------------------------------------
# Surrender value
# ---------------------------------------------------------------------------


class TestSurrender:
    """GET /annuities/{id}/surrender returns correct surrender breakdown."""

    def test_policy_year_1_charge(self, client):
        """In year 1, MYGA-001 surrender charge = 500 bps (5%)."""
        # 2023-06-01 is in policy year 1
        r = client.get("/annuities/MYGA-001/surrender?as_of_date=2023-06-01")
        assert r.status_code == 200
        data = r.json()
        assert data["policy_year"] == 1
        assert data["surrender_charge_bps"] == 500

    def test_policy_year_3_charge(self, client):
        """In year 3, MYGA-001 surrender charge = 300 bps (3%)."""
        # 2025-06-01: 2 full years completed → policy year 3
        r = client.get("/annuities/MYGA-001/surrender?as_of_date=2025-06-01")
        assert r.status_code == 200
        data = r.json()
        assert data["policy_year"] == 3
        assert data["surrender_charge_bps"] == 300

    def test_post_term_zero_charge(self, client):
        """After term expires, surrender charge is 0."""
        r = client.get("/annuities/MYGA-001/surrender?as_of_date=2029-01-15")
        assert r.status_code == 200
        data = r.json()
        assert data["policy_year"] > 5
        assert data["surrender_charge_bps"] == 0
        assert data["surrender_charge_cents"] == 0

    def test_free_withdrawal_10_percent(self, client):
        """Free withdrawal is 10% of accrued value."""
        r = client.get("/annuities/MYGA-001/surrender?as_of_date=2024-01-15")
        assert r.status_code == 200
        data = r.json()
        accrued = data["accrued_value_cents"]
        expected_free = int(
            (Decimal(accrued) * Decimal("0.10")).quantize(
                Decimal(1), rounding=ROUND_HALF_UP
            )
        )
        assert data["free_withdrawal_cents"] == expected_free

    def test_surrender_value_formula(self, client):
        """surrender_value = accrued_value - surrender_charge."""
        r = client.get("/annuities/MYGA-001/surrender?as_of_date=2024-06-01")
        data = r.json()
        assert data["surrender_value_cents"] == (
            data["accrued_value_cents"] - data["surrender_charge_cents"]
        )

    def test_surrender_pre_effective_returns_400(self, client):
        r = client.get("/annuities/MYGA-001/surrender?as_of_date=2022-12-31")
        assert r.status_code == 400

    def test_surrender_missing_policy_returns_404(self, client):
        r = client.get("/annuities/MYGA-999/surrender?as_of_date=2025-01-01")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# MYGA-002 cross-check (different rate + term)
# ---------------------------------------------------------------------------


class TestMYGA002:
    """Cross-check projections against MYGA-002 ($250k, 5.25%, 7yr)."""

    def test_one_year_accrual(self, client):
        """$250k * 1.0525 = $263,125.00 → 26_312_500 cents."""
        r = client.get("/annuities/MYGA-002/projection?as_of_date=2023-06-01")
        data = r.json()
        assert data["completed_years"] == 1
        assert data["accrued_value_cents"] == _expected_accrued(25_000_000, 525, 1)

    def test_surrender_year_1_700_bps(self, client):
        r = client.get("/annuities/MYGA-002/surrender?as_of_date=2022-12-01")
        data = r.json()
        assert data["policy_year"] == 1
        assert data["surrender_charge_bps"] == 700
