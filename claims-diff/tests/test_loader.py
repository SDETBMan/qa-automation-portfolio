"""Tests for CSV loading and validation."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from differ.loader import load_claims_csv


class TestValidCsvLoading:
    """Happy-path CSV loading."""

    def test_valid_csv_loads(self, baseline_claims):
        """20 records from baseline_claims.csv."""
        assert len(baseline_claims) == 20

    def test_field_types_correct(self, baseline_claims):
        """claim_id is str, billed_cents is int, adjudication_date is date."""
        first = baseline_claims[0]
        assert isinstance(first.claim_id, str)
        assert isinstance(first.billed_cents, int)
        assert isinstance(first.adjudication_date, date)


class TestCsvEdgeCases:
    """Error handling and edge cases in CSV loading."""

    def test_missing_column_raises_error(self, tmp_path):
        """CSV without claim_id column fails."""
        csv_file = tmp_path / "bad.csv"
        csv_file.write_text(
            "patient_id,procedure_code,billed_cents,allowed_cents,paid_cents,status,adjudication_date\n"
            "PAT-101,99213,15000,12000,9600,paid,2026-01-15\n",
            encoding="utf-8",
        )
        with pytest.raises(KeyError):
            load_claims_csv(csv_file)

    def test_empty_csv_returns_empty_list(self, tmp_path):
        """Header-only CSV loads as []."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text(
            "claim_id,patient_id,procedure_code,billed_cents,"
            "allowed_cents,paid_cents,status,adjudication_date\n",
            encoding="utf-8",
        )
        result = load_claims_csv(csv_file)
        assert result == []

    def test_non_numeric_cents_raises_error(self, tmp_path):
        """billed_cents='abc' fails on int conversion."""
        csv_file = tmp_path / "bad_cents.csv"
        csv_file.write_text(
            "claim_id,patient_id,procedure_code,billed_cents,allowed_cents,paid_cents,status,adjudication_date\n"
            "CLM-001,PAT-101,99213,abc,12000,9600,paid,2026-01-15\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError):
            load_claims_csv(csv_file)

    def test_file_not_found_raises_error(self):
        """Missing path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_claims_csv(Path("/nonexistent/path/claims.csv"))
