# Architecture & Review Rules Reference

Distilled from CLAUDE.md and REVIEW.md for quick consultation during verification.

## Page Object Model (POM)

- Every browser framework uses POM with a `BasePage` superclass
- Locators and page interactions live in page objects under `pages/`, never in test files
- New pages get their own class extending `BasePage` — never modify `BasePage` for page-specific logic
- Tests call page methods; tests never reference selectors directly

## Test data separation

| Framework | Pattern |
|-----------|---------|
| Cypress | `cy.fixture()` loading from `cypress/fixtures/*.json` |
| Java (Selenium/Cucumber) | `@DataProvider`, `Examples` tables, `config.properties` |
| Python (Pytest) | `@pytest.mark.parametrize` with JSON datasets in `datasets/` |
| Python (Behave) | `Scenario Outline` with `Examples`; `config.ini` for env |

Never hardcode test data in test methods.

## Configuration management

- Environment values (URLs, credentials, timeouts, browser) go in `.env` or `config.properties`
- Always provide `.env.example` when adding new env vars
- DataDog integration skips silently when `DD_API_KEY` is absent

## DRY utilities

- Cypress: custom commands in `support/commands.ts` (`cy.login()`, `cy.addToCart()`)
- Python Behave: Tasks in `utils/tasks.py` (Screenplay pattern)
- Java: Service layer in `services/` separates orchestration from page mechanics
- BasePage: waits, clicks, text retrieval — use inherited helpers, don't duplicate

## What constitutes an Important finding

These are blocking issues that must be fixed:

1. **Breaks test execution** or produces false passes/failures
2. **Introduces flaky tests** — race conditions, missing waits, non-deterministic assertions
3. **Leaks credentials** — API keys, PII in committed code
4. **Violates POM** — selectors or UI interactions in test files
5. **Hardcodes test data** — URLs, credentials in source instead of fixtures/config
6. **Creates cross-framework coupling** — one framework depending on another's code/config
7. **Breaks CI isolation** — workflow triggering unrelated frameworks

## Test reliability checks

- Explicit waits use `BasePage` utilities, not `Thread.sleep()` or `cy.wait(ms)`
- Assertions verify specific conditions, not just "page loaded"
- Tests include proper tagging (`smoke`, `regression`, `safety`)
- Session-scoped fixtures for expensive resources; function-scoped for stateful objects

## CI/CD rules

- Each workflow triggers only on its own path (e.g., `cypress/**`)
- All workflows support `workflow_dispatch`
- JUnit XML output required for DataDog CI Visibility
- Never cross-wire triggers between frameworks

## What NOT to report

- Formatting/style issues (defer to linters)
- Type annotation gaps in unmodified code
- Missing docstrings on unchanged code
- Dependency version ranges unless known CVE
- Generated files (`allure-results/`, `test-results/`, `*.lock`, `output/`)
