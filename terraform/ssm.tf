# SSM Parameters for storing secrets
resource "aws_ssm_parameter" "openai_api_key" {
  name  = "/${local.name_prefix}/openai/api_key"
  type  = "SecureString"
  value = "your-openai-api-key-here" # Replace with actual value or use terraform.tfvars

  tags = local.common_tags
}

resource "aws_ssm_parameter" "anthropic_api_key" {
  name  = "/${local.name_prefix}/anthropic/api_key"
  type  = "SecureString"
  value = "your-anthropic-api-key-here" # Replace with actual value or use terraform.tfvars

  tags = local.common_tags
}

resource "aws_ssm_parameter" "pinecone_api_key" {
  name  = "/${local.name_prefix}/pinecone/api_key"
  type  = "SecureString"
  value = "your-pinecone-api-key-here" # Replace with actual value or use terraform.tfvars

  tags = local.common_tags
}

resource "aws_ssm_parameter" "secret_key" {
  name  = "/${local.name_prefix}/app/secret_key"
  type  = "SecureString"
  value = random_password.secret_key.result

  tags = local.common_tags
}

resource "random_password" "secret_key" {
  length  = 32
  special = true
}

# Optional: Tavily API key
resource "aws_ssm_parameter" "tavily_api_key" {
  name  = "/${local.name_prefix}/tavily/api_key"
  type  = "SecureString"
  value = "your-tavily-api-key-here" # Replace with actual value or use terraform.tfvars

  tags = local.common_tags
}
