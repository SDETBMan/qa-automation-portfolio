# QMS Evidence Collector

Scans the monorepo for CI artifacts (test results, security scans, coverage reports, contract tests, performance baselines, drift reports) and maps them to compliance clauses across three standards:

- **ISO 9001:2015** — Quality Management Systems
- **SOC 2 (CC-series)** — Trust Services Criteria
- **ISO/IEC 17025:2017** — Testing and Calibration Laboratories

Generates a structured evidence report for audit preparation, with gap analysis and DataDog metrics.

## Quick Start

```bash
pip install -r requirements.txt
python run.py                              # Scan monorepo, print markdown report
python run.py --output evidence.json       # JSON report
python run.py --standard iso9001           # Filter to ISO 9001 only
python run.py --output evidence.md         # Save markdown report
```

## How It Works

1. **Scan** — Walks the monorepo and matches files against known artifact patterns (JUnit XML, ZAP reports, coverage files, Pact contracts, k6 results, etc.)
2. **Map** — Each artifact type is mapped to specific clauses via `mappings/clause_registry.json`
3. **Report** — Generates markdown or JSON report with clause-level evidence, rationale, and gap analysis
4. **Metrics** — Sends coverage counts to DataDog (`qms.clauses_covered`, `qms.iso9001_clauses`, etc.)

## Artifact Types Mapped

| Artifact | Source Frameworks | Example Clause |
|----------|------------------|----------------|
| JUnit/TRX XML | All test frameworks | ISO 9001 8.6 — Release of products |
| Coverage reports | Cypress, pytest | ISO 9001 8.5.1 — Control of production |
| ZAP reports | Playwright, Cypress, Selenium, Cucumber | SOC 2 CC6.1 — Logical access security |
| Flakiness reports | flakiness-detector | ISO 9001 7.1.5.2 — Measurement traceability |
| Pact contracts | pact-consumer, fastapi-service | ISO 9001 8.4.2 — External provision control |
| k6 SLO results | fastapi-service | ISO 9001 9.1.1 — Monitoring and measurement |
| Drift baselines | site-monitor | ISO 9001 8.5.6 — Control of changes |
| Allure reports | Playwright, Selenium, Cucumber | ISO 9001 7.5.1 — Documented information |
| Dependency scans | Dependabot, CodeQL | SOC 2 CC3.1 — Risk assessment |
| Triage reports | failure-triage | ISO 9001 10.2 — Corrective action |

## Project Structure

```
qms-evidence-collector/
├── run.py                        # Click CLI entry point
├── collector/
│   ├── scanner.py                # Repo walker + artifact pattern matching
│   ├── mapper.py                 # Artifact → clause mapping engine
│   ├── reporter.py               # Markdown + JSON report generation
│   └── datadog.py                # DataDog GAUGE metrics
├── mappings/
│   └── clause_registry.json      # Artifact-to-clause definitions
├── tests/
│   ├── test_scanner.py           # 16 tests — scanner + registry validation
│   ├── test_mapper.py            # 15 tests — clause mapping logic
│   └── test_reporter.py          # 14 tests — report generation
├── datadog-dashboard.json        # DataDog dashboard import
└── requirements.txt
```

## Tests

```bash
pytest tests/ -v
```

## DataDog Metrics

| Metric | Description |
|--------|-------------|
| `qms.clauses_covered` | Total unique clauses across all standards |
| `qms.evidence_files` | Total artifact files discovered |
| `qms.iso9001_clauses` | ISO 9001 clause count |
| `qms.soc2_controls` | SOC 2 control count |
| `qms.iso17025_clauses` | ISO/IEC 17025 clause count |
