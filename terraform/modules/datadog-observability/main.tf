# ── Dashboard ─────────────────────────────────────────────────────────────────
# Embeds the existing job-agent dashboard JSON verbatim.
# The JSON file in job-agent/ is the single source of truth.
resource "datadog_dashboard_json" "job_agent" {
  dashboard = file("${path.module}/../../../job-agent/datadog-dashboard.json")
}

# ── Monitor: no job-agent run in 24 hours ─────────────────────────────────────
resource "datadog_monitor" "job_agent_no_run" {
  name    = "[${var.environment}] Job Agent — No Successful Run in 24 Hours"
  type    = "metric alert"
  message = <<-EOT
    The job-agent has not produced any results in the last 24 hours.
    Check the GitHub Actions job-agent workflow for failures.
    Notify: ${var.notify_email}
  EOT

  query = "sum(last_1d):sum:llm.job_agent.jobs_found{framework:job-agent}.as_count() < 1"

  monitor_thresholds {
    critical = 1
  }

  notify_no_data    = true
  no_data_timeframe = 25 # 25 h — accommodates nightly run timing variance

  tags = [
    "env:${var.environment}",
    "service:job-agent",
    "managed-by:terraform",
  ]
}

# ── Monitor: CI pass rate below 80% ───────────────────────────────────────────
resource "datadog_monitor" "ci_pass_rate_low" {
  name    = "[${var.environment}] QA Portfolio — CI Pass Rate Below 80%"
  type    = "metric alert"
  message = <<-EOT
    The CI test pass rate for qa-automation-portfolio has dropped below 80% in the last hour.
    Review recent workflow runs for failures.
    Notify: ${var.notify_email}
  EOT

  query = "avg(last_1h):(sum:test.suite.passed{service:qa-automation-portfolio}.as_count() / (sum:test.suite.passed{service:qa-automation-portfolio}.as_count() + sum:test.suite.failed{service:qa-automation-portfolio}.as_count())) * 100 < 80"

  monitor_thresholds {
    critical = 80
  }

  notify_no_data    = false

  tags = [
    "env:${var.environment}",
    "service:qa-automation-portfolio",
    "managed-by:terraform",
  ]
}

# ── SLO: CI pass rate ─────────────────────────────────────────────────────────
resource "datadog_service_level_objective" "ci_pass_rate" {
  name        = "QA Portfolio — CI Test Pass Rate"
  type        = "metric"
  description = "Tracks the ratio of passing to total CI test runs for qa-automation-portfolio."

  query {
    numerator   = "sum:test.suite.passed{service:qa-automation-portfolio}.as_count()"
    denominator = "sum:test.suite.passed{service:qa-automation-portfolio}.as_count() + sum:test.suite.failed{service:qa-automation-portfolio}.as_count()"
  }

  thresholds {
    timeframe = "30d"
    target    = 90
    warning   = 95
  }

  thresholds {
    timeframe = "7d"
    target    = 85
    warning   = 90
  }

  tags = [
    "env:${var.environment}",
    "service:qa-automation-portfolio",
    "managed-by:terraform",
  ]
}
