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

### Step 3 — Check for test weakening

Read the diff of your changes and look for these test-weakening patterns:

- **Assertions removed or loosened** — e.g., `assertEquals` changed to `assertNotNull`, expected values broadened, assertion count reduced
- **Tests skipped or deleted** — `@Ignore`, `@Disabled`, `skip()`, `pytest.mark.skip`, `xit(`, `xdescribe(`, tests removed entirely
- **Timeouts increased** — `cy.wait()` durations doubled, `Thread.sleep()` added, `timeout:` values inflated
- **Error handling swallowing failures** — `try/catch` added around assertions, `.should('exist')` replacing `.should('have.text', ...)`, catch blocks that don't rethrow
- **Flaky test accommodations** — retry counts increased without fixing root cause, `@RerunFailures` added

If any weakening is found, flag it explicitly in your response with the file, line, and what was weakened.

### Step 4 — Report results

Summarize:
- Frameworks affected and tests run
- Pass / fail status for each
- Any test-weakening findings (or confirm none found)
- Any frameworks skipped and why

## Reference

For detailed architecture rules and review criteria, read:
```
.claude/skills/verify-changes/reference.md
```
