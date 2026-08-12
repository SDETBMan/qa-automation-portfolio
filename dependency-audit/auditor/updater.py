"""
updater.py — Write updated versions back to package manifests.

Supports:
  - package.json: updates version strings in dependencies/devDependencies
  - requirements.txt: updates version specifiers
  - .csproj: updates PackageReference Version attributes
  - pom.xml: updates <version> tags in <dependency> blocks
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from auditor.checkers import DependencyInfo


def update_manifest(
    ecosystem: str,
    path: Path,
    updates: list[DependencyInfo],
) -> int:
    """Apply version updates to the manifest file.  Returns count of changes."""
    updater = _UPDATERS.get(ecosystem)
    if not updater:
        return 0
    return updater(path, updates)


# ---------------------------------------------------------------------------
# npm
# ---------------------------------------------------------------------------


def _update_npm(path: Path, updates: list[DependencyInfo]) -> int:
    with open(path) as f:
        pkg = json.load(f)

    lookup = {u.package: u.latest for u in updates if u.latest and u.status == "outdated"}
    if not lookup:
        return 0

    count = 0
    for section in ("dependencies", "devDependencies"):
        deps = pkg.get(section, {})
        for name in deps:
            if name in lookup:
                old = deps[name]
                prefix = ""
                if old.startswith("^"):
                    prefix = "^"
                elif old.startswith("~"):
                    prefix = "~"
                deps[name] = f"{prefix}{lookup[name]}"
                count += 1

    with open(path, "w") as f:
        json.dump(pkg, f, indent=2)
        f.write("\n")

    return count


# ---------------------------------------------------------------------------
# pip
# ---------------------------------------------------------------------------


def _update_pip(path: Path, updates: list[DependencyInfo]) -> int:
    lookup = {u.package: u.latest for u in updates if u.latest and u.status == "outdated"}
    if not lookup:
        return 0

    lines = path.read_text().splitlines(keepends=True)
    count = 0
    new_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue

        match = re.match(r"^([a-zA-Z0-9_-]+(?:\[[a-zA-Z0-9_,]+\])?)\s*([><=!~]+)\s*([\d.*]+)", stripped)
        if match:
            pkg_name = match.group(1).split("[")[0]
            if pkg_name in lookup:
                extras = match.group(1)[len(pkg_name):]  # e.g. [standard]
                new_lines.append(f"{pkg_name}{extras}>={lookup[pkg_name]}\n")
                count += 1
                continue

        new_lines.append(line)

    path.write_text("".join(new_lines))
    return count


# ---------------------------------------------------------------------------
# NuGet (.csproj)
# ---------------------------------------------------------------------------


def _update_nuget(path: Path, updates: list[DependencyInfo]) -> int:
    lookup = {u.package: u.latest for u in updates if u.latest and u.status == "outdated"}
    if not lookup:
        return 0

    # Use string replacement to preserve formatting
    content = path.read_text()
    count = 0

    for pkg_name, new_version in lookup.items():
        # Match PackageReference Include="pkg_name" Version="..."
        pattern = (
            rf'(<PackageReference\s+Include="{re.escape(pkg_name)}"\s+Version=")([^"]*)'
        )
        new_content = re.sub(pattern, rf"\g<1>{new_version}.*", content)
        if new_content != content:
            count += 1
            content = new_content

    path.write_text(content)
    return count


# ---------------------------------------------------------------------------
# Maven (pom.xml)
# ---------------------------------------------------------------------------


def _update_maven(path: Path, updates: list[DependencyInfo]) -> int:
    lookup = {u.package: u.latest for u in updates if u.latest and u.status == "outdated"}
    if not lookup:
        return 0

    try:
        tree = ET.parse(path)
        root = tree.getroot()
        ns = ""
        if root.tag.startswith("{"):
            ns = root.tag.split("}")[0] + "}"

        count = 0
        for dep in root.iter(f"{ns}dependency"):
            group_id = dep.findtext(f"{ns}groupId", "")
            artifact_id = dep.findtext(f"{ns}artifactId", "")
            version_el = dep.find(f"{ns}version")
            if version_el is None:
                continue
            name = f"{group_id}:{artifact_id}" if group_id else artifact_id
            if name in lookup:
                version_el.text = lookup[name]
                count += 1

        if count:
            tree.write(path, xml_declaration=True, encoding="utf-8")
        return count
    except ET.ParseError:
        return 0


_UPDATERS = {
    "npm": _update_npm,
    "pip": _update_pip,
    "nuget": _update_nuget,
    "maven": _update_maven,
}
