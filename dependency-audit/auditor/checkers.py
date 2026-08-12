"""
checkers.py — Per-ecosystem version checkers.

Each checker reads the manifest, extracts current versions, and queries
the upstream registry for the latest version.

Supported ecosystems:
  - npm:    reads package.json, queries registry.npmjs.org
  - pip:    reads requirements.txt, queries pypi.org/pypi/<pkg>/json
  - nuget:  reads .csproj PackageReference, queries api.nuget.org
  - maven:  reads pom.xml <dependency>, queries search.maven.org

Returns a list of DependencyInfo for each package found.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import requests

# Timeout for registry lookups
_TIMEOUT = 10


@dataclass
class DependencyInfo:
    """Version status for a single dependency."""

    package: str
    current: str
    latest: str | None  # None if lookup failed
    status: str         # "up-to-date" | "outdated" | "unknown"


def _strip_version_prefix(v: str) -> str:
    """Remove ^, ~, >=, etc. to get a clean version string."""
    return re.sub(r"^[^0-9]*", "", v).rstrip("*").rstrip(".")


# ---------------------------------------------------------------------------
# npm
# ---------------------------------------------------------------------------


def check_npm(manifest_path: Path) -> list[DependencyInfo]:
    """Check npm dependencies in a package.json file."""
    with open(manifest_path) as f:
        pkg = json.load(f)

    results: list[DependencyInfo] = []
    for section in ("dependencies", "devDependencies"):
        deps = pkg.get(section, {})
        for name, version_spec in deps.items():
            current = _strip_version_prefix(version_spec)
            latest = _fetch_npm_latest(name)
            status = _compare(current, latest)
            results.append(DependencyInfo(name, current, latest, status))
    return results


def _fetch_npm_latest(package: str) -> str | None:
    try:
        r = requests.get(
            f"https://registry.npmjs.org/{package}/latest",
            timeout=_TIMEOUT,
        )
        if r.ok:
            return r.json().get("version")
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# pip
# ---------------------------------------------------------------------------


def check_pip(manifest_path: Path) -> list[DependencyInfo]:
    """Check pip dependencies in a requirements.txt file."""
    results: list[DependencyInfo] = []
    with open(manifest_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            # Parse "package>=1.0.0" or "package==1.0.0" or "package"
            match = re.match(r"^([a-zA-Z0-9_-]+(?:\[[a-zA-Z0-9_,]+\])?)\s*([><=!~]+)?\s*([\d.*]+)?", line)
            if not match:
                continue
            name = match.group(1).split("[")[0]  # strip extras like [standard]
            current = match.group(3) or "unspecified"
            latest = _fetch_pypi_latest(name)
            status = _compare(current, latest) if current != "unspecified" else "unknown"
            results.append(DependencyInfo(name, current, latest, status))
    return results


def _fetch_pypi_latest(package: str) -> str | None:
    try:
        r = requests.get(
            f"https://pypi.org/pypi/{package}/json",
            timeout=_TIMEOUT,
        )
        if r.ok:
            return r.json()["info"]["version"]
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# NuGet (.csproj)
# ---------------------------------------------------------------------------


def check_nuget(manifest_path: Path) -> list[DependencyInfo]:
    """Check NuGet dependencies in a .csproj file."""
    results: list[DependencyInfo] = []
    try:
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        # Handle default namespace
        ns = ""
        if root.tag.startswith("{"):
            ns = root.tag.split("}")[0] + "}"

        for ref in root.iter(f"{ns}PackageReference"):
            name = ref.get("Include", "")
            version = ref.get("Version", "")
            if not name or not version:
                continue
            current = _strip_version_prefix(version)
            latest = _fetch_nuget_latest(name)
            status = _compare(current, latest)
            results.append(DependencyInfo(name, current, latest, status))
    except ET.ParseError:
        pass
    return results


def _fetch_nuget_latest(package: str) -> str | None:
    try:
        r = requests.get(
            f"https://api.nuget.org/v3-flatcontainer/{package.lower()}/index.json",
            timeout=_TIMEOUT,
        )
        if r.ok:
            versions = r.json().get("versions", [])
            # Filter out pre-release versions
            stable = [v for v in versions if "-" not in v]
            return stable[-1] if stable else (versions[-1] if versions else None)
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Maven (pom.xml)
# ---------------------------------------------------------------------------


def check_maven(manifest_path: Path) -> list[DependencyInfo]:
    """Check Maven dependencies in a pom.xml file."""
    results: list[DependencyInfo] = []
    try:
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        ns = ""
        if root.tag.startswith("{"):
            ns = root.tag.split("}")[0] + "}"

        for dep in root.iter(f"{ns}dependency"):
            group_id = dep.findtext(f"{ns}groupId", "")
            artifact_id = dep.findtext(f"{ns}artifactId", "")
            version = dep.findtext(f"{ns}version", "")
            if not artifact_id or not version:
                continue
            # Skip property references like ${project.version}
            if version.startswith("${"):
                continue
            name = f"{group_id}:{artifact_id}" if group_id else artifact_id
            current = _strip_version_prefix(version)
            latest = _fetch_maven_latest(group_id, artifact_id)
            status = _compare(current, latest)
            results.append(DependencyInfo(name, current, latest, status))
    except ET.ParseError:
        pass
    return results


def _fetch_maven_latest(group_id: str, artifact_id: str) -> str | None:
    try:
        r = requests.get(
            "https://search.maven.org/solrsearch/select",
            params={"q": f"g:{group_id} AND a:{artifact_id}", "rows": 1, "wt": "json"},
            timeout=_TIMEOUT,
        )
        if r.ok:
            docs = r.json().get("response", {}).get("docs", [])
            if docs:
                return docs[0].get("latestVersion")
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------


def _compare(current: str, latest: str | None) -> str:
    """Compare version strings and return status."""
    if not latest or not current or current == "unspecified":
        return "unknown"
    # Normalize for comparison: strip wildcards
    c = current.rstrip(".*")
    l = latest.rstrip(".*")
    if c == l:
        return "up-to-date"
    # Check if current is a prefix of latest (e.g. "1.52" matches "1.52.0")
    if l.startswith(c + ".") or l.startswith(c):
        return "up-to-date"
    return "outdated"


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

CHECKERS: dict[str, type] = {
    "npm": check_npm,
    "pip": check_pip,
    "nuget": check_nuget,
    "maven": check_maven,
}


def check_manifest(ecosystem: str, path: Path) -> list[DependencyInfo]:
    """Run the appropriate checker for the given ecosystem."""
    checker = CHECKERS.get(ecosystem)
    if not checker:
        return []
    return checker(path)
