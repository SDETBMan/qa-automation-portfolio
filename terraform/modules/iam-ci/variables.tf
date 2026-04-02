variable "github_org" {
  type        = string
  description = "GitHub organisation or user that owns the repository."
}

variable "github_repo" {
  type        = string
  description = "GitHub repository name (without the org prefix)."
}

variable "artifacts_bucket_arn" {
  type        = string
  description = "ARN of the S3 artifacts bucket the CI role is permitted to access."
}

variable "environment" {
  type        = string
  description = "Environment tag (ci / staging / prod)."
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Additional tags to merge onto all resources."
}

variable "create_oidc_provider" {
  type        = bool
  default     = true
  description = "Set to false if a GitHub Actions OIDC provider already exists in the AWS account."
}
