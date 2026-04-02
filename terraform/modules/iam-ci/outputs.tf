output "role_arn" {
  description = "ARN of the IAM role assumed by GitHub Actions via OIDC."
  value       = aws_iam_role.ci.arn
}

output "role_name" {
  description = "Name of the IAM role assumed by GitHub Actions via OIDC."
  value       = aws_iam_role.ci.name
}
