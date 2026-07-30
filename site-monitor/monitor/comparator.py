"""comparator.py — Diff current vs baseline, categorize changes."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DriftReport:
    """Result of comparing two selector snapshots."""

    added_ids: list[str] = field(default_factory=list)
    removed_ids: list[str] = field(default_factory=list)
    added_classes: list[str] = field(default_factory=list)
    removed_classes: list[str] = field(default_factory=list)
    added_data_test: list[str] = field(default_factory=list)
    removed_data_test: list[str] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        """True if any removals or additions detected."""
        return bool(
            self.added_ids
            or self.removed_ids
            or self.added_classes
            or self.removed_classes
            or self.added_data_test
            or self.removed_data_test
        )

    @property
    def severity(self) -> str:
        """'critical' if any removals, 'info' if only additions, 'none' otherwise."""
        if self.removed_ids or self.removed_classes or self.removed_data_test:
            return "critical"
        if self.added_ids or self.added_classes or self.added_data_test:
            return "info"
        return "none"

    @property
    def total_removed(self) -> int:
        return len(self.removed_ids) + len(self.removed_classes) + len(self.removed_data_test)

    @property
    def total_added(self) -> int:
        return len(self.added_ids) + len(self.added_classes) + len(self.added_data_test)


def compare(baseline: dict, current: dict) -> DriftReport:
    """Compare two snapshots and produce a DriftReport."""
    baseline_ids = set(baseline.get("ids", []))
    current_ids = set(current.get("ids", []))

    baseline_classes = set(baseline.get("classes", []))
    current_classes = set(current.get("classes", []))

    baseline_data_test = set(baseline.get("data_test", []))
    current_data_test = set(current.get("data_test", []))

    return DriftReport(
        added_ids=sorted(current_ids - baseline_ids),
        removed_ids=sorted(baseline_ids - current_ids),
        added_classes=sorted(current_classes - baseline_classes),
        removed_classes=sorted(baseline_classes - current_classes),
        added_data_test=sorted(current_data_test - baseline_data_test),
        removed_data_test=sorted(baseline_data_test - current_data_test),
    )


def check_monitored(report: DriftReport, registry_path: str | Path) -> list[dict]:
    """Cross-reference removals against selectors.json to identify affected frameworks."""
    registry_path = Path(registry_path)
    if not registry_path.exists():
        return []

    with open(registry_path, encoding="utf-8") as f:
        registry = json.load(f)

    monitored = registry.get("monitored", {})
    affected: list[dict] = []

    for selector in report.removed_ids:
        frameworks = monitored.get("ids", {}).get(selector, [])
        if frameworks:
            affected.append({
                "selector": selector,
                "type": "id",
                "frameworks": frameworks,
            })

    for selector in report.removed_classes:
        frameworks = monitored.get("classes", {}).get(selector, [])
        if frameworks:
            affected.append({
                "selector": selector,
                "type": "class",
                "frameworks": frameworks,
            })

    for selector in report.removed_data_test:
        frameworks = monitored.get("data_test", {}).get(selector, [])
        if frameworks:
            affected.append({
                "selector": selector,
                "type": "data-test",
                "frameworks": frameworks,
            })

    return affected
