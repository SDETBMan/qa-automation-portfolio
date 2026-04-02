locals {
  github_oidc_url = "https://token.actions.githubusercontent.com"
}

# GitHub Actions OIDC provider — conditionally created so the module is
# idempotent when the provider already exists in the AWS account.
resource "aws_iam_openid_connect_provider" "github_actions" {
  count = var.create_oidc_provider ? 1 : 0

  url = local.github_oidc_url

  client_id_list = ["sts.amazonaws.com"]

  # Current GitHub Actions OIDC thumbprints (both active, as of 2024)
  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd",
  ]

  tags = var.tags
}

data "aws_iam_policy_document" "ci_assume_role" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    principals {
      type = "Federated"
      identifiers = [
        var.create_oidc_provider
        ? aws_iam_openid_connect_provider.github_actions[0].arn
        : "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/token.actions.githubusercontent.com"
      ]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_org}/${var.github_repo}:*"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

data "aws_caller_identity" "current" {}

resource "aws_iam_role" "ci" {
  name               = "github-actions-ci-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.ci_assume_role.json

  tags = merge(var.tags, {
    Name = "github-actions-ci-${var.environment}"
  })
}

data "aws_iam_policy_document" "ci_s3" {
  statement {
    sid    = "ArtifactsBucketObjects"
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:DeleteObject",
    ]
    resources = ["${var.artifacts_bucket_arn}/*"]
  }

  statement {
    sid     = "ArtifactsBucketList"
    effect  = "Allow"
    actions = ["s3:ListBucket"]
    resources = [var.artifacts_bucket_arn]
  }
}

resource "aws_iam_role_policy" "ci_s3" {
  name   = "ci-s3-artifacts-access"
  role   = aws_iam_role.ci.id
  policy = data.aws_iam_policy_document.ci_s3.json
}
