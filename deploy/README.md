# AWS Deployment Guide

This guide covers deploying the Learning AI Platform to AWS using Terraform and ECS.

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured (`aws configure`)
3. **Terraform** installed (v1.0+)
4. **Docker** installed
5. **Python 3.13+** for local development

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd learning-ai-platform
cp .env.example .env
# Edit .env with your API keys
```

### 2. Local Development

```bash
# Start local services
docker compose up -d

# Run database migrations
alembic upgrade head

# Seed default prompts
python scripts/seed_prompts.py

# Start the application
uvicorn app.main:app --reload
```

### 3. AWS Deployment

#### Initialize Terraform

```bash
cd terraform
terraform init
```

#### Configure Variables

Create `terraform.tfvars`:

```hcl
aws_region = "us-east-1"
environment = "dev"
project_name = "learning-ai-platform"

# API Keys (store securely!)
openai_api_key = "sk-..."
anthropic_api_key = "sk-ant-..."
pinecone_api_key = "your-pinecone-key"
tavily_api_key = "tvly-..."
```

#### Deploy Infrastructure

```bash
terraform plan
terraform apply
```

#### Build and Deploy Application

```bash
# Make deployment script executable
chmod +x deploy/deploy-ecs.sh

# Deploy to ECS
./deploy/deploy-ecs.sh
```

## Architecture Overview

### AWS Resources Created

- **VPC** with public/private subnets
- **ECS Fargate** cluster and service
- **Application Load Balancer**
- **RDS PostgreSQL** database
- **ElastiCache Redis** cluster
- **S3** bucket for file storage
- **ECR** repository for Docker images
- **AWS Secrets Manager** for secrets

### Environment Variables

#### Local Development (.env)
```bash
ENV=local
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/appdb
REDIS_URL=redis://localhost:6379
UPLOAD_DIR=/app/uploads
```

#### AWS Production
Environment variables are set via ECS task definition and AWS Secrets Manager.

## File Storage

The application supports two storage backends:

### Local Storage (Development)
- Files stored in `/app/uploads` directory
- Used when `S3_BUCKET_NAME` is not configured

### S3 Storage (Production)
- Files uploaded to S3 bucket
- Automatic fallback to local storage if S3 fails
- URLs returned for uploaded files

## Prompt Management

### Default Prompts
The system includes default prompts for:
- RAG queries (with/without web search)
- General chat interactions

### Managing Prompts
Use the API endpoints:
```bash
# List prompts
GET /ai/prompts

# Create prompt
POST /ai/prompts

# Update prompt
PUT /ai/prompts/{id}

# Activate/Deactivate
POST /ai/prompts/{id}/activate
```

## Monitoring

### CloudWatch Logs
- ECS container logs are sent to CloudWatch
- Log group: `/ecs/learning-ai-platform-dev-app`

### Health Checks
- Application health endpoint: `/health`
- Load balancer health checks configured

## Troubleshooting

### Common Issues

1. **ECS Deployment Fails**
   ```bash
   # Check ECS service events
   aws ecs describe-services --cluster <cluster> --services <service>

   # Check CloudWatch logs
   aws logs tail /ecs/learning-ai-platform-dev-app --follow
   ```

2. **Database Connection Issues**
   - Check security groups allow traffic from ECS tasks
   - Verify database credentials in AWS Secrets Manager

3. **S3 Upload Issues**
   - Ensure ECS task role has S3 permissions
   - Check S3 bucket exists and is accessible

### Rollback

To rollback infrastructure changes:
```bash
cd terraform
terraform destroy
```

## Security Considerations

1. **Secrets Management**: All sensitive data stored in AWS Secrets Manager
2. **Network Security**: Application runs in private subnets
3. **Access Control**: IAM roles with least privilege
4. **Encryption**: S3 SSE enabled, database encryption

## Cost Optimization

1. **ECS Fargate**: Pay only for actual usage
2. **RDS**: Use t3.micro for development, scale up for production
3. **ElastiCache**: Small instance for development
4. **S3**: Standard storage with lifecycle policies

## Next Steps

1. **CI/CD Pipeline**: Set up GitHub Actions or CodePipeline
2. **Monitoring**: Add CloudWatch alarms and dashboards
3. **Backup**: Configure automated RDS backups
4. **Scaling**: Implement auto-scaling for ECS services
5. **CDN**: Add CloudFront for static assets
