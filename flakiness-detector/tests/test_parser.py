"""Tests for JUnit XML parser."""

from pathlib import Path

from flakiness.parser import parse_junit_xml, parse_directory

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def test_parse_single_file():
    result = parse_junit_xml(FIXTURES / "run-001.xml")
    assert result.run_id == "run-001"
    assert len(result.results) == 8


def test_parse_extracts_failures():
    result = parse_junit_xml(FIXTURES / "run-001.xml")
    failed = [r for r in result.results if r.status == "failed"]
    assert len(failed) == 1
    assert failed[0].name == "test_sort_products"


def test_parse_extracts_passed():
    result = parse_junit_xml(FIXTURES / "run-001.xml")
    passed = [r for r in result.results if r.status == "passed"]
    assert len(passed) == 7


def test_parse_directory_finds_all_files():
    runs = parse_directory(FIXTURES)
    assert len(runs) == 3


def test_parse_preserves_classname():
    result = parse_junit_xml(FIXTURES / "run-001.xml")
    api_tests = [r for r in result.results if "test_api" in r.classname]
    assert len(api_tests) == 2
