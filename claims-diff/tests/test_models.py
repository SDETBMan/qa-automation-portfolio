"""Tests for Pydantic model validation — healthcare data integrity."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from differ.models import ClaimDiff, ClaimRecord, DiffReport, FieldDiff


class TestClaimRecordValidation:
    """Proves the schema enforces healthcare data integrity."""

    def test_valid_claim_creation(self, sample_claim):
        """All fields accepted, frozen model works."""
        claim = sample_claim()
        assert claim.claim_id == "CLM-001"
        assert claim.billed_cents == 15000
        assert claim.adjudication_date == date(2026, 1, 15)

    def test_extra_fields_rejected(self):
        """extra='forbid' blocks unexpected columns."""
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ClaimRecord(
                claim_id="CLM-001",
                patient_id="PAT-101",
                procedure_code="99213",
                billed_cents=15000,
                allowed_cents=12000,
                paid_cents=9600,
                status="paid",
                adjudication_date=date(2026, 1, 15),
                surprise_field="oops",
            )

    def test_invalid_date_rejected(self):
        """Non-ISO date string raises ValidationError."""
        with pytest.raises(ValidationError):
            ClaimRecord(
                claim_id="CLM-001",
                patient_id="PAT-101",
                procedure_code="99213",
                billed_cents=15000,
                allowed_cents=12000,
                paid_cents=9600,
                status="paid",
                adjudication_date="not-a-date",
            )

    def test_negative_billed_cents_rejected(self):
        """billed_cents < 0 raises validation error (ge=0 constraint)."""
        with pytest.raises(ValidationError, match="greater_than_equal"):
            ClaimRecord(
                claim_id="CLM-001",
                patient_id="PAT-101",
                procedure_code="99213",
                billed_cents=-100,
                allowed_cents=12000,
                paid_cents=9600,
                status="paid",
                adjudication_date=date(2026, 1, 15),
            )

    def test_status_enum_enforcement(self):
        """Invalid status like 'refunded' rejected (Literal constraint)."""
        with pytest.raises(ValidationError, match="literal_error"):
            ClaimRecord(
                claim_id="CLM-001",
                patient_id="PAT-101",
                procedure_code="99213",
                billed_cents=15000,
                allowed_cents=12000,
                paid_cents=9600,
                status="refunded",
                adjudication_date=date(2026, 1, 15),
            )

    def test_procedure_code_format(self):
        """Invalid procedure code like 'XXXXX' rejected (regex validator)."""
        with pytest.raises(ValidationError, match="string_pattern_mismatch"):
            ClaimRecord(
                claim_id="CLM-001",
                patient_id="PAT-101",
                procedure_code="XXXXX",
                billed_cents=15000,
                allowed_cents=12000,
                paid_cents=9600,
                status="paid",
                adjudication_date=date(2026, 1, 15),
            )

    def test_claim_id_format(self):
        """Invalid claim_id rejected (must match CLM-NNN pattern)."""
        with pytest.raises(ValidationError, match="string_pattern_mismatch"):
            ClaimRecord(
                claim_id="INVALID",
                patient_id="PAT-101",
                procedure_code="99213",
                billed_cents=15000,
                allowed_cents=12000,
                paid_cents=9600,
                status="paid",
                adjudication_date=date(2026, 1, 15),
            )

    def test_patient_id_format(self):
        """Invalid patient_id rejected (must match PAT-NNN pattern)."""
        with pytest.raises(ValidationError, match="string_pattern_mismatch"):
            ClaimRecord(
                claim_id="CLM-001",
                patient_id="INVALID",
                procedure_code="99213",
                billed_cents=15000,
                allowed_cents=12000,
                paid_cents=9600,
                status="paid",
                adjudication_date=date(2026, 1, 15),
            )


class TestFieldDiffModel:
    """FieldDiff stores baseline vs current values correctly."""

    def test_field_diff_creation(self):
        fd = FieldDiff(field="billed_cents", baseline_value=15000, current_value=20000)
        assert fd.field == "billed_cents"
        assert fd.baseline_value == 15000
        assert fd.current_value == 20000


class TestDiffReportModel:
    """DiffReport immutability and structure."""

    def test_diff_report_immutability(self):
        """Frozen model prevents mutation."""
        report = DiffReport(
            total_baseline=20,
            total_current=20,
            added=0,
            removed=0,
            modified=0,
            unchanged=20,
            diffs=[],
        )
        with pytest.raises(ValidationError):
            report.total_baseline = 999


class TestClaimRecordEquality:
    """ClaimRecord equality and serialization."""

    def test_identical_records_compare_equal(self, sample_claim):
        """Two identical records compare equal."""
        a = sample_claim()
        b = sample_claim()
        assert a == b

    def test_serialization_round_trip(self, sample_claim):
        """model_dump() -> ClaimRecord(**data) produces identical record."""
        original = sample_claim()
        data = original.model_dump()
        restored = ClaimRecord(**data)
        assert original == restored
