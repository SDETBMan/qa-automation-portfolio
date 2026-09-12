"""
analyzer.py — Detect hot zones and score collision severity across branches.

Scoring algorithm (3 layers):
  1. File categorization: source (1.0), config (0.8), test (0.7), ci (0.6), docs (0.2)
  2. Per-file severity:
       (overlap_count / total_branches) * category_weight + min(lines_changed / 500, 0.3)
     Capped at 1.0.
  3. Overall risk: sum(severity_scores) / total_files, mapped to risk level.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ── File category weights ────────────────────────────────────────────────────

CATEGORY_WEIGHTS: dict[str, float] = {
    "source": 1.0,
    "config": 0.8,
    "test": 0.7,
    "ci": 0.6,
    "docs": 0.2,
}


# ── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class BranchInfo:
    """Metadata for a single active branch."""
    name: str
    files_changed: list[str] = field(default_factory=list)
    lines_added: int = 0
    lines_removed: int = 0
    author: str = ""
    last_commit_date: str = ""


@dataclass
class FileOverlap:
    """A file touched by multiple branches — a potential collision."""
    path: str
    branches: list[str] = field(default_factory=list)
    category: str = "source"
    total_lines_changed: int = 0
    severity_score: float = 0.0


@dataclass
class SemanticOverlap:
    """Claude-assessed semantic conflict between two branches on a file."""
    file_path: str
    branch_a: str
    branch_b: str
    conflict_likelihood: str = "none"  # high | medium | low | none
    explanation: str = ""
    functions_affected: list[str] = field(default_factory=list)


@dataclass
class CollisionReport:
    """Full collision analysis for a repository."""
    repo: str
    base_branch: str
    branches_analyzed: int = 0
    total_files_touched: int = 0
    overlapping_files: list[FileOverlap] = field(default_factory=list)
    semantic_overlaps: list[SemanticOverlap] = field(default_factory=list)
    overall_risk: str = "LOW"  # LOW | MODERATE | HIGH | CRITICAL
    overall_score: float = 0.0


# ── Categorization ───────────────────────────────────────────────────────────

_SOURCE_EXTS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".cs", ".go", ".rs",
    ".rb", ".php", ".swift", ".kt", ".scala", ".sh", ".bash",
}

_CONFIG_EXTS = {
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".properties",
    ".env", ".xml", ".tf", ".hcl",
}

_DOC_EXTS = {".md", ".rst", ".txt", ".adoc"}

_CI_PATHS = {".github/", ".circleci/", ".gitlab-ci", "Jenkinsfile"}


def categorize_file(path: str) -> str:
    """Classify a file path into source, config, test, ci, or docs."""
    lower = path.lower()

    # CI detection (path-based)
    for ci_path in _CI_PATHS:
        if ci_path in lower:
            return "ci"

    # Test detection (path or filename)
    if "/test" in lower or "/tests/" in lower or lower.startswith("test"):
        return "test"
    if "test_" in lower or "_test." in lower or ".spec." in lower or ".test." in lower:
        return "test"

    # .env files (may have suffixes like .env.example, .env.local)
    basename = lower.rsplit("/", 1)[-1]
    if basename.startswith(".env"):
        return "config"

    # Extension-based
    dot_idx = lower.rfind(".")
    ext = lower[dot_idx:] if dot_idx != -1 else ""

    if ext in _DOC_EXTS:
        return "docs"
    if ext in _CONFIG_EXTS:
        return "config"
    if ext in _SOURCE_EXTS:
        return "source"

    # Specific filenames
    if lower.endswith("makefile") or lower.endswith("dockerfile"):
        return "config"
    if lower.endswith("readme") or lower.endswith("changelog") or lower.endswith("license"):
        return "docs"

    return "source"  # default


# ── Severity scoring ─────────────────────────────────────────────────────────

def compute_severity_score(
    overlap_count: int,
    total_branches: int,
    category: str,
    lines_changed: int,
) -> float:
    """Compute severity score for a single overlapping file.

    Formula:
        (overlap_count / total_branches) * category_weight + min(lines_changed / 500, 0.3)
    Capped at 1.0.
    """
    if total_branches == 0:
        return 0.0

    weight = CATEGORY_WEIGHTS.get(category, 1.0)
    overlap_ratio = overlap_count / total_branches
    line_bonus = min(lines_changed / 500, 0.3)

    return min(overlap_ratio * weight + line_bonus, 1.0)


def compute_overall_risk(overlapping_files: list[FileOverlap], total_files: int) -> tuple[str, float]:
    """Compute overall risk level from overlapping files.

    Returns:
        (risk_level, score) where risk_level is LOW/MODERATE/HIGH/CRITICAL.
    """
    if not overlapping_files or total_files == 0:
        return "LOW", 0.0

    score = sum(f.severity_score for f in overlapping_files) / total_files

    if score >= 0.7:
        return "CRITICAL", round(score, 4)
    if score >= 0.4:
        return "HIGH", round(score, 4)
    if score >= 0.2:
        return "MODERATE", round(score, 4)
    return "LOW", round(score, 4)


# ── Main analysis ────────────────────────────────────────────────────────────

def analyze(
    branches: list[BranchInfo],
    repo: str = "",
    base_branch: str = "main",
) -> CollisionReport:
    """Analyze branches for file-level collisions.

    Finds files touched by 2+ branches, scores severity, and computes
    overall risk.
    """
    # Build file → branches mapping
    file_branches: dict[str, list[str]] = {}
    file_lines: dict[str, int] = {}

    all_files: set[str] = set()

    for branch in branches:
        branch_lines = branch.lines_added + branch.lines_removed
        per_file_avg = branch_lines // max(len(branch.files_changed), 1)

        for f in branch.files_changed:
            all_files.add(f)
            file_branches.setdefault(f, []).append(branch.name)
            file_lines[f] = file_lines.get(f, 0) + per_file_avg

    total_branches = len(branches)
    total_files = len(all_files)

    # Find overlaps (2+ branches touching the same file)
    overlapping: list[FileOverlap] = []
    for path, br_list in file_branches.items():
        if len(br_list) < 2:
            continue

        category = categorize_file(path)
        severity = compute_severity_score(
            overlap_count=len(br_list),
            total_branches=total_branches,
            category=category,
            lines_changed=file_lines.get(path, 0),
        )

        overlapping.append(FileOverlap(
            path=path,
            branches=sorted(br_list),
            category=category,
            total_lines_changed=file_lines.get(path, 0),
            severity_score=round(severity, 4),
        ))

    # Sort by severity descending
    overlapping.sort(key=lambda f: f.severity_score, reverse=True)

    risk_level, risk_score = compute_overall_risk(overlapping, total_files)

    return CollisionReport(
        repo=repo,
        base_branch=base_branch,
        branches_analyzed=total_branches,
        total_files_touched=total_files,
        overlapping_files=overlapping,
        overall_risk=risk_level,
        overall_score=risk_score,
    )
