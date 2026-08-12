"""
scanner.py — Walk the monorepo and discover package manifests.

Supports:
  - package.json  (npm / Node.js)
  - requirements.txt  (pip / Python)
  - *.csproj  (NuGet / .NET)
  - pom.xml  (Maven / Java)
  - go.mod  (Go modules)

Returns a list of ManifestInfo named tuples with the framework name,
ecosystem, and absolute path to the manifest file.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ManifestInfo:
    """Metadata about a discovered package manifest."""

    framework: str  # top-level directory name (e.g. "playwright")
    ecosystem: str  # "npm" | "pip" | "nuget" | "maven" | "go"
    path: Path      # absolute path to the manifest file


# Files to look for and their ecosystems
_MANIFEST_MAP: dict[str, str] = {
    "package.json": "npm",
    "requirements.txt": "pip",
    "pom.xml": "maven",
    "go.mod": "go",
}

# Directories to skip
_SKIP_DIRS = {
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "bin",
    "obj",
    "target",
    "dist",
    "build",
    ".next",
    ".nuxt",
}


def scan_repo(repo_dir: str | Path) -> list[ManifestInfo]:
    """Walk ``repo_dir`` and return all discovered manifests."""
    repo = Path(repo_dir).resolve()
    manifests: list[ManifestInfo] = []

    for root, dirs, files in os.walk(repo):
        # Prune directories we never want to descend into
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]

        root_path = Path(root)
        rel = root_path.relative_to(repo)
        # Framework name is the first path component
        parts = rel.parts
        framework = parts[0] if parts else root_path.name

        for fname in files:
            fpath = root_path / fname

            # Check known manifest filenames
            if fname in _MANIFEST_MAP:
                manifests.append(
                    ManifestInfo(
                        framework=framework,
                        ecosystem=_MANIFEST_MAP[fname],
                        path=fpath,
                    )
                )

            # .csproj files (NuGet)
            elif fname.endswith(".csproj"):
                manifests.append(
                    ManifestInfo(
                        framework=framework,
                        ecosystem="nuget",
                        path=fpath,
                    )
                )

    return sorted(manifests, key=lambda m: (m.framework, m.ecosystem, str(m.path)))
