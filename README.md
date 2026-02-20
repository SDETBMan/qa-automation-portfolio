# QA Automation Portfolio

[![playwright-dotnet CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/playwright-dotnet.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/playwright-dotnet.yml)
[![selenium-java CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/selenium-java.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/selenium-java.yml)
[![cucumber CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cucumber.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cucumber.yml)

A monorepo housing three independent, production-grade test automation frameworks — each showcasing a distinct language and testing approach used by senior SDETs in the industry.

---

## Frameworks

| Framework | Language | Stack | README |
|---|---|---|---|
| [`playwright-dotnet`](./playwright-dotnet/) | C# · TypeScript | Playwright 1.44 · NUnit · .NET 8 · TypeScript 5.4 | [→](./playwright-dotnet/README.md) |
| [`selenium-java`](./selenium-java/) | Java | Selenium 4 · TestNG · Maven · Java 17 | [→](./selenium-java/README.md) |
| [`cucumber`](./cucumber/) | Java | Cucumber 7 · TestNG · Selenium 4 · Maven · Java 17 | [→](./cucumber/README.md) |

---

## Feature Coverage

| Capability | playwright-dotnet | selenium-java | cucumber |
|---|---|---|---|
| **Page Object Model** | ✅ C# + TypeScript | ✅ Java | ✅ Java |
| **Parallel execution** | ✅ `[Parallelizable]` · `fullyParallel` | ✅ `ThreadLocal` · `parallel="tests"` | ✅ `ThreadLocal` · `@DataProvider(parallel=true)` |
| **Fixtures / base classes** | ✅ `AuthenticatedTest` · `test.extend<>` | ✅ `BaseTest` | ✅ Cucumber `Hooks` |
| **Retry on failure** | ✅ `[Retry]` · `retries: 2` in CI | ✅ `RetryAnalyzer` + `AnnotationTransformer` | ✅ `RetryAnalyzer` + `AnnotationTransformer` |
| **Cross-browser** | ✅ Chromium · Firefox · WebKit | ✅ Chrome · Firefox · Edge | ✅ Chrome · Firefox · Edge |
| **BDD / Gherkin** | — | — | ✅ 5 feature files · 16+ scenarios |
| **Data-driven tests** | ✅ `[TestCaseSource]` | ✅ `@DataProvider` | ✅ Scenario Outline |
| **REST API testing** | ✅ `HttpClient` | ✅ RestAssured | ✅ RestAssured |
| **Network interception** | ✅ 4 patterns (C# + TS) | — | — |
| **Trace viewer** | ✅ `retain-on-failure` | — | — |
| **Self-healing locators** | — | ✅ Healenium 3.4.8 | ✅ Healenium 3.4.8 |
| **Mobile (Appium)** | — | ✅ Android · iOS | ✅ Android · iOS |
| **Performance (JMeter)** | — | ✅ Maven plugin | ✅ Maven plugin |
| **Database validation** | — | ✅ JDBC / MySQL | ✅ JDBC / MySQL |
| **Containerized infra** | — | ✅ Docker Compose | ✅ Docker Compose |
| **Allure reporting** | ✅ GitHub Pages | ✅ | ✅ GitHub Pages |
| **Slack notifications** | — | ✅ Webhook | ✅ Webhook |
| **GitHub Actions CI** | ✅ | ✅ | ✅ |

---

## Quick Start

### playwright-dotnet (C# + TypeScript)

**Prerequisites:** [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8) · [Node.js 20 LTS](https://nodejs.org)

```bash
cd playwright-dotnet

# One command — installs all deps, browsers, runs C# and TypeScript suites
bash run-all.sh

# Or with make
make all
```

### selenium-java

**Prerequisites:** [Java 17](https://adoptium.net) · [Maven 3.9+](https://maven.apache.org)

```bash
cd selenium-java

# Headless Chrome (default)
mvn clean test -Dheadless=true

# Specific browser
mvn clean test -Dheadless=true -Dbrowser=firefox

# Selenium Grid (start Docker first)
docker compose up -d selenium-hub chrome firefox edge
mvn clean test -PGrid -Dheadless=true

# Performance tests
mvn jmeter:jmeter
```

### cucumber

**Prerequisites:** [Java 17](https://adoptium.net) · [Maven 3.9+](https://maven.apache.org)

```bash
cd cucumber

# Headless Chrome (default)
mvn clean test -Dheadless=true

# Tag filter
mvn clean test -Dheadless=true -Dcucumber.filter.tags="@smoke"

# Full stack with Selenium Grid + Healenium
docker compose up -d
mvn clean test -Dtarget=grid -Dheadless=true

# Performance tests
mvn jmeter:jmeter
```

---

## Repo Structure

```
qa-automation-portfolio/
├── .github/
│   └── workflows/
│       ├── playwright-dotnet.yml   # triggers on: paths playwright-dotnet/**
│       ├── selenium-java.yml       # triggers on: paths selenium-java/**
│       └── cucumber.yml            # triggers on: paths cucumber/**
├── playwright-dotnet/              # Playwright · NUnit · C# · TypeScript
│   ├── tests/
│   │   ├── Framework.Tests/        # NUnit C# test project
│   │   └── playwright-ts/          # TypeScript Playwright project
│   ├── Makefile
│   └── run-all.sh
├── selenium-java/                  # Selenium 4 · TestNG · Java · Maven
│   ├── src/main/java/              # Page objects, driver factory, utilities
│   ├── src/test/java/              # Tests, listeners, unit tests
│   └── testng.xml
├── cucumber/                       # Cucumber 7 · TestNG · Selenium 4 · Java
│   ├── src/main/java/              # Utilities: ConfigReader, RetryAnalyzer, SlackUtils
│   ├── src/test/java/              # Step definitions, runners, page objects
│   ├── src/test/resources/features/
│   └── docker-compose.yaml
├── .gitignore
└── README.md
```

---

## CI Strategy

Each workflow has **path filters** so a push to `selenium-java/` only triggers the `selenium-java.yml` pipeline — the other two frameworks are unaffected. A nightly `cron` schedule keeps the full portfolio green without cross-framework interference.

| Workflow | Trigger | dispatch inputs |
|---|---|---|
| `playwright-dotnet.yml` | push · PR · nightly 02:00 UTC | execution mode · browser · JMeter toggle |
| `selenium-java.yml` | push · PR · nightly 03:00 UTC | browser · suite XML · JMeter toggle |
| `cucumber.yml` | push · PR · nightly 04:00 UTC | execution mode · browser · JMeter toggle |

---

## Target Application

All three frameworks test [SauceDemo](https://www.saucedemo.com/) — a purpose-built e-commerce demo with stable, publicly documented test credentials. No back-end setup is required.

| Page | Coverage |
|---|---|
| Login | Valid login · invalid credentials · locked-out user · data-driven multi-user |
| Dashboard | Cart icon · logout flow · direct-URL security check |
| Inventory | Add item · add multiple · remove item · badge count |
| Cart | Item verification · checkout navigation |
| API | Health check · data integrity (JSONPlaceholder) |
