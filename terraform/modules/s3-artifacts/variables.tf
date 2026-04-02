variable "bucket_name" {
  type        = string
  description = "Globally unique name for the S3 artifacts bucket."
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
