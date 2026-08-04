# QA Operating Model

This document defines the quality assurance standards, processes, and coverage strategy for the qa-automation-portfolio. It serves as the single source of truth for regression planning, release readiness, defect triage, and device/browser coverage.

---

## 1. Supported Browser, Device, and OS Coverage

### Tier 1 -- Must Pass (blocks release)

| Platform | Browser / Device | Resolution | Framework |
|----------|-----------------|------------|-----------|
| Desktop Windows 11 | Chrome (latest) | 1920x1080 | Playwright, Cypress, Selenium |
| Desktop macOS 14+ | Safari (latest) | 1440x900 | Playwright (WebKit) |
| Desktop Windows/macOS | Firefox (latest) | 1920x1080 | Playwright, Selenium |
| Android 13+ | Chrome Mobile | 360x800 | Appium (Selenium Grid / BrowserStack) |
| iOS 17+ | Safari Mobile | 390x844 | Appium (BrowserStack) |

### Tier 2 -- Should Pass (does not block, tracked as known issues)

| Platform | Browser / Device | Framework |
|----------|-----------------|-----------|
| Desktop Windows | Edge (latest) | Selenium |
| Desktop Linux (CI) | Chromium headless | Playwright, Cypress |
| Android 12 | Chrome Mobile | Appium |
| iOS 16 | Safari Mobile | Appium |

### Tier 3 -- Best Effort (tested on demand, not gated)

| Platform | Browser / Device |
|----------|-----------------|
| Desktop | Chrome (N-1), Firefox (N-1) |
| Tablet | iPad Safari, Android Chrome |
| Desktop | Opera, Brave |

**Update cadence:** Review tier assignments quarterly or when analytics show a platform crossing the 5% traffic threshold.

---

## 2. Defect Severity Definitions and Triage SLAs

| Severity | Definition | Examples | Triage SLA | Fix SLA |
|----------|-----------|----------|------------|---------|
| **S1 -- Critical** | Application is unusable or data loss occurs. No workaround. | Login broken, checkout fails, data corruption, security vulnerability | Triage within 2 hours | Hotfix within 24 hours |
| **S2 -- Major** | Core functionality impaired. Workaround exists but is unacceptable for production. | Cart calculation wrong, payment flow error, broken navigation on Tier 1 browser | Triage within 4 hours | Fix in current sprint |
| **S3 -- Minor** | Non-core functionality affected. Workaround is acceptable. | UI misalignment on one browser, tooltip not displaying, non-blocking validation gap | Triage within 1 business day | Fix in next sprint |
| **S4 -- Cosmetic** | Visual or UX polish. No functional impact. | Font inconsistency, alignment off by pixels, copy/grammar issue | Triage within 2 business days | Backlog (prioritize with product) |

### Triage Process

1. **Reporter** files defect in Jira with: severity, steps to reproduce, expected vs actual, environment, screenshots/video.
2. **QA Lead** triages within the SLA window: validates severity, assigns component label, links to related tests.
3. **Engineering** acknowledges and estimates within 1 business day of triage.
4. **QA** verifies the fix on the branch, then regression tests post-merge.
5. **Closure:** QA closes the defect after verification passes on staging.

---

## 3. Test Coverage Strategy

### Coverage Tiers

| Tier | Description | Automation Target | Trigger |
|------|-------------|-------------------|---------|
| **Smoke** | Login, navigation, core page loads, health checks | 100% automated | Every PR, every deploy |
| **Regression** | Full user flows (checkout, account, content rendering, search) | 90%+ automated | Nightly schedule, pre-release |
| **Exploratory** | Edge cases, new features, cross-browser visual | Manual | Sprint-scoped sessions per feature |
| **Performance** | Page load budgets, API response times, CLS/LCP | Automated (Lighthouse, k6) | Weekly and pre-release |
| **Accessibility** | WCAG 2.1 AA compliance | Automated (axe-core) + manual audit | Every PR (automated), quarterly (manual audit) |
| **Security** | OWASP baseline, dependency vulnerabilities | Automated (ZAP passive, CodeQL, Dependabot) | Every PR (passive), weekly (full scan) |

### Automation Ownership

| Layer | Owner | Tool |
|-------|-------|------|
| Unit tests | Engineering | Jest / pytest |
| Integration / API | Engineering + QA | Playwright API, Postman/Newman, Pact |
| E2E browser | QA | Playwright (primary), Cypress |
| Visual regression | QA | Playwright `toHaveScreenshot()` |
| Mobile | QA | Appium via BrowserStack / Sauce Labs |
| Performance | QA + Engineering | k6, Lighthouse CI |

---

## 4. Regression Planning and Execution

### Entry Criteria (start regression)

- [ ] Feature branch merged to staging/release branch
- [ ] All unit and integration tests passing in CI
- [ ] Smoke suite green on staging environment
- [ ] Test case management tool (Testiny) updated with new/modified test cases
- [ ] Known defects documented with severity and workarounds

### Regression Scope

| Release Type | Scope | Estimated Duration |
|-------------|-------|-------------------|
| **Hotfix** | Smoke suite + targeted tests for the fix area | Automated only |
| **Minor release** | Full regression suite (automated) + exploratory testing on changed areas | Automated + 1 exploratory session |
| **Major release** | Full regression + cross-browser Tier 1 + mobile Tier 1 + performance + accessibility + exploratory | Full cycle |

### Exit Criteria (approve release)

- [ ] All Tier 1 browser/device combinations pass
- [ ] Zero open S1 or S2 defects
- [ ] All S3 defects reviewed and accepted by product owner
- [ ] Flakiness score below quarantine threshold (0.5) for all included tests
- [ ] Performance budgets met (LCP < 2.5s, CLS < 0.1, API p95 < 200ms)
- [ ] Accessibility scan shows zero critical violations
- [ ] Release notes reviewed and smoke-verified on staging

---

## 5. Release Readiness Checklist

### Pre-Release

- [ ] Regression suite executed and results reviewed
- [ ] Flakiness report generated -- no new flaky tests introduced
- [ ] Site drift monitor confirms no selector changes since last baseline
- [ ] Visual regression baselines reviewed (no unintended diffs)
- [ ] Manual exploratory testing completed for new features
- [ ] Defect triage complete -- all S1/S2 resolved or explicitly deferred with product sign-off
- [ ] Test results synced to Testiny with run documentation
- [ ] DataDog dashboards reviewed -- no anomalies in pass rate or duration trends

### Deploy

- [ ] Smoke suite passes on production post-deploy
- [ ] Health check endpoints return 200
- [ ] Monitoring alerts configured for the release window
- [ ] Rollback plan documented and validated

### Post-Release

- [ ] Production smoke verified within 30 minutes of deploy
- [ ] Monitor error rates and performance metrics for 24 hours
- [ ] Close release ticket and update test documentation

---

## 6. Test Case Management Standards (Testiny)

### Organization

| Level | Convention | Example |
|-------|-----------|---------|
| **Project** | One per application | `Web Platform`, `Drops Mobile App` |
| **Folder** | By feature area | `Authentication`, `Checkout`, `Content Rendering` |
| **Test case** | Imperative title, preconditions, steps, expected results | "Verify user can complete checkout with valid credit card" |

### Tagging

| Tag | Purpose |
|-----|---------|
| `@smoke` | Included in PR gate and deploy verification |
| `@regression` | Included in full regression suite |
| `@manual` | Requires manual execution (not automated) |
| `@automated` | Has a corresponding automated test (link in description) |
| `@accessibility` | WCAG compliance validation |
| `@mobile` | Mobile-specific test case |

### Maintenance Cadence

- **Sprint boundary:** Review and update test cases for features delivered in the sprint.
- **Quarterly:** Audit full test case inventory. Archive obsolete cases. Verify `@automated` links are current.
- **On selector drift:** When site-monitor detects removed selectors, update affected test cases immediately.

---

## 7. Flaky Test Policy

### Detection

The flakiness-detector runs on every CI pipeline and computes:

```
flakiness_score = min(passes, failures) / total_non_skipped
```

### Classification and Response

| Score Range | Classification | Action |
|-------------|---------------|--------|
| 0.0 | Stable | No action |
| 0.01 -- 0.19 | Low flakiness | Monitor -- add to watchlist |
| 0.20 -- 0.49 | Moderate flakiness | Investigate root cause within current sprint |
| 0.50+ | High flakiness | Quarantine -- remove from PR gate, file defect, fix within 2 sprints |

### Prevention

- Use `storageState` authentication instead of per-test UI login
- Use `data-test` / `data-testid` attributes instead of CSS class selectors
- Use `getByRole()` and semantic locators over fragile CSS paths
- Run site-monitor to detect upstream selector changes before they cause flake
- Set explicit timeouts (`actionTimeout`, `navigationTimeout`) rather than relying on defaults

---

## 8. CI/CD Integration

### Pipeline Architecture

| Stage | Trigger | Suite | Gate |
|-------|---------|-------|------|
| **PR gate** | Pull request opened/updated | Smoke (Chromium only, 5-min timeout) | Blocks merge |
| **Post-merge** | Push to main | Full regression (cross-browser) | Non-blocking (alerts on failure) |
| **Nightly** | Scheduled (staggered UTC) | Full regression + performance + security scan | Non-blocking (alerts on failure) |
| **Pre-release** | Manual dispatch | Full regression + mobile + visual + exploratory | Blocks release |
| **Post-deploy** | Deploy webhook | Smoke + health checks | Auto-rollback on failure |

### Artifact Retention

| Artifact | Retention | Purpose |
|----------|-----------|---------|
| JUnit/TRX XML | 30 days | Audit trail, DataDog CI Visibility, Testiny sync |
| Playwright traces | 30 days | Failure debugging |
| Visual regression diffs | 30 days | UI change audit |
| Allure reports | 30 days | Stakeholder reporting |
| Flakiness reports | 90 days | Trend analysis |

### Observability

All test suites report to DataDog:
- **CI Visibility:** JUnit XML upload for pass/fail/duration trends
- **Custom GAUGE metrics:** `test.suite.passed`, `test.suite.failed`, `test.suite.skipped`, `test.suite.duration_ms`
- **Quality KPIs:** Pass Rate, Failure Density, Suite Stability, Flakiness Rate, MTTD
- **Cache metrics:** `cache.hits`, `cache.misses` (FastAPI service)
- **Drift metrics:** `site_monitor.drift_detected`, `site_monitor.selectors_removed`
