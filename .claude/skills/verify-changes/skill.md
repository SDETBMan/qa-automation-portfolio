# Verify Changes

After modifying source code, refactoring, or creating new tests, verify that your changes work correctly and haven't weakened the test suite.

## When to use

Trigger this skill automatically whenever you:
- Modify test files, page objects, utilities, or configuration
- Add new test files or test frameworks
- Refactor existing code (rename, extract, restructure)
- Change CI workflow definitions

## Procedure

### Step 1 — Detect affected frameworks

Run the detection script to identify which frameworks were touched:

```bash
bash .claude/skills/verify-changes/scripts/check.sh --detect
```

This uses `git diff --name-only` against HEAD to find changed top-level directories and maps them to known frameworks.

### Step 2 — Run tests for each affected framework

For each detected framework, run its test suite:

```bash
bash .claude/skills/verify-changes/scripts/check.sh --run <framework-name>
```

If the test command requires external services, API keys, or infrastructure that isn't available locally, skip it and note the skip reason.

### Step 3 — Validate locators

If any page object files were changed (files under `pages/` directories in browser frameworks), validate that selectors match real elements on SauceDemo:

```bash
cd playwright/tests/playwright-ts && npm ci --quiet && npx playwright install chromium 2>/dev/null
cd "$REPO_ROOT"  # return to repo root
node .claude/skills/verify-changes/scripts/validate-locators.mjs
```

The script extracts CSS selectors from changed page objects across all 5 browser frameworks, navigates to the corresponding SauceDemo pages, and checks that each selector matches at least one element. Conditional elements (error messages, cart badges) are reported but not marked as failures.

If no page objects were changed, the script exits early. If saucedemo.com is unreachable, the script skips validation without failing.

### Step 4 — Check for zero-assertion tests

If any test files were changed, scan them for test functions with zero assertions:

```bash
bash .claude/skills/verify-changes/scripts/check-assertions.sh
```

The script detects test bodies across all browser frameworks and Python pytest that contain no assertion calls (`.should(`, `expect(`, `Assert.`, `assert`). Only flags tests with **zero** assertions — single-assertion tests are fine.

For Cucumber/Behave, only `@Then` / `@then` steps are checked (action steps like `@When` / `@Given` are not expected to assert).

**Known limitation:** Tests that delegate assertions to page object methods (e.g., `loginPage.isLoginButtonVisible()` which internally calls `.should('exist')`) appear assertion-free at the test level. The reviewer decides if the delegation is intentional.

### Step 5 — Check for test weakening

Read the diff of your changes and look for these test-weakening patterns:

- **Assertions removed or loosened** — e.g., `assertEquals` changed to `assertNotNull`, expected values broadened, assertion count reduced
- **Tests skipped or deleted** — `@Ignore`, `@Disabled`, `skip()`, `pytest.mark.skip`, `xit(`, `xdescribe(`, tests removed entirely
- **Timeouts increased** — `cy.wait()` durations doubled, `Thread.sleep()` added, `timeout:` values inflated
- **Error handling swallowing failures** — `try/catch` added around assertions, `.should('exist')` replacing `.should('have.text', ...)`, catch blocks that don't rethrow
- **Flaky test accommodations** — retry counts increased without fixing root cause, `@RerunFailures` added

If any weakening is found, flag it explicitly in your response with the file, line, and what was weakened.

### Step 6 — Report results

Summarize:
- Frameworks affected and tests run
- Pass / fail status for each
- Locator validation results (pass / fail / conditional / skip counts, or "no page objects changed")
- Zero-assertion test findings (count and locations, or "all tests have assertions")
- Any test-weakening findings (or confirm none found)
- Any frameworks skipped and why

## Reference

For detailed architecture rules and review criteria, read:
```
.claude/skills/verify-changes/reference.md
```
