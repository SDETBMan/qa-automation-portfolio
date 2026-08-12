# Dependency Audit

A CLI tool that scans all frameworks in the monorepo, detects outdated dependencies, and optionally auto-updates them.

## Supported Ecosystems

| Ecosystem | Manifest | Registry |
|-----------|----------|----------|
| npm | `package.json` | registry.npmjs.org |
| pip | `requirements.txt` | pypi.org |
| NuGet | `*.csproj` | api.nuget.org |
| Maven | `pom.xml` | search.maven.org |

## Quick Start

```bash
cd dependency-audit
pip install -r requirements.txt

# Audit all frameworks
python run.py --repo-dir ..

# Audit + auto-update
python run.py --repo-dir .. --update

# npm only
python run.py --repo-dir .. --ecosystem npm

# Save report to file
python run.py --repo-dir .. --output report.md
```

## CLI Options

| Option | Description |
|--------|-------------|
| `--repo-dir` | Path to the monorepo root (required) |
| `--ecosystem` | Filter to a single ecosystem: npm, pip, nuget, maven, go |
| `--update` | Auto-update outdated dependencies in manifests |
| `--output` | Write markdown report to a file (default: stdout) |

## Report Format

```
| Framework | File | Package | Current | Latest | Status |
|-----------|------|---------|---------|--------|--------|
| playwright | package.json | @playwright/test | 1.44.0 | 1.52.0 | outdated |
| cypress | package.json | cypress | 13.6.0 | 13.15.0 | outdated |
```

## CI Integration

The `dependency-audit.yml` workflow runs weekly on a cron schedule:
- Scans all frameworks for outdated dependencies
- Uploads the report as a build artifact
- Optionally creates a PR with auto-updated versions

## Architecture

```
dependency-audit/
├── run.py                    # CLI entry point (Click)
├── auditor/
│   ├── scanner.py            # Repo walker — discovers manifests
│   ├── checkers.py           # Per-ecosystem version checkers
│   ├── updater.py            # Writes updated versions to manifests
│   └── reporter.py           # Markdown report generator
├── requirements.txt          # click, requests
└── README.md
```
