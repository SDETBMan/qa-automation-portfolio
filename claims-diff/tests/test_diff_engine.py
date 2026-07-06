"""Tests for core diff logic — the heart of claims adjudication comparison."""

from __future__ import annotations

from datetime import date

from differ.diff_engine import diff_claims
from differ.models import ClaimRecord


class TestIdenticalDatasets:
    """When datasets match, no diffs should be reported."""

    def test_identical_datasets_no_diffs(self, sample_claim):
        """Unchanged count equals total, diffs list empty."""
        claims = [sample_claim(), sample_claim(claim_id="CLM-002", patient_id="PAT-102")]
        report = diff_claims(claims, list(claims))
        assert report.added == 0
        assert report.removed == 0
        assert report.modified == 0
        assert report.unchanged == 2
        assert report.diffs == []


class TestAddedClaims:
    """Claims present in current but not baseline are flagged as added."""

    def test_added_claim_detected(self, sample_claim):
        baseline = [sample_claim()]
        current = [sample_claim(), sample_claim(claim_id="CLM-002", patient_id="PAT-102")]
        report = diff_claims(baseline, current)
        assert report.added == 1
        assert any(d.claim_id == "CLM-002" and d.change_type == "added" for d in report.diffs)


class TestRemovedClaims:
    """Claims present in baseline but not current are flagged as removed."""

    def test_removed_claim_detected(self, sample_claim):
        baseline = [sample_claim(), sample_claim(claim_id="CLM-002", patient_id="PAT-102")]
        current = [sample_claim()]
        report = diff_claims(baseline, current)
        assert report.removed == 1
        assert any(d.claim_id == "CLM-002" and d.change_type == "removed" for d in report.diffs)


class TestModifiedClaims:
    """Field-level changes detected on matching claim_ids."""

    def test_modified_billed_cents(self, sample_claim):
        """Amount change detected with field-level diff."""
        baseline = [sample_claim()]
        current = [sample_claim(billed_cents=20000)]
        report = diff_claims(baseline, current)
        assert report.modified == 1
        diff = report.diffs[0]
        assert diff.change_type == "modified"
        field_diff = next(fd for fd in diff.field_diffs if fd.field == "billed_cents")
        assert field_diff.baseline_value == 15000
        assert field_diff.current_value == 20000

    def test_modified_status(self, sample_claim):
        """Status change (pending -> paid) detected."""
        baseline = [sample_claim(status="pending")]
        current = [sample_claim(status="paid")]
        report = diff_claims(baseline, current)
        assert report.modified == 1
        field_diff = next(fd for fd in report.diffs[0].field_diffs if fd.field == "status")
        assert field_diff.baseline_value == "pending"
        assert field_diff.current_value == "paid"

    def test_modified_adjudication_date(self, sample_claim):
        """Date change detected."""
        baseline = [sample_claim()]
        current = [sample_claim(adjudication_date=date(2026, 2, 1))]
        report = diff_claims(baseline, current)
        assert report.modified == 1
        field_diff = next(
            fd for fd in report.diffs[0].field_diffs if fd.field == "adjudication_date"
        )
        assert field_diff.baseline_value == date(2026, 1, 15)
        assert field_diff.current_value == date(2026, 2, 1)

    def test_multiple_field_changes(self, sample_claim):
        """Single claim with 2+ field diffs reports all of them."""
        baseline = [sample_claim()]
        current = [sample_claim(billed_cents=20000, status="denied")]
        report = diff_claims(baseline, current)
        assert report.modified == 1
        fields_changed = {fd.field for fd in report.diffs[0].field_diffs}
        assert "billed_cents" in fields_changed
        assert "status" in fields_changed


class TestMixedChangeTypes:
    """Multiple change types in a single diff run."""

    def test_multiple_change_types(self, sample_claim):
        """Mix of added + removed + modified in one run."""
        baseline = [
            sample_claim(),
            sample_claim(claim_id="CLM-002", patient_id="PAT-102"),
        ]
        current = [
            sample_claim(billed_cents=20000),  # modified
            sample_claim(claim_id="CLM-003", patient_id="PAT-103"),  # added (CLM-002 removed)
        ]
        report = diff_claims(baseline, current)
        assert report.modified == 1
        assert report.removed == 1
        assert report.added == 1


class TestEmptyDatasets:
    """Edge cases with empty datasets."""

    def test_empty_baseline(self, sample_claim):
        """All current claims reported as added."""
        current = [sample_claim(), sample_claim(claim_id="CLM-002", patient_id="PAT-102")]
        report = diff_claims([], current)
        assert report.added == 2
        assert report.removed == 0
        assert report.total_baseline == 0

    def test_empty_current(self, sample_claim):
        """All baseline claims reported as removed."""
        baseline = [sample_claim(), sample_claim(claim_id="CLM-002", patient_id="PAT-102")]
        report = diff_claims(baseline, [])
        assert report.removed == 2
        assert report.added == 0
        assert report.total_current == 0

    def test_both_empty(self):
        """Zero counts, no diffs."""
        report = diff_claims([], [])
        assert report.total_baseline == 0
        assert report.total_current == 0
        assert report.unchanged == 0
        assert report.diffs == []


class TestRealDatasets:
    """Integration test against the actual shipped CSV datasets."""

    def test_real_dataset_produces_expected_diffs(self, baseline_claims, current_claims):
        """Run against actual CSVs — expect 5 diffs (3 modified, 1 added, 1 removed)."""
        report = diff_claims(baseline_claims, current_claims)

        assert report.total_baseline == 20
        assert report.total_current == 20
        assert report.modified == 3
        assert report.added == 1
        assert report.removed == 1
        assert report.unchanged == 16
        assert len(report.diffs) == 5

        change_types = {d.change_type for d in report.diffs}
        assert change_types == {"modified", "added", "removed"}

        # Verify specific known diffs
        added_ids = {d.claim_id for d in report.diffs if d.change_type == "added"}
        removed_ids = {d.claim_id for d in report.diffs if d.change_type == "removed"}
        assert added_ids == {"CLM-021"}
        assert removed_ids == {"CLM-020"}
