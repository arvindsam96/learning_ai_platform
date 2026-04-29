terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    # Configure this based on your needs
    # bucket = "your-terraform-state-bucket"
    # key    = "learning-ai-platform/terraform.tfstate"
    # region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region

  # Optional: Use profiles or assume roles
  # profile = var.aws_profile
  # assume_role {
  #   role_arn = var.aws_role_arn
  # }
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Data sources
data "aws_caller_identity" "current" {}
