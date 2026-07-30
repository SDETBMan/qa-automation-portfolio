# Site Drift Detector

Monitors [saucedemo.com](https://www.saucedemo.com) for DOM selector changes that could break the 5 browser automation frameworks in this portfolio (Cypress, Selenium Java, Cucumber Java, Cucumber Python, Playwright .NET).

## Problem

SauceDemo has no changelog or notification system. When they push updates (e.g., lodash bumps, js-yaml bumps, Sauce Visual features), selectors can change without warning — causing test failures discovered only after the fact in CI.

## How It Works

1. **Fetch** — Downloads the HTML page and Vite JS bundle from saucedemo.com
2. **Extract** — Parses all DOM selectors (IDs, classes, data-test attributes) using BeautifulSoup + regex
3. **Compare** — Diffs the current state against a committed baseline snapshot
4. **Report** — Generates a markdown report identifying removed/added selectors and affected frameworks
5. **Alert** — Optionally creates a GitHub issue and sends metrics to DataDog

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate initial baseline
python run.py --update-baseline

# Run drift check (compares against baseline)
python run.py

# Run with report output
python run.py --output drift-report.md

# Auto-create GitHub issue on drift
python run.py --auto-issue
```

## CLI Options

| Option | Description |
|--------|-------------|
| `--url` | Target URL (default: `https://www.saucedemo.com`) |
| `--baseline` | Path to baseline JSON (default: `baseline.json`) |
| `--update-baseline` | Overwrite baseline with current snapshot |
| `--auto-issue` | Create GitHub issue when critical drift detected |
| `--output` | Write markdown report to file |

## Monitored Selectors

The `selectors.json` registry maps 30+ selectors to the frameworks that depend on them. When a monitored selector is removed, the report identifies exactly which test suites are affected.

## Architecture

```
site-monitor/
├── monitor/
│   ├── fetcher.py       # HTTP fetch of HTML + JS bundle
│   ├── extractor.py     # Parse selectors from HTML + JS
│   ├── comparator.py    # Diff current vs baseline
│   ├── reporter.py      # Markdown report + GitHub issue
│   └── datadog.py       # DataDog drift metrics
├── run.py               # CLI entry point (click)
├── baseline.json        # Committed selector baseline
├── selectors.json       # Monitored selector registry
└── tests/               # Unit tests
```

## DataDog Metrics

| Metric | Description |
|--------|-------------|
| `site_monitor.drift_detected` | 1 if drift found, 0 otherwise |
| `site_monitor.selectors_removed` | Count of removed selectors |
| `site_monitor.selectors_added` | Count of added selectors |

Tags: `service:qa-automation-portfolio`, `env:ci`, `target:saucedemo`

## CI

Runs daily at 06:00 UTC via `.github/workflows/site-monitor.yml`. On critical drift (selector removals), automatically creates a GitHub issue tagged `site-drift`.

## Tests

```bash
pytest tests/ -v
```
