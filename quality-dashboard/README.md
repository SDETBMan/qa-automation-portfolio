# Quality KPI Dashboard

Aggregates test results across all frameworks in the monorepo, computes derived quality KPIs, sends them to DataDog, and produces a VP-level JSON report.

**Stack:** Python 3.11 · JUnit XML · DataDog v2 API · GitHub Actions API (gh CLI)

---

## KPI Definitions

| KPI | Formula | Business Meaning | Data Source |
|-----|---------|-----------------|-------------|
| **Pass Rate** | `passed / total` | Percentage of tests passing — primary quality signal | JUnit XML |
| **Failure Density** | `failed / total` | Proportion of test failures — inverse of pass rate, useful for severity ranking | JUnit XML |
| **Avg Duration** | `mean(test.time_s)` | Mean test execution time — tracks performance regressions | JUnit XML |
| **p95 Duration** | `percentile(test.time_s, 95)` | 95th percentile execution time — catches slow outliers | JUnit XML |
| **Suite Stability** | `mean(pass_rates[-N:])` | Pass rate trend over last N runs — detects deteriorating suites | Historical runs |
| **Flakiness Rate** | `flaky_tests / total` | Percentage of tests exhibiting intermittent pass/fail — from flakiness-detector | flakiness-detector |
| **MTTD** | `mean(conclusion_time - push_time)` | Mean Time to Detect — seconds from code push to CI failure notification | GitHub Actions API |
| **MTTR** | `mean(next_pass.updated_at - failure.created_at)` | Mean Time to Recovery — seconds from failure to next successful run | GitHub Actions API |
| **Total Tests** | `sum(total)` | Portfolio-wide test count across all frameworks | JUnit XML |

---

## How to Run

```bash
# Parse local JUnit XML files and compute KPIs
python run.py --xml-dir ../flakiness-detector/fixtures/

# Write JSON report to file
python run.py --xml-dir ./results/ --output report.json

# Fetch MTTD and stability from GitHub Actions API
python run.py --from-github --repo SDETBMan/qa-automation-portfolio

# Both: local XML + GitHub Actions data
python run.py --xml-dir ./results/ --from-github
```

**Requirements:**
- Python 3.11+
- `requests` (for DataDog API)
- `gh` CLI authenticated (for `--from-github` mode, optional)
- `DD_API_KEY` environment variable (optional — gracefully skips if absent)

---

## Dashboard Preview

The `quality-kpi-dashboard.json` file can be imported directly into DataDog (Dashboards → New Dashboard → Import Dashboard JSON).

**Layout (12-column grid):**

| Row | Widget | Description |
|-----|--------|-------------|
| 0 | Header note | "Quality KPIs: Portfolio-Wide Test Health" |
| 1 | 4 gauge widgets | Overall Pass Rate · Failure Density · Suite Stability · MTTD |
| 6 | MTTR gauge + trend | MTTR (seconds) gauge · MTTR Trend line |
| 2 | Timeseries | Pass rate trend over time, per framework (stacked line chart) |
| 3 | Timeseries | Test execution duration trends (p95) |
| 4 | Top list + Heatmap | Frameworks ranked by failure density (worst first) + Test outcomes heatmap |
| 5 | Gauges + Trend | Flakiness Rate · Total Tests · MTTD Trend |

All widgets use conditional formatting: green (healthy) → yellow (warning) → red (critical).

---

## DataDog Metrics Reference

| Metric | Description | Tags |
|--------|-------------|------|
| `kpi.pass_rate` | Overall pass rate (0–1) | `framework:<name>`, `framework:aggregate` |
| `kpi.failure_density` | Failures / total tests | `framework:<name>`, `framework:aggregate` |
| `kpi.avg_duration_s` | Mean test execution time | `framework:<name>` |
| `kpi.p95_duration_s` | 95th percentile duration | `framework:<name>` |
| `kpi.total_tests` | Total test count | `framework:<name>`, `framework:aggregate` |
| `kpi.suite_stability` | Pass rate over last N runs | `framework:aggregate` |
| `kpi.flakiness_rate` | Flaky test percentage | `framework:aggregate` |
| `kpi.mttd_seconds` | Mean time to detect (commit → failure) | `framework:aggregate` |
| `kpi.mttr_seconds` | Mean time to recovery (failure → next pass) | `framework:aggregate` |

All metrics tagged with `service:qa-automation-portfolio`, `env:ci`.

---

## Architecture

```
quality-dashboard/
├── kpi_calculator.py          # Core KPI computation engine (FrameworkKPI, AggregateKPI)
├── datadog_reporter.py        # Send KPI metrics to DataDog v2 API
├── github_actions.py          # Fetch workflow run history for MTTD via gh CLI
├── run.py                     # CLI entry point
├── quality-kpi-dashboard.json # DataDog dashboard JSON (import-ready)
└── README.md
```

Reuses `flakiness-detector/flakiness/parser.py` for JUnit XML parsing — no duplication.
