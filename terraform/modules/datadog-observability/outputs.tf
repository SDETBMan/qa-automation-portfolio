output "dashboard_url" {
  description = "URL of the DataDog dashboard for the job-agent."
  value       = "https://app.datadoghq.com/dashboard/${datadog_dashboard_json.job_agent.id}"
}

output "job_agent_monitor_id" {
  description = "ID of the DataDog monitor that alerts when the job-agent has no run in 24 hours."
  value       = datadog_monitor.job_agent_no_run.id
}

output "slo_id" {
  description = "ID of the CI pass-rate Service Level Objective."
  value       = datadog_service_level_objective.ci_pass_rate.id
}
