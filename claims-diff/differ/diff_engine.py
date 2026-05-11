"""Core diff logic for comparing two sets of claim records."""

from __future__ import annotations

from .models import ClaimDiff, ClaimRecord, DiffReport, FieldDiff

_COMPARE_FIELDS = (
    "patient_id",
    "procedure_code",
    "billed_cents",
    "allowed_cents",
    "paid_cents",
    "status",
    "adjudication_date",
)


def diff_claims(
    baseline: list[ClaimRecord],
    current: list[ClaimRecord],
) -> DiffReport:
    """Compare two claim sets by claim_id. Returns a structured diff report."""
    baseline_map = {c.claim_id: c for c in baseline}
    current_map = {c.claim_id: c for c in current}

    all_ids = sorted(set(baseline_map.keys()) | set(current_map.keys()))
    diffs: list[ClaimDiff] = []
    added = 0
    removed = 0
    modified = 0
    unchanged = 0

    for cid in all_ids:
        b = baseline_map.get(cid)
        c = current_map.get(cid)

        if b is None and c is not None:
            diffs.append(ClaimDiff(claim_id=cid, change_type="added"))
            added += 1
        elif b is not None and c is None:
            diffs.append(ClaimDiff(claim_id=cid, change_type="removed"))
            removed += 1
        elif b is not None and c is not None:
            field_diffs: list[FieldDiff] = []
            for field in _COMPARE_FIELDS:
                bv = getattr(b, field)
                cv = getattr(c, field)
                if bv != cv:
                    field_diffs.append(FieldDiff(
                        field=field,
                        baseline_value=bv,
                        current_value=cv,
                    ))
            if field_diffs:
                diffs.append(ClaimDiff(
                    claim_id=cid,
                    change_type="modified",
                    field_diffs=field_diffs,
                ))
                modified += 1
            else:
                unchanged += 1

    return DiffReport(
        total_baseline=len(baseline),
        total_current=len(current),
        added=added,
        removed=removed,
        modified=modified,
        unchanged=unchanged,
        diffs=diffs,
    )
