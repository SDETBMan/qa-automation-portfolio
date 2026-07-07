# Claims Adjudication Data Diff Engine

Compares two sets of healthcare claim records to detect discrepancies in adjudication results. Demonstrates BigQuery/SQL data validation patterns for claims QA at scale.

## Quick Start

```bash
pip install -r requirements.txt
python run.py
```

Or from the repo root:

```bash
make claims-diff          # run diff against default datasets
make claims-diff-test     # run pytest suite with coverage
```

## What It Does

- Loads claim records from CSV (or BigQuery when credentials are available)
- Compares baseline vs. current claims by `claim_id`
- Detects: added claims, removed claims, field-level modifications
- Outputs a structured JSON diff report
- Exits non-zero when differences are found (CI-friendly)

## Healthcare Validation Rules

The `ClaimRecord` Pydantic model enforces domain-specific constraints:

| Field | Constraint | Rationale |
|---|---|---|
| `claim_id` | `^CLM-\d{3,}$` | Standardised claim identifier format |
| `patient_id` | `^PAT-\d{3,}$` | Standardised patient identifier format |
| `procedure_code` | `^\d{5}$` | CPT codes are 5-digit numeric |
| `billed_cents`, `allowed_cents`, `paid_cents` | `>= 0` | Monetary amounts cannot be negative |
| `status` | `paid \| denied \| pending` | Only valid adjudication statuses accepted |
| `adjudication_date` | ISO 8601 date | Enforced by Pydantic `date` type |

## Test Suite

```bash
pytest tests/ -v --cov=differ --cov-report=term-missing
```

| File | Tests | What it validates |
|---|---|---|
| `tests/test_models.py` | 10 | Pydantic schema enforcement — CPT format, status enum, negative amounts, extra fields, serialization round-trip |
| `tests/test_diff_engine.py` | 12 | Core diff logic — added/removed/modified detection, multi-field changes, empty datasets, real CSV integration |
| `tests/test_loader.py` | 6 | CSV loading — field types, missing columns, empty files, non-numeric values, file-not-found |
| **Total** | **28** | |

## CI Workflow

`claims-diff.yml` — triggers on push/PR to `claims-diff/**` and `workflow_dispatch`:

- Python 3.11, pip cache
- `pytest tests/ -v --junit-xml --cov=differ`
- CLI verification (`python run.py` exits with code 1 on expected diffs)
- JUnit XML + coverage uploaded as 30-day artifacts
- DataDog CI Visibility upload

## BigQuery Integration

The `differ/loader.py` module includes a `load_from_bigquery()` function that loads claims directly from a BigQuery table. To use it:

1. Install: `pip install google-cloud-bigquery`
2. Configure GCP credentials
3. Update `.env` with your project/dataset/table

## Data Generation

The `datasets/generate.py` utility creates synthetic claim datasets at any scale with controlled diff injection — useful for load testing, exploratory QA, or seeding test environments.

```bash
python datasets/generate.py                          # 100 claims, 10 diffs
python datasets/generate.py --count 500 --diffs 25   # custom sizes
python datasets/generate.py --seed 42                # reproducible output

# Run the diff engine against generated data
python run.py --baseline datasets/baseline_generated.csv --current datasets/current_generated.csv
```

Generated files (`baseline_generated.csv`, `current_generated.csv`) are written to `datasets/` and never overwrite the hand-crafted originals.

## Parallel Execution

The test suite runs in parallel via `pytest-xdist`. The `pytest.ini` configures `-n auto --dist=loadscope` — auto-detecting CPU cores and grouping tests by class to match the existing class-organised structure. No test changes required; the suite has no global state or autouse fixtures.

```bash
pytest tests/ -v -n auto --dist=loadscope --cov=differ
```

## Dataset

The `datasets/` directory contains two synthetic CSV files with 20 claims each. The current file has 5 intentional differences (2 amount changes, 1 status change, 1 added, 1 removed) to demonstrate the diff engine.
