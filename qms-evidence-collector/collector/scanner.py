"""Scan the monorepo for CI artifacts that constitute compliance evidence."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ArtifactHit:
    """A single artifact file discovered in the repo."""

    artifact_type: str
    file_path: str
    framework: str
    size_bytes: int


@dataclass
class ScanResult:
    """Aggregated scan results across the entire repo."""

    root_dir: str
    hits: list[ArtifactHit] = field(default_factory=list)
    frameworks_scanned: list[str] = field(default_factory=list)

    @property
    def artifact_types_found(self) -> set[str]:
        return {h.artifact_type for h in self.hits}

    def hits_by_type(self, artifact_type: str) -> list[ArtifactHit]:
        return [h for h in self.hits if h.artifact_type == artifact_type]

    def hits_by_framework(self, framework: str) -> list[ArtifactHit]:
        return [h for h in self.hits if h.framework == framework]


# Directories to skip during scanning
_SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".mypy_cache", ".pytest_cache", ".tox", "dist", "build",
}


def _match_pattern(file_path: Path, pattern: str) -> bool:
    """Check if a file path matches a glob-like pattern."""
    return file_path.match(pattern)


def _detect_framework(file_path: Path, root: Path) -> str:
    """Determine which framework a file belongs to based on its path."""
    relative = file_path.relative_to(root)
    parts = relative.parts
    if parts:
        return parts[0]
    return "root"


def load_registry(registry_path: Path | None = None) -> list[dict]:
    """Load the artifact-to-clause mapping registry."""
    if registry_path is None:
        registry_path = Path(__file__).parent.parent / "mappings" / "clause_registry.json"
    with open(registry_path, encoding="utf-8") as f:
        data = json.load(f)
    return data["artifact_mappings"]


def scan_repo(root_dir: str | Path, registry: list[dict] | None = None) -> ScanResult:
    """Walk the repo and identify compliance-relevant artifacts.

    Args:
        root_dir: Root of the monorepo to scan.
        registry: Optional pre-loaded registry (defaults to clause_registry.json).

    Returns:
        ScanResult with all discovered artifact hits.
    """
    root = Path(root_dir).resolve()
    if registry is None:
        registry = load_registry()

    result = ScanResult(root_dir=str(root))

    # Discover framework directories
    for entry in sorted(root.iterdir()):
        if entry.is_dir() and entry.name not in _SKIP_DIRS and not entry.name.startswith("."):
            result.frameworks_scanned.append(entry.name)

    # Walk and match
    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        # Skip noise directories
        if any(skip in file_path.parts for skip in _SKIP_DIRS):
            continue

        for mapping in registry:
            for pattern in mapping["file_patterns"]:
                if _match_pattern(file_path, pattern):
                    hit = ArtifactHit(
                        artifact_type=mapping["artifact_type"],
                        file_path=str(file_path.relative_to(root)),
                        framework=_detect_framework(file_path, root),
                        size_bytes=file_path.stat().st_size,
                    )
                    result.hits.append(hit)
                    break  # Don't double-count same file under same mapping
    return result
