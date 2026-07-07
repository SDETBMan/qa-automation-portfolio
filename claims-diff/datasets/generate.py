#!/usr/bin/env python3
"""Synthetic claim dataset generator for QA testing.

Generates realistic healthcare claim CSVs with configurable size and
controlled diff injection — enabling reproducible test data for the
claims-diff engine at any scale.

Usage:
    python datasets/generate.py                          # 100 claims, 10 diffs
    python datasets/generate.py --count 500 --diffs 25   # custom sizes
    python datasets/generate.py --seed 42                # reproducible output
    python datasets/generate.py --days 180               # 180-day date range
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
from datetime import date, timedelta
from pathlib import Path

_HERE = Path(__file__).resolve().parent

# Common E/M CPT codes used in outpatient claims
_CPT_CODES = ["99213", "99214", "99215", "99203", "99204", "99205", "99211", "99212"]
_CPT_WEIGHTS = [25, 20, 10, 15, 10, 5, 10, 5]  # weighted toward 99213/99214

# Adjudication status distribution
_STATUSES = ["paid", "denied", "pending"]
_STATUS_WEIGHTS = [75, 15, 10]

_FIELDNAMES = [
    "claim_id",
    "patient_id",
    "procedure_code",
    "billed_cents",
    "allowed_cents",
    "paid_cents",
    "status",
    "adjudication_date",
]


def _generate_claim(index: int, rng: random.Random, end_date: date, days: int) -> dict:
    """Generate a single realistic claim record."""
    claim_id = f"CLM-{index:03d}"
    patient_id = f"PAT-{100 + index:03d}"
    procedure_code = rng.choices(_CPT_CODES, weights=_CPT_WEIGHTS, k=1)[0]

    billed_cents = rng.randint(5000, 50000)
    allowed_pct = rng.uniform(0.75, 0.85)
    allowed_cents = int(billed_cents * allowed_pct)
    paid_pct = rng.uniform(0.75, 0.85)
    paid_cents = int(allowed_cents * paid_pct)

    status = rng.choices(_STATUSES, weights=_STATUS_WEIGHTS, k=1)[0]
    adj_date = end_date - timedelta(days=rng.randint(0, days - 1))

    return {
        "claim_id": claim_id,
        "patient_id": patient_id,
        "procedure_code": procedure_code,
        "billed_cents": billed_cents,
        "allowed_cents": allowed_cents,
        "paid_cents": paid_cents,
        "status": status,
        "adjudication_date": adj_date.isoformat(),
    }


def _inject_diffs(
    baseline: list[dict], num_diffs: int, rng: random.Random, end_date: date, days: int,
) -> list[dict]:
    """Create a current dataset by injecting controlled diffs into a copy of baseline.

    Diff distribution:
      ~40% — modify billed_cents (amount reprocessing)
      ~20% — modify status (adjudication change)
      ~20% — add new claim (late filing)
      ~20% — remove claim (voided/reversed)
    """
    current = [dict(row) for row in baseline]
    max_index = max(int(row["claim_id"].split("-")[1]) for row in current)

    if num_diffs > len(current):
        print(
            f"warning: requested {num_diffs} diffs but only {len(current)} claims; "
            f"capping at {len(current)}",
            file=sys.stderr,
        )
        num_diffs = len(current)

    # Decide how many of each diff type
    n_modify_amount = max(1, int(num_diffs * 0.4))
    n_modify_status = max(1, int(num_diffs * 0.2))
    n_add = max(1, int(num_diffs * 0.2))
    n_remove = num_diffs - n_modify_amount - n_modify_status - n_add

    # Pick indices for modification (no overlap)
    modifiable = list(range(len(current)))
    rng.shuffle(modifiable)

    # Amount modifications
    for i in modifiable[:n_modify_amount]:
        original = current[i]["billed_cents"]
        delta = rng.choice([-1, 1]) * rng.randint(1000, 10000)
        new_billed = max(1000, int(original) + delta)
        current[i]["billed_cents"] = new_billed
        allowed_pct = rng.uniform(0.75, 0.85)
        current[i]["allowed_cents"] = int(new_billed * allowed_pct)
        paid_pct = rng.uniform(0.75, 0.85)
        current[i]["paid_cents"] = int(current[i]["allowed_cents"] * paid_pct)

    # Status modifications
    offset = n_modify_amount
    for i in modifiable[offset : offset + n_modify_status]:
        old_status = current[i]["status"]
        new_status = rng.choice([s for s in _STATUSES if s != old_status])
        current[i]["status"] = new_status

    # Remove claims (voided/reversed)
    offset += n_modify_status
    remove_indices = sorted(modifiable[offset : offset + n_remove], reverse=True)
    for i in remove_indices:
        current.pop(i)

    # Add new claims (late filing)
    for j in range(n_add):
        max_index += 1
        new_claim = _generate_claim(max_index, rng, end_date, days)
        current.append(new_claim)

    return current


def _write_csv(records: list[dict], path: Path) -> None:
    """Write claim records to a CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python datasets/generate.py",
        description="Generate synthetic claim datasets for QA testing.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of baseline claims to generate (default: 100)",
    )
    parser.add_argument(
        "--diffs",
        type=int,
        default=10,
        help="Number of diffs to inject into the current dataset (default: 10)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible output",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Date range in days for adjudication dates (default: 90)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory (default: datasets/)",
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    end_date = date.today()
    output_dir = Path(args.output_dir) if args.output_dir else _HERE

    # Generate baseline
    baseline = [_generate_claim(i + 1, rng, end_date, args.days) for i in range(args.count)]

    # Inject diffs to create current
    current = _inject_diffs(baseline, args.diffs, rng, end_date, args.days)

    # Write CSVs (never overwrite the hand-crafted datasets)
    baseline_path = output_dir / "baseline_generated.csv"
    current_path = output_dir / "current_generated.csv"

    _write_csv(baseline, baseline_path)
    _write_csv(current, current_path)

    print(f"  Baseline: {baseline_path} ({len(baseline)} claims)")
    print(f"  Current:  {current_path} ({len(current)} claims)")
    print(f"  Diffs injected: {args.diffs}")
    if args.seed is not None:
        print(f"  Seed: {args.seed}")
    print()
    print("  Run the diff engine against generated data:")
    print(f"    python run.py --baseline {baseline_path} --current {current_path}")


if __name__ == "__main__":
    main()
