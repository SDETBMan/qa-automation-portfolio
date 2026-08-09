"""Map discovered artifacts to ISO 9001, SOC 2, and ISO/IEC 17025 clauses."""

from __future__ import annotations

from dataclasses import dataclass, field

from .scanner import ArtifactHit, ScanResult


@dataclass
class ClauseEvidence:
    """A single compliance clause with supporting evidence artifacts."""

    standard: str          # "ISO 9001:2015", "SOC 2", "ISO/IEC 17025:2017"
    clause_id: str         # e.g. "9.1.1", "CC8.1"
    title: str
    rationale: str
    artifact_type: str
    evidence_files: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)


@dataclass
class ComplianceMap:
    """Full mapping of artifacts to compliance clauses."""

    evidence: list[ClauseEvidence] = field(default_factory=list)

    @property
    def iso_9001_clauses(self) -> list[ClauseEvidence]:
        return [e for e in self.evidence if e.standard == "ISO 9001:2015"]

    @property
    def soc2_controls(self) -> list[ClauseEvidence]:
        return [e for e in self.evidence if e.standard == "SOC 2"]

    @property
    def iso_17025_clauses(self) -> list[ClauseEvidence]:
        return [e for e in self.evidence if e.standard == "ISO/IEC 17025:2017"]

    @property
    def unique_clause_count(self) -> int:
        seen = set()
        for e in self.evidence:
            seen.add((e.standard, e.clause_id))
        return len(seen)

    @property
    def total_evidence_files(self) -> int:
        all_files: set[str] = set()
        for e in self.evidence:
            all_files.update(e.evidence_files)
        return len(all_files)


def map_to_clauses(scan_result: ScanResult, registry: list[dict]) -> ComplianceMap:
    """Map scan results to compliance clauses using the registry.

    Args:
        scan_result: Output from scanner.scan_repo().
        registry: Loaded clause_registry.json artifact_mappings.

    Returns:
        ComplianceMap with all clause-to-evidence mappings.
    """
    compliance_map = ComplianceMap()

    # Index hits by artifact type
    hits_by_type: dict[str, list[ArtifactHit]] = {}
    for hit in scan_result.hits:
        hits_by_type.setdefault(hit.artifact_type, []).append(hit)

    for mapping in registry:
        artifact_type = mapping["artifact_type"]
        hits = hits_by_type.get(artifact_type, [])
        if not hits:
            continue

        files = [h.file_path for h in hits]
        frameworks = sorted(set(h.framework for h in hits))

        # ISO 9001:2015
        for clause in mapping["clauses"].get("iso_9001", []):
            compliance_map.evidence.append(ClauseEvidence(
                standard="ISO 9001:2015",
                clause_id=clause["clause"],
                title=clause["title"],
                rationale=clause["rationale"],
                artifact_type=artifact_type,
                evidence_files=files,
                frameworks=frameworks,
            ))

        # SOC 2
        for control in mapping["clauses"].get("soc2", []):
            compliance_map.evidence.append(ClauseEvidence(
                standard="SOC 2",
                clause_id=control["control"],
                title=control["title"],
                rationale=control["rationale"],
                artifact_type=artifact_type,
                evidence_files=files,
                frameworks=frameworks,
            ))

        # ISO/IEC 17025:2017
        for clause in mapping["clauses"].get("iso_17025", []):
            compliance_map.evidence.append(ClauseEvidence(
                standard="ISO/IEC 17025:2017",
                clause_id=clause["clause"],
                title=clause["title"],
                rationale=clause["rationale"],
                artifact_type=artifact_type,
                evidence_files=files,
                frameworks=frameworks,
            ))

    return compliance_map


def group_by_clause(compliance_map: ComplianceMap) -> dict[str, dict[str, list[ClauseEvidence]]]:
    """Group evidence by standard and clause for report generation.

    Returns:
        {standard: {clause_id: [ClauseEvidence, ...]}}
    """
    grouped: dict[str, dict[str, list[ClauseEvidence]]] = {}
    for ev in compliance_map.evidence:
        grouped.setdefault(ev.standard, {}).setdefault(ev.clause_id, []).append(ev)
    return grouped
