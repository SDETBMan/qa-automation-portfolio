"""Tests for monitor/analyzer.py — scoring formula, categorization, overlap detection."""

from __future__ import annotations

import pytest

from monitor.analyzer import (
    BranchInfo,
    CollisionReport,
    FileOverlap,
    CATEGORY_WEIGHTS,
    categorize_file,
    compute_overall_risk,
    compute_severity_score,
    analyze,
)


# ── categorize_file ──────────────────────────────────────────────────────────

class TestCategorizeFile:
    """File categorization into source, config, test, ci, docs."""

    def test_python_source(self):
        assert categorize_file("src/auth/middleware.py") == "source"

    def test_typescript_source(self):
        assert categorize_file("src/components/App.tsx") == "source"

    def test_java_source(self):
        assert categorize_file("src/main/java/Service.java") == "source"

    def test_yaml_config(self):
        assert categorize_file("config/settings.yaml") == "config"

    def test_json_config(self):
        assert categorize_file("package.json") == "config"

    def test_env_config(self):
        assert categorize_file(".env.example") == "config"

    def test_terraform_config(self):
        assert categorize_file("modules/main.tf") == "config"

    def test_properties_config(self):
        assert categorize_file("config.properties") == "config"

    def test_test_directory(self):
        assert categorize_file("tests/test_auth.py") == "test"

    def test_test_prefix(self):
        assert categorize_file("test_utils.py") == "test"

    def test_spec_file(self):
        assert categorize_file("src/auth.spec.ts") == "test"

    def test_test_suffix(self):
        assert categorize_file("src/auth_test.go") == "test"

    def test_github_actions_ci(self):
        assert categorize_file(".github/workflows/ci.yml") == "ci"

    def test_circleci(self):
        assert categorize_file(".circleci/config.yml") == "ci"

    def test_markdown_docs(self):
        assert categorize_file("README.md") == "docs"

    def test_rst_docs(self):
        assert categorize_file("docs/guide.rst") == "docs"

    def test_makefile_config(self):
        assert categorize_file("Makefile") == "config"

    def test_dockerfile_config(self):
        assert categorize_file("Dockerfile") == "config"

    def test_unknown_defaults_to_source(self):
        assert categorize_file("something.xyz") == "source"


# ── compute_severity_score ───────────────────────────────────────────────────

class TestComputeSeverityScore:
    """Per-file severity scoring formula."""

    def test_zero_branches(self):
        assert compute_severity_score(2, 0, "source", 100) == 0.0

    def test_all_branches_overlap_source(self):
        # (5/5) * 1.0 + min(250/500, 0.3) = 1.0 + 0.3 → capped at 1.0
        score = compute_severity_score(5, 5, "source", 250)
        assert score == 1.0

    def test_half_branches_overlap_source(self):
        # (2/4) * 1.0 + min(0/500, 0.3) = 0.5
        score = compute_severity_score(2, 4, "source", 0)
        assert score == 0.5

    def test_config_weight(self):
        # (2/4) * 0.8 + 0 = 0.4
        score = compute_severity_score(2, 4, "config", 0)
        assert score == pytest.approx(0.4)

    def test_test_weight(self):
        # (2/4) * 0.7 + 0 = 0.35
        score = compute_severity_score(2, 4, "test", 0)
        assert score == pytest.approx(0.35)

    def test_ci_weight(self):
        # (2/4) * 0.6 + 0 = 0.3
        score = compute_severity_score(2, 4, "ci", 0)
        assert score == pytest.approx(0.3)

    def test_docs_weight(self):
        # (2/4) * 0.2 + 0 = 0.1
        score = compute_severity_score(2, 4, "docs", 0)
        assert score == pytest.approx(0.1)

    def test_line_bonus_capped_at_03(self):
        # (1/2) * 1.0 + min(10000/500, 0.3) = 0.5 + 0.3 = 0.8
        score = compute_severity_score(1, 2, "source", 10000)
        assert score == pytest.approx(0.8)

    def test_line_bonus_partial(self):
        # (2/4) * 1.0 + min(100/500, 0.3) = 0.5 + 0.2 = 0.7
        score = compute_severity_score(2, 4, "source", 100)
        assert score == pytest.approx(0.7)

    def test_score_capped_at_1(self):
        # (10/10) * 1.0 + 0.3 → 1.3 capped at 1.0
        score = compute_severity_score(10, 10, "source", 10000)
        assert score == 1.0

    def test_unknown_category_uses_default_weight(self):
        # Unknown category defaults to 1.0 weight
        score = compute_severity_score(2, 4, "unknown_category", 0)
        assert score == pytest.approx(0.5)


# ── compute_overall_risk ─────────────────────────────────────────────────────

class TestComputeOverallRisk:
    """Overall risk mapping from score to level."""

    def test_no_overlaps(self):
        level, score = compute_overall_risk([], 10)
        assert level == "LOW"
        assert score == 0.0

    def test_zero_total_files(self):
        level, score = compute_overall_risk([FileOverlap(path="a.py", severity_score=0.5)], 0)
        assert level == "LOW"
        assert score == 0.0

    def test_low_risk(self):
        overlaps = [FileOverlap(path="a.py", severity_score=0.1)]
        level, score = compute_overall_risk(overlaps, 10)
        assert level == "LOW"
        assert score == pytest.approx(0.01)

    def test_moderate_risk(self):
        # score = 2.5 / 10 = 0.25
        overlaps = [FileOverlap(path=f"f{i}.py", severity_score=0.5) for i in range(5)]
        level, score = compute_overall_risk(overlaps, 10)
        assert level == "MODERATE"

    def test_high_risk(self):
        # score = 4.0 / 10 = 0.4
        overlaps = [FileOverlap(path=f"f{i}.py", severity_score=0.8) for i in range(5)]
        level, score = compute_overall_risk(overlaps, 10)
        assert level == "HIGH"

    def test_critical_risk(self):
        # score = 7.0 / 10 = 0.7
        overlaps = [FileOverlap(path=f"f{i}.py", severity_score=1.0) for i in range(7)]
        level, score = compute_overall_risk(overlaps, 10)
        assert level == "CRITICAL"


# ── analyze ──────────────────────────────────────────────────────────────────

class TestAnalyze:
    """End-to-end analysis of branch data."""

    def test_no_branches(self):
        report = analyze([], repo="owner/repo")
        assert report.branches_analyzed == 0
        assert report.overlapping_files == []
        assert report.overall_risk == "LOW"

    def test_single_branch_no_overlap(self):
        branches = [
            BranchInfo(name="feature/a", files_changed=["src/a.py"], lines_added=10, lines_removed=5),
        ]
        report = analyze(branches)
        assert report.branches_analyzed == 1
        assert len(report.overlapping_files) == 0

    def test_two_branches_overlap(self):
        branches = [
            BranchInfo(name="feature/a", files_changed=["src/auth.py", "src/utils.py"], lines_added=50, lines_removed=10),
            BranchInfo(name="feature/b", files_changed=["src/auth.py", "src/profile.py"], lines_added=30, lines_removed=5),
        ]
        report = analyze(branches)
        assert report.branches_analyzed == 2
        assert len(report.overlapping_files) == 1
        assert report.overlapping_files[0].path == "src/auth.py"
        assert set(report.overlapping_files[0].branches) == {"feature/a", "feature/b"}

    def test_three_branches_same_file(self):
        branches = [
            BranchInfo(name="a", files_changed=["shared.py"], lines_added=10, lines_removed=0),
            BranchInfo(name="b", files_changed=["shared.py"], lines_added=20, lines_removed=0),
            BranchInfo(name="c", files_changed=["shared.py"], lines_added=30, lines_removed=0),
        ]
        report = analyze(branches)
        assert len(report.overlapping_files) == 1
        overlap = report.overlapping_files[0]
        assert len(overlap.branches) == 3

    def test_no_overlap_different_files(self):
        branches = [
            BranchInfo(name="a", files_changed=["src/a.py"]),
            BranchInfo(name="b", files_changed=["src/b.py"]),
            BranchInfo(name="c", files_changed=["src/c.py"]),
        ]
        report = analyze(branches)
        assert len(report.overlapping_files) == 0
        assert report.overall_risk == "LOW"

    def test_overlapping_sorted_by_severity(self):
        branches = [
            BranchInfo(name="a", files_changed=["docs/readme.md", "src/core.py"], lines_added=100, lines_removed=0),
            BranchInfo(name="b", files_changed=["docs/readme.md", "src/core.py"], lines_added=200, lines_removed=0),
        ]
        report = analyze(branches)
        assert len(report.overlapping_files) == 2
        # Source file should have higher severity than docs
        assert report.overlapping_files[0].category == "source"
        assert report.overlapping_files[1].category == "docs"

    def test_repo_and_base_in_report(self):
        report = analyze([], repo="owner/repo", base_branch="develop")
        assert report.repo == "owner/repo"
        assert report.base_branch == "develop"

    def test_total_files_touched(self):
        branches = [
            BranchInfo(name="a", files_changed=["f1.py", "f2.py"]),
            BranchInfo(name="b", files_changed=["f2.py", "f3.py"]),
        ]
        report = analyze(branches)
        assert report.total_files_touched == 3
