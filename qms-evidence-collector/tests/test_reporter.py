"""Tests for the compliance report generator."""

import json
import pytest
from pathlib import Path

from collector.scanner import ArtifactHit, ScanResult, load_registry
from collector.mapper import map_to_clauses, ComplianceMap
from collector.reporter import generate_markdown, generate_json, write_report


@pytest.fixture
def registry():
    return load_registry()


@pytest.fixture
def compliance_map(registry) -> ComplianceMap:
    """Build a compliance map from representative scan results."""
    result = ScanResult(root_dir="/mock/repo")
    result.frameworks_scanned = ["selenium-java", "cypress", "playwright"]
    result.hits = [
        ArtifactHit("junit_xml", "selenium-java/test-results/TEST-Login.xml", "selenium-java", 1024),
        ArtifactHit("zap_report", "cypress/zap-report.json", "cypress", 4096),
        ArtifactHit("coverage_report", "cypress/coverage.xml", "cypress", 512),
        ArtifactHit("flakiness_report", "flakiness-detector/flakiness-report.md", "flakiness-detector", 300),
        ArtifactHit("k6_load_test", "fastapi-service/k6/k6-slo-report.json", "fastapi-service", 768),
        ArtifactHit("triage_report", "failure-triage/triage_report.json", "failure-triage", 600),
    ]
    return map_to_clauses(result, registry)


class TestGenerateMarkdown:
    def test_includes_title(self, compliance_map):
        md = generate_markdown(compliance_map)
        assert "# QMS Evidence Collection Report" in md

    def test_includes_coverage_summary(self, compliance_map):
        md = generate_markdown(compliance_map)
        assert "## Coverage Summary" in md
        assert "ISO 9001:2015" in md
        assert "SOC 2" in md

    def test_includes_clause_details(self, compliance_map):
        md = generate_markdown(compliance_map)
        assert "### ISO 9001:2015" in md or "## ISO 9001:2015" in md
        assert "Rationale:" in md

    def test_includes_evidence_files(self, compliance_map):
        md = generate_markdown(compliance_map)
        assert "Evidence files" in md

    def test_includes_gap_analysis(self, compliance_map):
        md = generate_markdown(compliance_map)
        assert "## Gap Analysis" in md

    def test_includes_timestamp(self, compliance_map):
        md = generate_markdown(compliance_map)
        assert "Generated:" in md
        assert "UTC" in md

    def test_includes_frameworks(self, compliance_map):
        md = generate_markdown(compliance_map)
        assert "Frameworks:" in md


class TestGenerateJson:
    def test_includes_timestamp(self, compliance_map):
        report = generate_json(compliance_map)
        assert "generated_at" in report

    def test_includes_summary(self, compliance_map):
        report = generate_json(compliance_map)
        summary = report["summary"]
        assert "unique_clauses_covered" in summary
        assert "total_evidence_files" in summary
        assert "iso_9001_clauses" in summary
        assert "soc2_controls" in summary
        assert "iso_17025_clauses" in summary

    def test_summary_counts_are_positive(self, compliance_map):
        report = generate_json(compliance_map)
        summary = report["summary"]
        assert summary["unique_clauses_covered"] > 0
        assert summary["iso_9001_clauses"] > 0
        assert summary["soc2_controls"] > 0

    def test_includes_standards(self, compliance_map):
        report = generate_json(compliance_map)
        assert "standards" in report
        assert "ISO 9001:2015" in report["standards"]

    def test_clause_has_title_and_evidence(self, compliance_map):
        report = generate_json(compliance_map)
        iso = report["standards"]["ISO 9001:2015"]
        for clause_id, clause_data in iso.items():
            assert "title" in clause_data
            assert "evidence" in clause_data
            assert len(clause_data["evidence"]) > 0

    def test_evidence_entry_structure(self, compliance_map):
        report = generate_json(compliance_map)
        iso = report["standards"]["ISO 9001:2015"]
        first_clause = list(iso.values())[0]
        ev = first_clause["evidence"][0]
        assert "artifact_type" in ev
        assert "rationale" in ev
        assert "frameworks" in ev
        assert "file_count" in ev

    def test_json_is_serializable(self, compliance_map):
        report = generate_json(compliance_map)
        serialized = json.dumps(report)
        assert len(serialized) > 100


class TestWriteReport:
    def test_writes_markdown_file(self, tmp_path, compliance_map):
        output = str(tmp_path / "report.md")
        write_report(compliance_map, output, "markdown")
        content = Path(output).read_text()
        assert "# QMS Evidence Collection Report" in content

    def test_writes_json_file(self, tmp_path, compliance_map):
        output = str(tmp_path / "report.json")
        write_report(compliance_map, output, "json")
        data = json.loads(Path(output).read_text())
        assert "summary" in data

    def test_creates_parent_directories(self, tmp_path, compliance_map):
        output = str(tmp_path / "nested" / "dir" / "report.md")
        write_report(compliance_map, output, "markdown")
        assert Path(output).exists()
