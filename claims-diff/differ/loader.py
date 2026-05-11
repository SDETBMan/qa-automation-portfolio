"""Load claims from CSV or BigQuery."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from .models import ClaimRecord


def load_claims_csv(path: Path) -> list[ClaimRecord]:
    """Load claim records from a CSV file."""
    records: list[ClaimRecord] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(ClaimRecord(
                claim_id=row["claim_id"],
                patient_id=row["patient_id"],
                procedure_code=row["procedure_code"],
                billed_cents=int(row["billed_cents"]),
                allowed_cents=int(row["allowed_cents"]),
                paid_cents=int(row["paid_cents"]),
                status=row["status"],
                adjudication_date=date.fromisoformat(row["adjudication_date"]),
            ))
    return records


def load_from_bigquery(project: str, dataset: str, table: str) -> list[ClaimRecord]:
    """Load claims from BigQuery. Requires google-cloud-bigquery.

    This demonstrates the BigQuery integration pattern. When BQ credentials
    are available, this loads directly from a warehouse table.
    """
    try:
        from google.cloud import bigquery  # optional dependency
    except ImportError:
        raise RuntimeError(
            "google-cloud-bigquery is not installed. "
            "Install it with: pip install google-cloud-bigquery"
        )

    client = bigquery.Client(project=project)
    query = f"SELECT * FROM `{project}.{dataset}.{table}`"
    df = client.query(query).to_dataframe()
    return [ClaimRecord(**row) for _, row in df.iterrows()]
