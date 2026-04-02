variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region in which to provision resources."
}

variable "environment" {
  type        = string
  default     = "ci"
  description = "Environment tag applied to all resources (ci / staging / prod)."
}

variable "artifacts_bucket_name" {
  type        = string
  description = "Globally unique S3 bucket name for test artifacts (Allure, JUnit XML, screenshots)."
}

variable "github_org" {
  type        = string
  default     = "SDETBMan"
  description = "GitHub organisation or user that owns the repository."
}

variable "github_repo" {
  type        = string
  default     = "qa-automation-portfolio"
  description = "GitHub repository name (without the org prefix)."
}

variable "create_oidc_provider" {
  type        = bool
  default     = true
  description = "Set to false if a GitHub Actions OIDC provider already exists in the AWS account."
}

variable "dd_api_key" {
  type        = string
  sensitive   = true
  description = "DataDog API key.  Pass via TF_VAR_dd_api_key or a .tfvars file."
}

variable "dd_app_key" {
  type        = string
  sensitive   = true
  description = "DataDog Application key.  Pass via TF_VAR_dd_app_key or a .tfvars file."
}

variable "dd_site" {
  type        = string
  default     = "datadoghq.com"
  description = "DataDog intake site (e.g. datadoghq.com, datadoghq.eu, us3.datadoghq.com)."
}

variable "dd_notify_email" {
  type        = string
  description = "Email address that DataDog monitors will alert (e.g. @example.com handle)."
}
