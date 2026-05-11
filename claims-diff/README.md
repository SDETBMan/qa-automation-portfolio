# Claims Adjudication Data Diff Engine

Compares two sets of healthcare claim records to detect discrepancies in adjudication results. Demonstrates BigQuery/SQL data validation patterns for claims QA at scale.

## Quick Start

```bash
pip install -r requirements.txt
python run.py
```

## What It Does

- Loads claim records from CSV (or BigQuery when credentials are available)
- Compares baseline vs. current claims by `claim_id`
- Detects: added claims, removed claims, field-level modifications
- Outputs a structured JSON diff report
- Exits non-zero when differences are found (CI-friendly)

## BigQuery Integration

The `differ/loader.py` module includes a `load_from_bigquery()` function that loads claims directly from a BigQuery table. To use it:

1. Install: `pip install google-cloud-bigquery`
2. Configure GCP credentials
3. Update `.env` with your project/dataset/table

## Dataset

The `datasets/` directory contains two synthetic CSV files with 20 claims each. The current file has 5 intentional differences (2 amount changes, 1 status change, 1 added, 1 removed) to demonstrate the diff engine.
