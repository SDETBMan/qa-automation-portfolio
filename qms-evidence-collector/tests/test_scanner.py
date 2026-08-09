"""Tests for the artifact scanner."""

import json
import pytest
from pathlib import Path

from collector.scanner import scan_repo, load_registry, ArtifactHit, ScanResult


@pytest.fixture
def registry():
    return load_registry()


@pytest.fixture
def mock_repo(tmp_path):
    """Create a mock repo structure with various artifact types."""
    # JUnit XML
    results_dir = tmp_path / "selenium-java" / "test-results"
    results_dir.mkdir(parents=True)
    (results_dir / "TEST-LoginTest.xml").write_text("<testsuites/>")

    # Coverage
    cypress_dir = tmp_path / "cypress"
    cypress_dir.mkdir()
    (cypress_dir / "coverage.xml").write_text("<coverage/>")

    # ZAP report
    (cypress_dir / "zap-report.json").write_text("{}")

    # Allure results
    allure_dir = tmp_path / "playwright" / "allure-results"
    allure_dir.mkdir(parents=True)
    (allure_dir / "result1.json").write_text("{}")

    # Pact contracts
    pact_dir = tmp_path / "pact-consumer" / "pacts"
    pact_dir.mkdir(parents=True)
    (pact_dir / "consumer-provider.json").write_text("{}")

    # k6 SLO report
    k6_dir = tmp_path / "fastapi-service" / "k6"
    k6_dir.mkdir(parents=True)
    (k6_dir / "k6-slo-report.json").write_text("{}")

    # Flakiness report
    flakiness_dir = tmp_path / "flakiness-detector"
    flakiness_dir.mkdir()
    (flakiness_dir / "flakiness-report.md").write_text("# Flakiness")

    # Drift baseline
    monitor_dir = tmp_path / "site-monitor"
    monitor_dir.mkdir()
    (monitor_dir / "baseline.json").write_text("{}")

    # Triage report
    triage_dir = tmp_path / "failure-triage"
    triage_dir.mkdir()
    (triage_dir / "triage_report.json").write_text("{}")

    # Dependabot config
    github_dir = tmp_path / ".github"
    github_dir.mkdir()
    (github_dir / "dependabot.yml").write_text("version: 2")

    return tmp_path


class TestScanRepo:
    def test_discovers_junit_xml(self, mock_repo, registry):
        result = scan_repo(mock_repo, registry)
        junit_hits = result.hits_by_type("junit_xml")
        assert len(junit_hits) >= 1
        assert any("TEST-LoginTest.xml" in h.file_path for h in junit_hits)

    def test_discovers_coverage(self, mock_repo, registry):
        result = scan_repo(mock_repo, registry)
        coverage_hits = result.hits_by_type("coverage_report")
        assert len(coverage_hits) >= 1

    def test_discovers_zap_report(self, mock_repo, registry):
        result = scan_repo(mock_repo, registry)
        zap_hits = result.hits_by_type("zap_report")
        assert len(zap_hits) >= 1

    def test_discovers_allure_results(self, mock_repo, registry):
        result = scan_repo(mock_repo, registry)
        allure_hits = result.hits_by_type("allure_report")
        assert len(allure_hits) >= 1

    def test_discovers_pact_contracts(self, mock_repo, registry):
        result = scan_repo(mock_repo, registry)
        pact_hits = result.hits_by_type("pact_contract")
        assert len(pact_hits) >= 1

    def test_discovers_k6_results(self, mock_repo, registry):
        result = scan_repo(mock_repo, registry)
        k6_hits = result.hits_by_type("k6_load_test")
        assert len(k6_hits) >= 1

    def test_discovers_flakiness_report(self, mock_repo, registry):
        result = scan_repo(mock_repo, registry)
        flakiness_hits = result.hits_by_type("flakiness_report")
        assert len(flakiness_hits) >= 1

    def test_discovers_drift_baseline(self, mock_repo, registry):
        result = scan_repo(mock_repo, registry)
        drift_hits = result.hits_by_type("drift_report")
        assert len(drift_hits) >= 1

    def test_detects_framework_from_path(self, mock_repo, registry):
        result = scan_repo(mock_repo, registry)
        selenium_hits = result.hits_by_framework("selenium-java")
        assert len(selenium_hits) >= 1

    def test_lists_frameworks_scanned(self, mock_repo, registry):
        result = scan_repo(mock_repo, registry)
        assert "selenium-java" in result.frameworks_scanned
        assert "cypress" in result.frameworks_scanned
        assert "playwright" in result.frameworks_scanned

    def test_artifact_types_found(self, mock_repo, registry):
        result = scan_repo(mock_repo, registry)
        types = result.artifact_types_found
        assert "junit_xml" in types
        assert "zap_report" in types

    def test_empty_repo_returns_no_hits(self, tmp_path, registry):
        result = scan_repo(tmp_path, registry)
        assert len(result.hits) == 0
        assert len(result.frameworks_scanned) == 0

    def test_skips_node_modules(self, tmp_path, registry):
        nm_dir = tmp_path / "cypress" / "node_modules" / "test-results"
        nm_dir.mkdir(parents=True)
        (nm_dir / "TEST-fake.xml").write_text("<testsuites/>")
        result = scan_repo(tmp_path, registry)
        junit_hits = result.hits_by_type("junit_xml")
        assert len(junit_hits) == 0


class TestLoadRegistry:
    def test_loads_default_registry(self):
        registry = load_registry()
        assert len(registry) > 0
        assert registry[0]["artifact_type"] == "junit_xml"

    def test_registry_has_required_fields(self):
        registry = load_registry()
        for mapping in registry:
            assert "artifact_type" in mapping
            assert "file_patterns" in mapping
            assert "clauses" in mapping
            assert "iso_9001" in mapping["clauses"]
            assert "soc2" in mapping["clauses"]

    def test_all_iso_clauses_have_rationale(self):
        registry = load_registry()
        for mapping in registry:
            for clause in mapping["clauses"].get("iso_9001", []):
                assert "rationale" in clause
                assert len(clause["rationale"]) > 10
