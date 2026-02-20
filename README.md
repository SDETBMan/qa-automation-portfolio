# qa-automation-portfolio

[![playwright-dotnet CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/playwright-dotnet.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/playwright-dotnet.yml)
[![selenium-java CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/selenium-java.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/selenium-java.yml)
[![cucumber CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cucumber.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cucumber.yml)

A monorepo housing three production-quality test automation frameworks demonstrating
the skills and patterns required of a senior SDET: parallel execution, fixtures,
network interception, trace viewer, cross-browser testing, BDD, and CI/CD pipelines.

---

## Frameworks

| Framework | Language | Stack | Status | README |
|---|---|---|---|---|
| [`playwright-dotnet`](./playwright-dotnet/) | C# + TypeScript | Playwright 1.44 · NUnit · .NET 8 · TS 5.4 | ✅ Active | [→](./playwright-dotnet/README.md) |
| [`selenium-java`](./selenium-java/) | Java | Selenium 4 · TestNG · Maven | 🔄 Migrating | [→](./selenium-java/README.md) |
| [`cucumber`](./cucumber/) | TBD | Cucumber-JVM / Cucumber.js | 🚧 In development | [→](./cucumber/README.md) |

---

## Key Features (across all frameworks)

| Feature | playwright-dotnet | selenium-java | cucumber |
|---|---|---|---|
| Page Object Model | ✅ C# + TypeScript | ✅ Java | 🚧 |
| Parallel execution | ✅ `[Parallelizable]` + `fullyParallel` | 🔄 | 🚧 |
| Fixtures / base classes | ✅ `AuthenticatedTest` + `test.extend` | 🔄 | 🚧 |
| Network interception | ✅ 4 patterns (C# + TS) | — | — |
| Trace viewer | ✅ retain-on-failure | — | — |
| Cross-browser | ✅ Chromium / Firefox / WebKit | 🔄 | 🚧 |
| Retries | ✅ `[Retry]` + `retries: 2` in CI | 🔄 | 🚧 |
| BDD / Gherkin | — | — | 🚧 |
| Allure reporting | ✅ | 🔄 | 🚧 |
| GitHub Actions CI | ✅ | ✅ scaffold | ✅ scaffold |
| Data-driven tests | ✅ `[TestCaseSource]` | 🔄 | 🚧 |
| REST API tests | ✅ `HttpClient` | 🔄 | — |

---

## Quick Start

### playwright-dotnet (C# + TypeScript)

**Prerequisites:** [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8) · [Node.js 20 LTS](https://nodejs.org)

```bash
cd playwright-dotnet

# One command — installs deps, browsers, runs both C# and TypeScript suites
bash run-all.sh

# Or with make
make all
```

See [`playwright-dotnet/README.md`](./playwright-dotnet/README.md) for full documentation.

### selenium-java

```bash
cd selenium-java
# Coming soon — migrating from SDETBMan/SeleniumPOMFramework
```

### cucumber

```bash
cd cucumber
# In development
```

---

## Repo Structure

```
qa-automation-portfolio/
├── .github/
│   └── workflows/
│       ├── playwright-dotnet.yml   # fires on: push paths playwright-dotnet/**
│       ├── selenium-java.yml       # fires on: push paths selenium-java/**
│       └── cucumber.yml            # fires on: push paths cucumber/**
├── playwright-dotnet/              # Playwright · NUnit · C# · TypeScript
│   ├── src/                        # C# page objects + utilities
│   ├── tests/
│   │   ├── Framework.Tests/        # NUnit test project
│   │   └── playwright-ts/          # TypeScript Playwright project
│   ├── Makefile
│   └── run-all.sh
├── selenium-java/                  # Selenium · Java · TestNG · Maven
├── cucumber/                       # BDD · Cucumber · Gherkin
├── .gitignore
└── README.md
```

---

## CI Strategy

Each framework has its own workflow with **path filters** — a push that only touches
`playwright-dotnet/` will only trigger the `playwright-dotnet.yml` workflow. The other
suites are not run, keeping CI fast and costs low.

Nightly schedules run all workflows independently on their own cron so the full
portfolio stays green without cross-framework interference.

---

## Target App

All frameworks test [SauceDemo](https://www.saucedemo.com/) — a purpose-built
e-commerce demo with stable, publicly documented test credentials. This allows
full end-to-end automation without any back-end setup.
