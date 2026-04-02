# Default: local backend (safe for portfolio demo — no AWS account required)
terraform {}

# Production: uncomment after bootstrapping the state bucket
# terraform {
#   backend "s3" {
#     bucket         = "your-tf-state-bucket"
#     key            = "qa-portfolio/terraform.tfstate"
#     region         = "us-east-1"
#     dynamodb_table = "terraform-state-lock"
#     encrypt        = true
#   }
# }
