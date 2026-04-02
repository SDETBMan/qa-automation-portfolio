variable "environment" {
  type        = string
  description = "Environment tag (ci / staging / prod)."
}

variable "notify_email" {
  type        = string
  description = "DataDog notification handle for monitor alerts (e.g. @your-email@example.com)."
}
