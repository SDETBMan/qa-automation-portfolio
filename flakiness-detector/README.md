# Flakiness Detector

Parses JUnit XML test results across multiple CI runs, computes per-test flakiness scores, and generates a severity-ranked report with quarantine recommendations.

## Quick Start

```bash
pip install -r requirements.txt

# Analyze included sample fixtures
python run.py --xml-dir fixtures/

# Custom quarantine threshold
python run.py --xml-dir fixtures/ --threshold 0.20

# Write report to file
python run.py --xml-dir fixtures/ --output report.md
```

## How It Works

1. **Parse** — Reads all JUnit XML files in the target directory
2. **Analyze** — Aggregates outcomes per test across runs; computes `flakiness_score = min(passes, failures) / total_non_skipped`
3. **Report** — Generates markdown ranked by score with QUARANTINE/MONITOR recommendations
4. **DataDog** — Sends `flakiness.score`, `flakiness.quarantined_count`, `flakiness.total_flaky` metrics

## Tests

```bash
pytest tests/ -v
```

## CI

The `flakiness-detector.yml` workflow runs on push to `flakiness-detector/**` and on `workflow_dispatch`.
