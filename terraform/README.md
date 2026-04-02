# Terraform — QA Automation Portfolio Infrastructure

Provisions the cloud infrastructure that supports the `qa-automation-portfolio` monorepo:

| Module | What it creates |
|---|---|
| `s3-artifacts` | S3 bucket for permanent test artifact storage (Allure reports, JUnit XML, screenshots) with versioning, AES-256 encryption, public-access block, and lifecycle rules |
| `iam-ci` | Keyless GitHub Actions → AWS IAM role via OIDC (no long-lived AWS keys in CI) |
| `datadog-observability` | DataDog dashboard (sourced from `job-agent/`), two monitors, and a CI pass-rate SLO |

---

## Prerequisites

| Tool | Version |
|---|---|
| [Terraform](https://developer.hashicorp.com/terraform/downloads) | >= 1.6 |
| AWS credentials | Any method recognised by the AWS provider (env vars, `~/.aws/credentials`, IAM role) |
| DataDog API + App keys | [Organisation Settings → API Keys](https://app.datadoghq.com/organization-settings/api-keys) |

---

## Quick Start

```bash
# 1. Copy the example vars file and fill in your values
cp terraform.tfvars.example terraform.tfvars

# 2. Initialise providers
make terraform-init          # or: cd terraform && terraform init

# 3. Preview the plan
make terraform-plan

# 4. Apply (requires real AWS + DataDog credentials)
make terraform-apply
```

---

## Backend

The default backend is **local** — safe for portfolio demos with no AWS account.

To use a remote S3 backend in production:
1. Bootstrap a state bucket manually (or with a separate Terraform root).
2. Uncomment the `backend "s3"` block in `backend.tf`.
3. Re-run `terraform init -migrate-state`.

---

## Variables

See [`variables.tf`](./variables.tf) for the full list.  The required variables are:

| Variable | How to set |
|---|---|
| `artifacts_bucket_name` | `terraform.tfvars` or `TF_VAR_artifacts_bucket_name` |
| `dd_api_key` | `TF_VAR_dd_api_key` (sensitive — never commit) |
| `dd_app_key` | `TF_VAR_dd_app_key` (sensitive — never commit) |
| `dd_notify_email` | `terraform.tfvars` or `TF_VAR_dd_notify_email` |

---

## GitHub Actions Integration

The [`.github/workflows/terraform.yml`](../.github/workflows/terraform.yml) workflow:

- Runs **plan** on every pull request that touches `terraform/**`, posting the output as a PR comment
- Runs **apply** automatically on merges to `main`
- Authenticates to AWS via OIDC using the role created by `module.iam_ci` — **no long-lived AWS secrets**

### Required repository secrets / variables

| Secret / Variable | Value |
|---|---|
| `AWS_ROLE_ARN` *(secret)* | Output of `terraform output ci_role_arn` — bootstrap once manually |
| `DD_API_KEY` *(secret)* | DataDog API key |
| `DD_APP_KEY` *(secret)* | DataDog Application key |
| `TF_VAR_dd_notify_email` *(secret)* | Notification email handle |
| `TF_VAR_artifacts_bucket_name` *(secret)* | S3 bucket name |
| `AWS_REGION` *(variable, optional)* | Defaults to `us-east-1` |

> **Bootstrap note:** There is an intentional chicken-and-egg for the first deploy.
> Run `terraform apply` locally once with AWS credentials to create the IAM role,
> then add the output ARN as the `AWS_ROLE_ARN` secret to enable keyless CI runs.

---

## Make Targets

```
make terraform-init      # terraform init
make terraform-validate  # terraform validate
make terraform-fmt       # terraform fmt -recursive
make terraform-plan      # terraform plan
make terraform-apply     # terraform apply
make terraform-destroy   # terraform destroy
make terraform-clean     # remove .terraform/ and state files
```

---

## Module Structure

```
terraform/
├── versions.tf                     # required_providers block
├── backend.tf                      # local (default) + S3 (commented out)
├── main.tf                         # providers, locals, module calls
├── variables.tf                    # all root variable declarations
├── outputs.tf                      # bucket_name, bucket_arn, ci_role_arn
├── terraform.tfvars.example        # safe example values (committed)
├── .gitignore
└── modules/
    ├── s3-artifacts/               # S3 bucket with versioning, SSE, lifecycle
    ├── iam-ci/                     # GitHub OIDC + IAM role + S3 policy
    └── datadog-observability/      # dashboard, monitors, SLO
```
