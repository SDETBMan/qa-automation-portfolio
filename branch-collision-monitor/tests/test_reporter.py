"""Tests for monitor/reporter.py — JSON schema and Markdown structure validation."""

from __future__ import annotations

import json

from monitor.analyzer import CollisionReport, FileOverlap, SemanticOverlap
from monitor.reporter import generate_json_report, generate_markdown_report


def _sample_report() -> CollisionReport:
    """Build a sample report for testing."""
    return CollisionReport(
        repo="owner/repo",
        base_branch="main",
        branches_analyzed=3,
        total_files_touched=10,
        overlapping_files=[
            FileOverlap(
                path="src/auth/middleware.py",
                branches=["feature/a", "feature/b"],
                category="source",
                total_lines_changed=150,
                severity_score=0.85,
            ),
            FileOverlap(
                path="config/settings.yaml",
                branches=["feature/a", "feature/c"],
                category="config",
                total_lines_changed=20,
                severity_score=0.45,
            ),
        ],
        semantic_overlaps=[
            SemanticOverlap(
                file_path="src/auth/middleware.py",
                branch_a="feature/a",
                branch_b="feature/b",
                conflict_likelihood="high",
                explanation="Both branches modify the __init__ method of AuthMiddleware.",
                functions_affected=["__init__", "__call__"],
            ),
        ],
        overall_risk="HIGH",
        overall_score=0.42,
    )


class TestGenerateJsonReport:
    """JSON report generation."""

    def test_valid_json(self):
        report = _sample_report()
        output = generate_json_report(report)
        data = json.loads(output)
        assert isinstance(data, dict)

    def test_contains_required_fields(self):
        report = _sample_report()
        data = json.loads(generate_json_report(report))
        assert data["repo"] == "owner/repo"
        assert data["base_branch"] == "main"
        assert data["branches_analyzed"] == 3
        assert data["overall_risk"] == "HIGH"
        assert "generated_at" in data

    def test_overlapping_files_serialized(self):
        report = _sample_report()
        data = json.loads(generate_json_report(report))
        assert len(data["overlapping_files"]) == 2
        first = data["overlapping_files"][0]
        assert first["path"] == "src/auth/middleware.py"
        assert first["severity_score"] == 0.85

    def test_semantic_overlaps_serialized(self):
        report = _sample_report()
        data = json.loads(generate_json_report(report))
        assert len(data["semantic_overlaps"]) == 1
        sem = data["semantic_overlaps"][0]
        assert sem["conflict_likelihood"] == "high"
        assert "functions_affected" in sem

    def test_empty_report(self):
        report = CollisionReport(repo="owner/repo", base_branch="main")
        data = json.loads(generate_json_report(report))
        assert data["overlapping_files"] == []
        assert data["overall_risk"] == "LOW"


class TestGenerateMarkdownReport:
    """Markdown report structure validation."""

    def test_contains_title(self):
        report = _sample_report()
        md = generate_markdown_report(report)
        assert "# Branch Collision Report" in md

    def test_contains_repo_info(self):
        report = _sample_report()
        md = generate_markdown_report(report)
        assert "owner/repo" in md
        assert "main" in md

    def test_contains_risk_level(self):
        report = _sample_report()
        md = generate_markdown_report(report)
        assert "HIGH" in md

    def test_contains_file_table(self):
        report = _sample_report()
        md = generate_markdown_report(report)
        assert "| File | Category |" in md
        assert "`src/auth/middleware.py`" in md

    def test_contains_category_breakdown(self):
        report = _sample_report()
        md = generate_markdown_report(report)
        assert "## By Category" in md
        assert "source" in md

    def test_contains_semantic_section(self):
        report = _sample_report()
        md = generate_markdown_report(report)
        assert "Semantic Conflicts" in md
        assert "feature/a" in md

    def test_no_overlaps_message(self):
        report = CollisionReport(repo="owner/repo", base_branch="main")
        md = generate_markdown_report(report)
        assert "No file-level collisions detected" in md

    def test_contains_footer(self):
        report = _sample_report()
        md = generate_markdown_report(report)
        assert "branch-collision-monitor" in md
