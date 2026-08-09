# Quality Manual — ISO 9001:2015 Clause-Aligned

This document maps the quality management practices in the qa-automation-portfolio to ISO 9001:2015 clause structure. It supplements the [QA Operating Model](QA-OPERATING-MODEL.md) with formal clause references for audit preparation and compliance evidence collection.

Where applicable, ISO/IEC 17025:2017 (Testing and Calibration Laboratories) and SOC 2 Trust Services Criteria cross-references are included.

---

## 4 — Context of the Organization

### 4.1 Understanding the Organization and Its Context

The QA function operates within SaaS product development. External factors include evolving browser platforms, third-party API changes, and regulatory requirements (HIPAA for healthcare, SOC 2 for SaaS, ISO/IEC 17025 for calibration/metrology). Internal factors include CI/CD maturity, team size, and technology stack diversity.

### 4.4 Quality Management System and Its Processes

| Process | Input | Output | Tool |
|---------|-------|--------|------|
| Test execution | Code changes | Pass/fail results (JUnit XML, TRX) | Playwright, Cypress, Selenium, pytest |
| Risk identification | Codebase, dependencies | Vulnerability reports | OWASP ZAP, Dependabot, CodeQL |
| Change monitoring | Target application DOM | Drift reports | site-monitor |
| Evidence collection | CI artifacts | Compliance evidence map | qms-evidence-collector |
| Quality KPI reporting | Test results across frameworks | Aggregated metrics | quality-dashboard |
| Failure analysis | Test failures | Root cause clusters | failure-triage |

**ISO/IEC 17025 cross-reference:** Clause 4.1.1 — The laboratory shall carry out activities impartially and in a structurally consistent manner.

---

## 5 — Leadership

### 5.1 Leadership and Commitment

Quality objectives are embedded in CI pipeline gates. No code merges to main without passing smoke tests. No release proceeds without regression suite completion. These gates enforce quality commitment as a structural property of the system, not a policy declaration.

### 5.3 Organizational Roles, Responsibilities and Authorities

| Role | Responsibilities | Documented In |
|------|-----------------|---------------|
| QA Lead | Regression planning, defect triage, release sign-off | QA-OPERATING-MODEL.md §4 |
| SDET | Framework development, test automation, CI pipeline maintenance | Framework READMEs |
| Engineering | Unit tests, integration tests, defect remediation | QA-OPERATING-MODEL.md §3 |
| Product Owner | Acceptance criteria, S3/S4 defect disposition | QA-OPERATING-MODEL.md §2 |

---

## 6 — Planning

### 6.1 Actions to Address Risks and Opportunities

| Risk | Detection Mechanism | Response |
|------|---------------------|----------|
| Security vulnerabilities in dependencies | Dependabot, CodeQL (weekly) | Auto-PR for patch, vulnerability-aggregator report |
| OWASP Top 10 vulnerabilities | ZAP passive scan (every CI run) | Report uploaded as artifact, triage on critical findings |
| Upstream DOM changes breaking tests | site-monitor (daily 06:00 UTC) | Auto GitHub issue, baseline update, affected test update |
| Test reliability degradation | flakiness-detector (every CI run) | Quarantine at score >= 0.5, investigate at 0.2-0.49 |
| API contract drift | Pact consumer-driven tests (every push/PR) | Consumer contract failure blocks merge |

**SOC 2 cross-reference:** CC3.1 — The entity identifies and assesses risks to the achievement of its objectives.

### 6.2 Quality Objectives and Planning to Achieve Them

| Objective | Target | Measurement | Frequency |
|-----------|--------|-------------|-----------|
| Test suite pass rate | > 95% | quality-dashboard `kpi.pass_rate` | Every CI run |
| Flakiness rate | < 5% quarantined | flakiness-detector `flakiness.total_flaky` | Every CI run |
| Mean Time to Detect (MTTD) | < 300s | quality-dashboard `kpi.mttd_seconds` | Every CI run |
| Security scan coverage | Zero critical open alerts | vulnerability-aggregator | Weekly |
| Regression coverage | 90%+ automated | QA-OPERATING-MODEL.md §3 | Sprint review |

---

## 7 — Support

### 7.1.5 Monitoring and Measuring Resources

Test frameworks are the measurement instruments of software quality. Their reliability must be assured.

| Measurement Resource | Validation Method | Frequency |
|---------------------|-------------------|-----------|
| Browser automation (Playwright, Cypress, Selenium) | Cross-browser execution on Tier 1 platforms | Every CI run |
| API contract tests (Pact, Postman/Newman) | Consumer-provider contract verification | Every push/PR |
| Load test baselines (k6) | SLO threshold validation | Nightly |
| LLM evaluation metrics (DeepEval) | 10-metric evaluation across golden dataset | Nightly |
| Security scanners (ZAP, CodeQL) | Known-vulnerability detection against OWASP benchmarks | Weekly |

**ISO/IEC 17025 cross-reference:** Clause 6.4 — Equipment used for testing shall be calibrated or checked to establish that it fulfills specified requirements.

### 7.1.5.2 Measurement Traceability

Flakiness scoring (`flakiness_score = min(passes, failures) / total_non_skipped`) identifies unreliable measurement instruments (tests). Quarantined tests are removed from release decisions until their reliability is restored. This ensures that quality decisions are based on traceable, reproducible measurements.

**ISO/IEC 17025 cross-reference:** Clause 7.7 — Ensuring the validity of results through intermediate checks.

### 7.5 Documented Information

| Document Type | Location | Retention |
|---------------|----------|-----------|
| Test execution results (JUnit XML, TRX) | CI artifacts | 30 days |
| Allure reports | GitHub Pages + CI artifacts | 30 days |
| Visual regression diffs | CI artifacts | 30 days |
| Flakiness reports | CI artifacts | 90 days |
| Security scan reports | CI artifacts | 30 days |
| Drift detection baselines | Version-controlled (`baseline.json`) | Permanent (git history) |
| Quality KPI dashboards | DataDog | Per DataDog retention policy |
| Compliance evidence maps | qms-evidence-collector output | 30 days (CI) + on-demand regeneration |

**SOC 2 cross-reference:** CC4.1 — The entity selects, develops, and performs ongoing evaluations to ascertain whether controls are present and functioning.

---

## 8 — Operation

### 8.2 Requirements for Products and Services

Requirements are documented as:
- Gherkin feature files (Cucumber, Behave) — business-readable acceptance criteria
- Test case management entries (Testiny) — traceable to feature requirements
- Pact consumer contracts — formal inter-service interface requirements
- k6 SLO definitions (`slo.json`) — quantitative performance requirements

### 8.4 Control of Externally Provided Processes, Products and Services

| External Provider | Control Mechanism | Monitoring |
|-------------------|-------------------|------------|
| Third-party npm/pip packages | Dependabot weekly scans | Auto-PR on vulnerability |
| Target application (SauceDemo) | site-monitor DOM drift detection | Daily scan, auto-issue on critical drift |
| Cloud test infrastructure (BrowserStack, Sauce Labs) | Configuration-as-code (`.sauce/config.yml`, `browserstack.json`) | CI execution logs |
| LLM APIs (OpenAI, Anthropic, Vertex AI) | Rate limit handling, retry logic, cost tracking | Langfuse tracing, DataDog latency metrics |

### 8.5.1 Control of Production and Service Provision

Controlled conditions for test execution:

| Condition | Implementation |
|-----------|---------------|
| Defined procedures | Page Object Model, consistent fixture patterns across all frameworks |
| Qualified personnel | SDET role with framework ownership |
| Monitoring | DataDog CI Visibility, custom GAUGE metrics, Allure trends |
| Controlled environment | Docker Compose, Kubernetes manifests, reproducible CI runners |
| Traceability | JUnit XML → DataDog CI Visibility → Testiny test management |

### 8.5.6 Control of Changes

| Change Type | Detection | Response |
|-------------|-----------|----------|
| Upstream DOM changes | site-monitor drift detection | Baseline update + affected test update |
| API contract changes | Pact verification failure | Consumer/provider contract renegotiation |
| Dependency vulnerabilities | Dependabot/CodeQL alerts | Version bump or mitigation |
| Test reliability changes | Flakiness score trending | Quarantine or root cause fix |

### 8.6 Release of Products and Services

Release readiness is verified through the checklist in [QA-OPERATING-MODEL.md §5](QA-OPERATING-MODEL.md#5-release-readiness-checklist). Evidence of conformity is retained as:
- JUnit/TRX XML results (30-day retention)
- Allure reports (GitHub Pages deployment)
- Visual regression baselines (version-controlled)
- k6 SLO pass/fail reports

---

## 9 — Performance Evaluation

### 9.1.1 Monitoring, Measurement, Analysis and Evaluation

All test suites report to DataDog via two mechanisms:
1. **CI Visibility:** `datadog-ci junit upload` for pass/fail/duration trend analysis
2. **Custom GAUGE metrics:** Framework-specific KPIs sent to DataDog v2 API

The quality-dashboard aggregates across all frameworks to compute:
- Pass Rate, Failure Density, Suite Stability
- Mean Time to Detect (MTTD)
- Flakiness Rate (from flakiness-detector)
- p95 Duration (performance regression detection)

### 9.1.3 Analysis and Evaluation

| Analysis | Data Source | Output |
|----------|------------|--------|
| Test trend analysis | DataDog CI Visibility | Pass/fail/duration time series |
| Flakiness trends | flakiness-detector 90-day history | Quarantine recommendations |
| Security posture | vulnerability-aggregator | Severity-prioritized report |
| Failure patterns | failure-triage AI clustering | Root cause categories + fix actions |
| Compliance coverage | qms-evidence-collector | Clause-level evidence map + gap analysis |

**SOC 2 cross-reference:** CC7.1 — The entity uses detection and monitoring procedures to identify anomalies.

---

## 10 — Improvement

### 10.2 Nonconformity and Corrective Action

| Nonconformity Type | Detection | Corrective Action |
|--------------------|-----------|-------------------|
| Test failure | JUnit XML / CI pipeline | Defect triage per SLA (QA-OPERATING-MODEL.md §2) |
| Flaky test | flakiness-detector score >= 0.20 | Root cause investigation within sprint |
| Security vulnerability | ZAP / Dependabot / CodeQL alert | Patch or mitigation per severity |
| Measurement unreliability | Flakiness score >= 0.50 | Quarantine + defect filed + 2-sprint fix deadline |
| Upstream change | site-monitor drift | Selector update + regression verification |

The failure-triage framework provides AI-powered root cause clustering, categorizing failures into: `assertion_error`, `element_not_found`, `timeout`, `setup_failure`, `api_error`, `data_error`, `unknown`. This structured analysis feeds corrective action planning.

### 10.3 Continual Improvement

Improvement inputs:
- Quality KPI trends (quality-dashboard)
- Flakiness score trends (flakiness-detector)
- Failure pattern analysis (failure-triage)
- Security scan trends (vulnerability-aggregator)
- Compliance gap analysis (qms-evidence-collector)
- Site drift frequency (site-monitor)

Improvement mechanisms:
- Sprint retrospective review of flaky test backlog
- Quarterly test case inventory audit (QA-OPERATING-MODEL.md §6)
- Quarterly browser/device tier reassessment (QA-OPERATING-MODEL.md §1)

---

## ISO/IEC 17025:2017 — Supplemental References

For roles involving calibration, metrology, or laboratory quality management (e.g., calibration software QA), the following additional clauses are relevant:

| ISO/IEC 17025 Clause | Title | Portfolio Evidence |
|----------------------|-------|-------------------|
| 6.4 | Equipment | Test framework versioning (Playwright 1.44, Selenium 4, etc.) pinned in CI |
| 7.2.2 | Validation of methods | Coverage reports validating test scope; k6 load test validation |
| 7.7.1 | Ensuring validity of results | Repeated standardized test execution (JUnit XML evidence) |
| 7.7.2 | Intermediate checks | Flakiness detection as measurement system health check |
| 7.11 | Control of data and information management | Allure reports, version-controlled baselines, structured CI artifacts |

---

## SOC 2 — Trust Services Criteria Cross-Reference

| SOC 2 Control | Title | Portfolio Evidence |
|---------------|-------|-------------------|
| CC3.1 | Risk assessment | vulnerability-aggregator, Dependabot, CodeQL |
| CC4.1 | Monitoring activities | quality-dashboard, DataDog CI Visibility, flakiness-detector |
| CC6.1 | Logical access security | OWASP ZAP scans, 4 security test cases per browser framework |
| CC7.1 | System monitoring | DataDog custom metrics, site-monitor drift detection |
| CC7.2 | Incident management | failure-triage AI clustering, defect severity SLAs |
| CC8.1 | Change management | PR smoke gates, regression suite, Pact contract verification |

---

*This document is maintained alongside the [QA Operating Model](QA-OPERATING-MODEL.md). The qms-evidence-collector framework automates evidence collection against these clause references.*
