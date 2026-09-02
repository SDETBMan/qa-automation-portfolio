"""Tests for the diff_claims MCP tool wrapper."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.claims_diff import diff_claims


@pytest.mark.asyncio
async def test_diff_detects_changes(claims_csv_pair: tuple[Path, Path]) -> None:
    """Diff detects added, removed, and modified claims."""
    baseline, current = claims_csv_pair
    result = json.loads(await diff_claims(str(baseline), str(current)))

    assert result["total_baseline"] == 3
    assert result["total_current"] == 3
    assert result["unchanged"] == 1  # CLM-001
    assert result["modified"] == 1   # CLM-002 (paid_cents changed)
    assert result["removed"] == 1    # CLM-003
    assert result["added"] == 1      # CLM-004


@pytest.mark.asyncio
async def test_diff_field_level_detail(claims_csv_pair: tuple[Path, Path]) -> None:
    """Modified claim includes field-level diff details."""
    baseline, current = claims_csv_pair
    result = json.loads(await diff_claims(str(baseline), str(current)))

    modified = [d for d in result["diffs"] if d["change_type"] == "modified"]
    assert len(modified) == 1
    assert modified[0]["claim_id"] == "CLM-002"
    assert len(modified[0]["field_diffs"]) >= 1

    paid_diff = [
        fd for fd in modified[0]["field_diffs"] if fd["field"] == "paid_cents"
    ]
    assert len(paid_diff) == 1
    assert paid_diff[0]["baseline_value"] == "16000"
    assert paid_diff[0]["current_value"] == "18000"


@pytest.mark.asyncio
async def test_diff_identical_files(tmp_path: Path) -> None:
    """Identical files produce zero diffs."""
    csv_content = (
        "claim_id,patient_id,procedure_code,billed_cents,"
        "allowed_cents,paid_cents,status,adjudication_date\n"
        "CLM-001,PAT-101,99213,15000,12000,9600,paid,2026-01-15\n"
    )
    f1 = tmp_path / "a.csv"
    f2 = tmp_path / "b.csv"
    f1.write_text(csv_content, encoding="utf-8")
    f2.write_text(csv_content, encoding="utf-8")

    result = json.loads(await diff_claims(str(f1), str(f2)))

    assert result["added"] == 0
    assert result["removed"] == 0
    assert result["modified"] == 0
    assert result["unchanged"] == 1


@pytest.mark.asyncio
async def test_diff_baseline_not_found() -> None:
    """Missing baseline file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        await diff_claims("/nonexistent/baseline.csv", "/nonexistent/current.csv")


@pytest.mark.asyncio
async def test_diff_current_not_found(tmp_path: Path) -> None:
    """Missing current file raises FileNotFoundError."""
    baseline = tmp_path / "baseline.csv"
    baseline.write_text(
        "claim_id,patient_id,procedure_code,billed_cents,"
        "allowed_cents,paid_cents,status,adjudication_date\n",
        encoding="utf-8",
    )
    with pytest.raises(FileNotFoundError):
        await diff_claims(str(baseline), "/nonexistent/current.csv")
