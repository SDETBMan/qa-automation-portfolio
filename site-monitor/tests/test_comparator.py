"""Tests for the comparator module."""

import json
import tempfile
from pathlib import Path

from monitor.comparator import compare, check_monitored, DriftReport


class TestCompare:
    def test_no_drift(self):
        baseline = {"ids": ["a", "b"], "classes": ["c"], "data_test": ["d"]}
        current = {"ids": ["a", "b"], "classes": ["c"], "data_test": ["d"]}
        report = compare(baseline, current)
        assert not report.has_drift
        assert report.severity == "none"
        assert report.total_removed == 0
        assert report.total_added == 0

    def test_added_selectors(self):
        baseline = {"ids": ["a"], "classes": [], "data_test": []}
        current = {"ids": ["a", "b"], "classes": ["new-class"], "data_test": []}
        report = compare(baseline, current)
        assert report.has_drift
        assert report.severity == "info"
        assert "b" in report.added_ids
        assert "new-class" in report.added_classes
        assert report.total_added == 2
        assert report.total_removed == 0

    def test_removed_selectors(self):
        baseline = {"ids": ["a", "b"], "classes": ["c"], "data_test": ["d"]}
        current = {"ids": ["a"], "classes": [], "data_test": ["d"]}
        report = compare(baseline, current)
        assert report.has_drift
        assert report.severity == "critical"
        assert "b" in report.removed_ids
        assert "c" in report.removed_classes
        assert report.total_removed == 2

    def test_mixed_additions_and_removals(self):
        baseline = {"ids": ["a", "b"], "classes": ["c"], "data_test": ["d"]}
        current = {"ids": ["a", "x"], "classes": ["c", "y"], "data_test": []}
        report = compare(baseline, current)
        assert report.has_drift
        assert report.severity == "critical"
        assert "b" in report.removed_ids
        assert "x" in report.added_ids
        assert "y" in report.added_classes
        assert "d" in report.removed_data_test

    def test_empty_baselines(self):
        baseline = {"ids": [], "classes": [], "data_test": []}
        current = {"ids": ["new"], "classes": [], "data_test": []}
        report = compare(baseline, current)
        assert report.has_drift
        assert report.severity == "info"


class TestCheckMonitored:
    def _write_registry(self, tmp_dir: Path) -> Path:
        registry = {
            "monitored": {
                "ids": {
                    "user-name": ["cypress", "selenium-java"],
                    "login-button": ["cypress", "playwright"],
                },
                "classes": {
                    "inventory_item": ["cypress"],
                },
                "data_test": {
                    "error": ["selenium-java"],
                },
            }
        }
        path = tmp_dir / "selectors.json"
        path.write_text(json.dumps(registry), encoding="utf-8")
        return path

    def test_identifies_affected_frameworks(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = self._write_registry(Path(tmp))
            report = DriftReport(
                removed_ids=["user-name"],
                removed_classes=["inventory_item"],
                removed_data_test=[],
            )
            affected = check_monitored(report, registry_path)
            assert len(affected) == 2
            assert affected[0]["selector"] == "user-name"
            assert "cypress" in affected[0]["frameworks"]
            assert affected[1]["selector"] == "inventory_item"

    def test_unmonitored_selectors_not_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = self._write_registry(Path(tmp))
            report = DriftReport(
                removed_ids=["unknown-id"],
                removed_classes=[],
                removed_data_test=[],
            )
            affected = check_monitored(report, registry_path)
            assert affected == []

    def test_missing_registry_returns_empty(self):
        report = DriftReport(removed_ids=["user-name"])
        affected = check_monitored(report, "/nonexistent/path.json")
        assert affected == []

    def test_data_test_affected(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = self._write_registry(Path(tmp))
            report = DriftReport(
                removed_ids=[],
                removed_classes=[],
                removed_data_test=["error"],
            )
            affected = check_monitored(report, registry_path)
            assert len(affected) == 1
            assert affected[0]["type"] == "data-test"
            assert "selenium-java" in affected[0]["frameworks"]
