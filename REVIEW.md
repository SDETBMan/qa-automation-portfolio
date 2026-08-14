# Review instructions

## What Important means here

Reserve Important for findings that would:
- Break test execution or produce false passes/failures
- Introduce flaky tests (race conditions, missing waits, non-deterministic assertions)
- Leak credentials, API keys, or PII in committed code
- Violate POM architecture (selectors or UI interactions in test files)
- Hardcode test data, URLs, or credentials in source code instead of fixtures/config
- Create coupling between independent framework directories
- Break CI pipeline isolation (one workflow triggering unrelated frameworks)

## Cap the nits

Report at most five Nits per review. If more are found, say "plus N similar items" in the summary.

## Do not report

- Formatting and style issues — defer to each framework's linter (ESLint, ruff, Checkstyle)
- Type annotation gaps in code that was not modified by the PR
- Missing docstrings or comments on unchanged code
- Dependency version ranges in requirements.txt or package.json unless there is a known CVE
- Generated files: `allure-results/`, `test-results/`, `*.lock`, `output/`
- Fixture data files (`*.json` in `fixtures/` or `datasets/`) unless they contain secrets

## Always check

### Architecture (POM, SOLID, DRY)
- Page objects extend `BasePage` and own all locators — tests never reference selectors directly
- New pages get their own class; existing `BasePage` is extended, not modified with page-specific logic
- Repeated logic (3+ occurrences) is extracted to a shared utility, custom command, or task
- Each test file covers one feature area; each page class owns one page

### Test data separation
- No hardcoded test data in test methods — use fixtures, `@DataProvider`, `@pytest.mark.parametrize`, or Scenario Outline
- Cypress tests load data via `cy.fixture()`, not inline objects
- Python tests use JSON datasets in `datasets/` with parametrize, not inline dicts

### Configuration management
- New environment variables have a corresponding `.env.example` update
- URLs, credentials, timeouts, and browser settings come from config files or env vars
- DataDog reporter calls degrade gracefully when `DD_API_KEY` is absent

### CI/CD integrity
- Workflow changes only affect the workflow for the modified framework
- Path filters in `on.push.paths` and `on.pull_request.paths` match the framework directory
- JUnit XML output is included for DataDog CI Visibility upload
- Secrets are never logged or echoed in workflow steps

### Test reliability
- Explicit waits use `BasePage` utilities, not `Thread.sleep()` or `cy.wait(ms)`
- Assertions verify specific conditions, not just "page loaded"
- Tests include proper tagging/grouping (`smoke`, `regression`, `safety`, etc.)
- Session-scoped fixtures are used for expensive resources (API clients, vector stores)
- Function-scoped fixtures are used for stateful objects requiring reset between tests

### Security
- No `.env` files, API keys, credentials, or PII in committed code
- SQL queries are parameterized (no string concatenation)
- User input is validated at system boundaries
