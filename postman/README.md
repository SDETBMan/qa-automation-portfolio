[![postman-newman CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/postman-newman.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/postman-newman.yml)

# Postman / Newman API Test Framework

![JavaScript](https://img.shields.io/badge/Language-JavaScript-yellow)
![Postman](https://img.shields.io/badge/Tool-Postman-orange)
![Newman](https://img.shields.io/badge/CLI-Newman-blue)

A production-grade API test suite built with **Postman Collection v2.1** and executed headlessly via **Newman CLI**, covering four testing layers (smoke, functional, write-operation, and integration) against the [JSONPlaceholder](https://jsonplaceholder.typicode.com) REST API.

## Key Features

* **Four Test Layers:** Smoke connectivity checks, Users CRUD + negative-path tests, Posts write-operation validation, and a chained Integration Flow scenario.
* **Request Chaining:** The Integration Flow folder captures a `userId` from Step 1's response and injects it into Step 2's query parameter, demonstrating cross-request state management with collection variables.
* **Pre-request Scripts:** Dynamic payload generation using `Date.now()` timestamps prevents test pollution between runs; stored variables are cleaned up post-assertion.
* **Negative Path Coverage:** Explicit 404 test for a non-existent user (`GET /users/999`) validates error-handling behavior alongside happy-path tests.
* **Dual Reporting:** JUnit XML for CI Visibility and DataDog integration; `htmlextra` HTML report for human-readable run summaries.
* **CI/CD Ready:** GitHub Actions pipeline with a `workflow_dispatch` folder filter to run: Smoke, Users, Posts, or Integration Flow independently without modifying the collection.
* **DataDog CI Visibility:** JUnit XML results uploaded to DataDog Test Optimization on every run for pass/fail trend tracking and duration metrics.

## Tech Stack

| Layer | Technology |
|---|---|
| Collection format | Postman Collection v2.1 JSON |
| CLI runner | Newman 6.2.1 |
| HTML reporter | newman-reporter-htmlextra 1.22.11 |
| Runtime | Node.js 20 LTS |
| CI/CD | GitHub Actions |
| Observability | DataDog CI Visibility (JUnit XML) |

## Test Coverage

| Folder | Requests | What is tested |
|---|---|---|
| **Smoke** | 2 | `GET /users/1` and `GET /posts/1` → status 200, response time < 3 s, Content-Type header, required fields present |
| **Users** | 3 | List all users (array length, field schema), single user (data integrity, nested address/company objects), non-existent user (404 + empty body) |
| **Posts** | 3 | List all posts (array length, field schema), create post with dynamic payload (201, echo validation), delete post (200, empty body) |
| **Integration Flow** | 2 | Capture `userId` from `GET /users/1` → filter `GET /posts?userId=` and assert every returned post belongs to that user |

**Total: 10 requests · 28 test assertions**

## How to Run

**Prerequisite:** [Node.js 20 LTS](https://nodejs.org)

```bash
# Install Newman and reporters
npm install

# Run full collection (all 4 folders), outputs JUnit XML
npm test

# Smoke folder only (fast connectivity check)
npm run test:smoke

# Verbose output with request/response details
npm run test:verbose

# HTML report (results/newman-report.html)
npm run test:html
```

> Results are written to the `results/` directory. JUnit XML (`newman-results.xml`) is consumed by CI; HTML report (`newman-report.html`) is for local inspection.

## CI/CD Pipeline

The `postman-newman.yml` workflow triggers on every push/PR to `main` that touches `postman/**`, on a nightly schedule (`07:00 UTC`), and via `workflow_dispatch`.

**Manual dispatch input:**

| Input | Description |
|---|---|
| `folder` | Newman folder to target: `Smoke`, `Users`, `Posts`, or `Integration Flow`. Leave blank to run all four. |

**Pipeline steps:**

1. Checkout code
2. Set up Node.js 20
3. `npm install` (Newman + htmlextra)
4. Run Newman — full collection or targeted folder based on dispatch input
5. Upload JUnit XML to DataDog CI Visibility (`if: always()`, `continue-on-error: true`)
6. Upload `newman-results.xml` as a workflow artifact (retained 30 days)

> **Secret required:** `DD_API_KEY` in repository secrets enables DataDog CI Visibility. The upload step skips gracefully without it, while the CI stays green.

## Project Structure

```
postman/
├── collections/
│   └── jsonplaceholder.postman_collection.json   # 10 requests across 4 folders
├── environments/
│   └── jsonplaceholder.postman_environment.json  # baseUrl · defaultUserId · defaultPostId
├── results/
│   ├── newman-results.xml                        # JUnit XML (git-ignored, CI artifact)
│   └── newman-report.html                        # htmlextra report (git-ignored)
└── package.json                                  # Newman + htmlextra · npm scripts
```

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `baseUrl` | `https://jsonplaceholder.typicode.com` | API base URL; use `-e` to target staging |
| `defaultUserId` | `1` | User ID used in single-resource and data-integrity tests |
| `defaultPostId` | `1` | Post ID used in the DELETE test |
