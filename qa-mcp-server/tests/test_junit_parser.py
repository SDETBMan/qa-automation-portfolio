"""Tests for the parse_junit_xml MCP tool wrapper."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.junit_parser import parse_junit_xml


@pytest.mark.asyncio
async def test_parse_single_file(sample_xml_file: Path) -> None:
    """Single XML file produces correct summary counts."""
    result = json.loads(await parse_junit_xml(str(sample_xml_file)))

    assert result["summary"]["total"] == 3
    assert result["summary"]["passed"] == 1
    assert result["summary"]["failed"] == 1
    assert result["summary"]["skipped"] == 1


@pytest.mark.asyncio
async def test_parse_directory(sample_xml_dir: Path) -> None:
    """Directory of XML files aggregates all test results."""
    result = json.loads(await parse_junit_xml(str(sample_xml_dir)))

    # 3 files * 3 tests each = 9 total
    assert result["summary"]["total"] == 9
    assert len(result["results"]) == 9


@pytest.mark.asyncio
async def test_parse_result_fields(sample_xml_file: Path) -> None:
    """Each result has the expected fields."""
    result = json.loads(await parse_junit_xml(str(sample_xml_file)))

    first = result["results"][0]
    assert "suite" in first
    assert "name" in first
    assert "classname" in first
    assert "status" in first
    assert "time_s" in first
    assert "message" in first


@pytest.mark.asyncio
async def test_parse_nonexistent_path() -> None:
    """Non-existent path raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        await parse_junit_xml("/nonexistent/path/results.xml")


@pytest.mark.asyncio
async def test_parse_failure_message(sample_xml_file: Path) -> None:
    """Failed test case includes the failure message."""
    result = json.loads(await parse_junit_xml(str(sample_xml_file)))

    failed = [r for r in result["results"] if r["status"] == "failed"]
    assert len(failed) == 1
    assert failed[0]["message"] == "Expected error message"


@pytest.mark.asyncio
async def test_parse_skipped_message(sample_xml_file: Path) -> None:
    """Skipped test case includes the skip reason."""
    result = json.loads(await parse_junit_xml(str(sample_xml_file)))

    skipped = [r for r in result["results"] if r["status"] == "skipped"]
    assert len(skipped) == 1
    assert "Known issue" in skipped[0]["message"]
