# Branch Collision Monitor

Early-warning system that detects when active branches are on a collision course. Finds file-level overlaps and optionally uses Claude to assess semantic conflict likelihood — before merge conflicts happen.

## Problem

AI-accelerated development means developers push 50K+ lines/day. Traditional coordination ("hey, I'm about to push") doesn't scale. This tool provides early warning when active branches modify the same files, scoring severity and identifying the highest-risk hot zones.

## Architecture

```
CLI (run.py)
  -> github_api.py    — fetch branches + diffs via gh CLI
  -> analyzer.py      — detect hot zones, score severity
  -> semantic.py      — optional Claude semantic overlap analysis
  -> reporter.py      — JSON + Markdown reports
  -> datadog.py       — optional DataDog metrics
```

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11+ |
| GitHub API | `gh` CLI (subprocess) |
| Semantic Analysis | Anthropic Claude (`claude-haiku-4-5`) |
| Metrics | DataDog v2 Gauge API |
| Reports | JSON + Markdown |

## Scoring Algorithm

Three-layer severity scoring:

1. **File categorization**: source (1.0), config (0.8), test (0.7), ci (0.6), docs (0.2)
2. **Per-file severity**: `(overlap_count / total_branches) * category_weight + min(lines_changed / 500, 0.3)`, capped at 1.0
3. **Overall risk**: `sum(severity_scores) / total_files`, mapped to LOW / MODERATE / HIGH / CRITICAL

## How to Run

### Prerequisites

- Python 3.11+
- `gh` CLI installed and authenticated (`gh auth login`)

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Analyze a repository
python run.py --repo owner/repo

# With file output
python run.py --repo owner/repo --output report --format both

# With Claude semantic analysis
python run.py --repo owner/repo --semantic --max-semantic 5
```

### CLI Options

| Flag | Default | Description |
|---|---|---|
| `--repo` | (required) | GitHub repository (`owner/repo`) |
| `--base` | auto-detect | Base branch to compare against |
| `--limit` | 20 | Maximum branches to analyze |
| `--format` | markdown | Output format: `json`, `markdown`, `both` |
| `--output` | stdout | File path (writes `.json` and/or `.md`) |
| `--semantic` | off | Enable Claude semantic conflict analysis |
| `--max-semantic` | 10 | Maximum semantic API calls |

### Run Tests

```bash
pip install -r requirements.txt pytest
pytest tests/ -v
```

## Graceful Degradation

| Missing | Behavior |
|---|---|
| `gh` CLI | Warns, returns empty branch list |
| `ANTHROPIC_API_KEY` | Skips semantic analysis, structural analysis still runs |
| `DD_API_KEY` | Skips DataDog metrics silently |

## DataDog Metrics

| Metric | Type | Description |
|---|---|---|
| `branch_collision.risk_level` | gauge | 0=LOW, 1=MODERATE, 2=HIGH, 3=CRITICAL |
| `branch_collision.overall_score` | gauge | 0.0 - 1.0 severity score |
| `branch_collision.branches_analyzed` | gauge | Number of branches scanned |
| `branch_collision.overlapping_files` | gauge | Files touched by 2+ branches |
| `branch_collision.semantic_conflicts` | gauge | High/medium semantic conflicts |

## Example Output

```
[INFO] Repository: SDETBMan/qa-automation-portfolio
[INFO] Base branch: main
[INFO] Fetching active branches (limit: 20)...
[INFO] Found 5 branches to analyze.
[INFO] Fetching diff 1/5: feature/auth-refactor
...

[RESULT] Risk: MODERATE (score: 0.2500)
[RESULT] Overlapping files: 3
```

## Repo Structure

```
branch-collision-monitor/
  run.py                    CLI entry point
  requirements.txt          Python dependencies
  .env.example              Environment variable template
  pytest.ini                Pytest configuration
  monitor/
    __init__.py             Package marker
    analyzer.py             Dataclasses + scoring engine
    github_api.py           gh CLI integration
    reporter.py             JSON + Markdown reports
    semantic.py             Claude semantic analysis
    datadog.py              DataDog metrics
  tests/
    __init__.py             Package marker
    test_analyzer.py        Scoring + categorization tests
    test_github_api.py      Diff parsing tests
    test_reporter.py        Report format validation
    fixtures/
      sample_branches.json  Mock branch listing
      sample_diff_branch_a.txt  Mock unified diff
      sample_diff_branch_b.txt  Mock unified diff
```
