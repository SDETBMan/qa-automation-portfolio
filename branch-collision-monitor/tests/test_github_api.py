"""Tests for monitor/github_api.py — diff parsing with fixtures."""

from __future__ import annotations

from pathlib import Path

from monitor.github_api import parse_diff_stats

FIXTURES = Path(__file__).parent / "fixtures"


class TestParseDiffStats:
    """Parse unified diffs to extract filenames and line counts."""

    def test_branch_a_files(self):
        diff = (FIXTURES / "sample_diff_branch_a.txt").read_text()
        files, added, removed = parse_diff_stats(diff)
        assert "src/auth/middleware.py" in files
        assert "src/auth/utils.py" in files
        assert "config/settings.yaml" in files
        assert len(files) == 3

    def test_branch_a_line_counts(self):
        diff = (FIXTURES / "sample_diff_branch_a.txt").read_text()
        _, added, removed = parse_diff_stats(diff)
        assert added > 0
        assert removed > 0

    def test_branch_b_files(self):
        diff = (FIXTURES / "sample_diff_branch_b.txt").read_text()
        files, added, removed = parse_diff_stats(diff)
        assert "src/auth/middleware.py" in files
        assert "src/users/profile.py" in files
        assert "tests/test_auth.py" in files
        assert len(files) == 3

    def test_branch_b_line_counts(self):
        diff = (FIXTURES / "sample_diff_branch_b.txt").read_text()
        _, added, removed = parse_diff_stats(diff)
        assert added > 0

    def test_empty_diff(self):
        files, added, removed = parse_diff_stats("")
        assert files == []
        assert added == 0
        assert removed == 0

    def test_overlapping_file_between_branches(self):
        diff_a = (FIXTURES / "sample_diff_branch_a.txt").read_text()
        diff_b = (FIXTURES / "sample_diff_branch_b.txt").read_text()
        files_a, _, _ = parse_diff_stats(diff_a)
        files_b, _, _ = parse_diff_stats(diff_b)
        overlap = set(files_a) & set(files_b)
        assert "src/auth/middleware.py" in overlap
