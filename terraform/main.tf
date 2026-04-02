provider "aws" {
  region = var.aws_region
}

provider "datadog" {
  api_key = var.dd_api_key
  app_key = var.dd_app_key
  api_url = "https://api.${var.dd_site}/"
}

locals {
  common_tags = {
    Project     = "qa-automation-portfolio"
    Environment = var.environment
    ManagedBy   = "terraform"
    Owner       = var.github_org
  }
}

module "s3_artifacts" {
  source = "./modules/s3-artifacts"

  bucket_name = var.artifacts_bucket_name
  environment = var.environment
  tags        = local.common_tags
}

module "iam_ci" {
  source = "./modules/iam-ci"

  github_org            = var.github_org
  github_repo           = var.github_repo
  artifacts_bucket_arn  = module.s3_artifacts.bucket_arn
  environment           = var.environment
  tags                  = local.common_tags
  create_oidc_provider  = var.create_oidc_provider
}

module "datadog_observability" {
  source = "./modules/datadog-observability"

  environment  = var.environment
  notify_email = var.dd_notify_email
}
