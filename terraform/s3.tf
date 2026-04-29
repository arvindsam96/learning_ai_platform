# S3 Bucket for file storage
resource "aws_s3_bucket" "app_storage" {
  bucket = "${local.name_prefix}-storage"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-storage"
  })
}

resource "aws_s3_bucket_versioning" "app_storage" {
  bucket = aws_s3_bucket.app_storage.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "app_storage" {
  bucket = aws_s3_bucket.app_storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "app_storage" {
  bucket = aws_s3_bucket.app_storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 bucket policy for CloudFront access (if needed)
# resource "aws_s3_bucket_policy" "app_storage" {
#   bucket = aws_s3_bucket.app_storage.id
#   policy = data.aws_iam_policy_document.s3_policy.json
# }

# Terraform state bucket (uncomment if using S3 backend)
# resource "aws_s3_bucket" "terraform_state" {
#   bucket = "${local.name_prefix}-terraform-state"
#
#   tags = merge(local.common_tags, {
#     Name = "${local.name_prefix}-terraform-state"
#   })
# }
#
# resource "aws_s3_bucket_versioning" "terraform_state" {
#   bucket = aws_s3_bucket.terraform_state.id
#   versioning_configuration {
#     status = "Enabled"
#   }
# }
#
# resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
#   bucket = aws_s3_bucket.terraform_state.id
#   rule {
#     apply_server_side_encryption_by_default {
#       sse_algorithm = "AES256"
#     }
#   }
# }
