output "artifacts_bucket_name" {
  description = "Name of the S3 bucket used to store test artifacts."
  value       = module.s3_artifacts.bucket_name
}

output "artifacts_bucket_arn" {
  description = "ARN of the S3 artifacts bucket."
  value       = module.s3_artifacts.bucket_arn
}

output "ci_role_arn" {
  description = "ARN of the IAM role assumed by GitHub Actions via OIDC.  Paste this into the AWS_ROLE_ARN repository secret."
  value       = module.iam_ci.role_arn
}
