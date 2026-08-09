"""Tests for the clause mapper."""

import pytest

from collector.scanner import ArtifactHit, ScanResult, load_registry
from collector.mapper import map_to_clauses, group_by_clause, ComplianceMap


@pytest.fixture
def registry():
    return load_registry()


@pytest.fixture
def sample_scan_result() -> ScanResult:
    """Scan result with representative artifact types."""
    result = ScanResult(root_dir="/mock/repo")
    result.frameworks_scanned = ["selenium-java", "cypress", "playwright"]
    result.hits = [
        ArtifactHit("junit_xml", "selenium-java/test-results/TEST-Login.xml", "selenium-java", 1024),
        ArtifactHit("junit_xml", "cypress/test-results/results.xml", "cypress", 2048),
        ArtifactHit("zap_report", "cypress/zap-report.json", "cypress", 4096),
        ArtifactHit("coverage_report", "cypress/coverage.xml", "cypress", 512),
        ArtifactHit("k6_load_test", "fastapi-service/k6/k6-slo-report.json", "fastapi-service", 768),
        ArtifactHit("pact_contract", "pact-consumer/pacts/consumer-provider.json", "pact-consumer", 1500),
        ArtifactHit("flakiness_report", "flakiness-detector/flakiness-report.md", "flakiness-detector", 300),
        ArtifactHit("drift_report", "site-monitor/baseline.json", "site-monitor", 900),
        ArtifactHit("triage_report", "failure-triage/triage_report.json", "failure-triage", 600),
    ]
    return result


class TestMapToClauses:
    def test_produces_iso_9001_evidence(self, sample_scan_result, registry):
        compliance_map = map_to_clauses(sample_scan_result, registry)
        iso_clauses = compliance_map.iso_9001_clauses
        assert len(iso_clauses) > 0

    def test_produces_soc2_evidence(self, sample_scan_result, registry):
        compliance_map = map_to_clauses(sample_scan_result, registry)
        soc2 = compliance_map.soc2_controls
        assert len(soc2) > 0

    def test_produces_iso_17025_evidence(self, sample_scan_result, registry):
        compliance_map = map_to_clauses(sample_scan_result, registry)
        iso_17025 = compliance_map.iso_17025_clauses
        assert len(iso_17025) > 0

    def test_junit_maps_to_release_clause(self, sample_scan_result, registry):
        compliance_map = map_to_clauses(sample_scan_result, registry)
        iso_clauses = compliance_map.iso_9001_clauses
        clause_ids = [e.clause_id for e in iso_clauses]
        assert "8.6" in clause_ids  # Release of products and services

    def test_zap_maps_to_risk_clause(self, sample_scan_result, registry):
        compliance_map = map_to_clauses(sample_scan_result, registry)
        iso_clauses = compliance_map.iso_9001_clauses
        clause_ids = [e.clause_id for e in iso_clauses]
        assert "6.1" in clause_ids  # Actions to address risks

    def test_zap_maps_to_soc2_access_control(self, sample_scan_result, registry):
        compliance_map = map_to_clauses(sample_scan_result, registry)
        soc2 = compliance_map.soc2_controls
        control_ids = [e.clause_id for e in soc2]
        assert "CC6.1" in control_ids  # Logical access security

    def test_flakiness_maps_to_measurement_traceability(self, sample_scan_result, registry):
        compliance_map = map_to_clauses(sample_scan_result, registry)
        iso_clauses = compliance_map.iso_9001_clauses
        clause_ids = [e.clause_id for e in iso_clauses]
        assert "7.1.5.2" in clause_ids  # Measurement traceability

    def test_triage_maps_to_corrective_action(self, sample_scan_result, registry):
        compliance_map = map_to_clauses(sample_scan_result, registry)
        iso_clauses = compliance_map.iso_9001_clauses
        clause_ids = [e.clause_id for e in iso_clauses]
        assert "10.2" in clause_ids  # Nonconformity and corrective action

    def test_evidence_includes_file_paths(self, sample_scan_result, registry):
        compliance_map = map_to_clauses(sample_scan_result, registry)
        for ev in compliance_map.evidence:
            assert len(ev.evidence_files) > 0

    def test_evidence_includes_framework_names(self, sample_scan_result, registry):
        compliance_map = map_to_clauses(sample_scan_result, registry)
        for ev in compliance_map.evidence:
            assert len(ev.frameworks) > 0

    def test_unique_clause_count(self, sample_scan_result, registry):
        compliance_map = map_to_clauses(sample_scan_result, registry)
        assert compliance_map.unique_clause_count > 10

    def test_empty_scan_produces_empty_map(self, registry):
        empty = ScanResult(root_dir="/empty")
        compliance_map = map_to_clauses(empty, registry)
        assert len(compliance_map.evidence) == 0
        assert compliance_map.unique_clause_count == 0


class TestGroupByClause:
    def test_groups_by_standard(self, sample_scan_result, registry):
        compliance_map = map_to_clauses(sample_scan_result, registry)
        grouped = group_by_clause(compliance_map)
        assert "ISO 9001:2015" in grouped
        assert "SOC 2" in grouped

    def test_groups_by_clause_id(self, sample_scan_result, registry):
        compliance_map = map_to_clauses(sample_scan_result, registry)
        grouped = group_by_clause(compliance_map)
        iso_9001 = grouped["ISO 9001:2015"]
        # Multiple artifact types can map to the same clause
        assert "9.1.1" in iso_9001

    def test_multiple_artifacts_under_same_clause(self, sample_scan_result, registry):
        compliance_map = map_to_clauses(sample_scan_result, registry)
        grouped = group_by_clause(compliance_map)
        # CC8.1 (change management) should have multiple evidence sources
        soc2 = grouped.get("SOC 2", {})
        if "CC8.1" in soc2:
            assert len(soc2["CC8.1"]) >= 2
