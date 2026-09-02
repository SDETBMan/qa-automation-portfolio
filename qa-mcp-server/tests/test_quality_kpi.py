"""Tests for the compute_quality_kpis MCP tool wrapper."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.quality_kpi import compute_quality_kpis


@pytest.mark.asyncio
async def test_kpis_from_xml_dir(sample_xml_dir: Path) -> None:
    """KPIs are computed from a directory of XML files."""
    result = json.loads(await compute_quality_kpis(str(sample_xml_dir)))

    assert "aggregate" in result
    assert "frameworks" in result
    assert result["aggregate"]["total_tests"] == 9
    assert 0 <= result["aggregate"]["overall_pass_rate"] <= 1


@pytest.mark.asyncio
async def test_kpis_pass_rate_calculation(sample_xml_dir: Path) -> None:
    """Pass rate matches expected ratio.

    3 runs * 3 tests = 9 total. Across the fixtures:
    - test_valid_login: passed 3x
    - test_invalid_creds: failed 2x, passed 1x
    - test_locked_user: skipped 3x
    So 4 passed out of 9 total => ~0.4444
    """
    result = json.loads(await compute_quality_kpis(str(sample_xml_dir)))

    agg = result["aggregate"]
    assert agg["total_passed"] == 4
    assert round(agg["overall_pass_rate"], 2) == 0.44


@pytest.mark.asyncio
async def test_kpis_framework_breakdown(sample_xml_dir: Path) -> None:
    """Framework list contains at least one entry with expected fields."""
    result = json.loads(await compute_quality_kpis(str(sample_xml_dir)))

    assert len(result["frameworks"]) >= 1
    fw = result["frameworks"][0]
    assert "pass_rate" in fw
    assert "failure_density" in fw
    assert "avg_duration_s" in fw
    assert "total_tests" in fw


@pytest.mark.asyncio
async def test_kpis_empty_dir(tmp_path: Path) -> None:
    """Empty directory returns zero-valued KPIs."""
    result = json.loads(await compute_quality_kpis(str(tmp_path)))

    assert result["aggregate"]["total_tests"] == 0
    assert result["aggregate"]["overall_pass_rate"] == 0.0
    assert result["frameworks"] == []


@pytest.mark.asyncio
async def test_kpis_not_a_directory() -> None:
    """Non-directory path raises NotADirectoryError."""
    with pytest.raises(NotADirectoryError):
        await compute_quality_kpis("/nonexistent/dir")
