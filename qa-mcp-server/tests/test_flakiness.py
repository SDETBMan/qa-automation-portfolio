"""Tests for the analyze_flakiness MCP tool wrapper."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.flakiness import analyze_flakiness


@pytest.mark.asyncio
async def test_flakiness_detects_flaky_test(sample_xml_dir: Path) -> None:
    """test_invalid_creds fails in runs 1 and 3, passes in run 2 => flaky."""
    result = json.loads(await analyze_flakiness(str(sample_xml_dir)))

    assert result["total_tests"] == 3
    assert result["total_runs"] == 3
    assert result["total_flaky"] >= 1

    # The flaky test should appear in quarantine or monitor
    all_flaky = result["quarantine_recommended"] + result["monitor"]
    flaky_keys = [t["test_key"] for t in all_flaky]
    assert any("test_invalid_creds" in k for k in flaky_keys)


@pytest.mark.asyncio
async def test_flakiness_stable_test_not_flagged(sample_xml_dir: Path) -> None:
    """test_valid_login passes in all 3 runs => not flaky."""
    result = json.loads(await analyze_flakiness(str(sample_xml_dir)))

    all_flaky = result["quarantine_recommended"] + result["monitor"]
    flaky_keys = [t["test_key"] for t in all_flaky]
    assert not any("test_valid_login" in k for k in flaky_keys)


@pytest.mark.asyncio
async def test_flakiness_custom_threshold(sample_xml_dir: Path) -> None:
    """Higher threshold moves tests from quarantine to monitor."""
    strict = json.loads(await analyze_flakiness(str(sample_xml_dir), threshold=0.1))
    relaxed = json.loads(await analyze_flakiness(str(sample_xml_dir), threshold=0.9))

    assert len(strict["quarantine_recommended"]) >= len(
        relaxed["quarantine_recommended"]
    )


@pytest.mark.asyncio
async def test_flakiness_empty_dir(tmp_path: Path) -> None:
    """Empty directory returns zero counts."""
    result = json.loads(await analyze_flakiness(str(tmp_path)))

    assert result["total_tests"] == 0
    assert result["total_flaky"] == 0
    assert result["total_runs"] == 0


@pytest.mark.asyncio
async def test_flakiness_not_a_directory() -> None:
    """Non-directory path raises NotADirectoryError."""
    with pytest.raises(NotADirectoryError):
        await analyze_flakiness("/nonexistent/dir")
