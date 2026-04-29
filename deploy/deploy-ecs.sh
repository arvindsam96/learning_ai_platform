#!/bin/bash

# ECS Deployment Script
# This script builds and deploys the application to AWS ECS

set -e

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
PROJECT_NAME=${PROJECT_NAME:-learning-ai-platform}
ENVIRONMENT=${ENVIRONMENT:-dev}
ECR_REPO_NAME="${PROJECT_NAME}-${ENVIRONMENT}-app"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting ECS deployment for ${PROJECT_NAME}...${NC}"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}AWS CLI is not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo -e "${YELLOW}Using ECR repository: ${ECR_REPO_URI}${NC}"

# Authenticate Docker with ECR
echo -e "${YELLOW}Authenticating Docker with ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Build Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t ${ECR_REPO_NAME}:latest .

# Tag the image
docker tag ${ECR_REPO_NAME}:latest ${ECR_REPO_URI}:latest

# Push to ECR
echo -e "${YELLOW}Pushing image to ECR...${NC}"
docker push ${ECR_REPO_URI}:latest

# Get ECS cluster and service names from Terraform outputs
echo -e "${YELLOW}Getting ECS cluster and service information...${NC}"
CLUSTER_NAME=$(cd terraform && terraform output -raw ecs_cluster_name 2>/dev/null || echo "${PROJECT_NAME}-${ENVIRONMENT}-cluster")
SERVICE_NAME=$(cd terraform && terraform output -raw ecs_service_name 2>/dev/null || echo "${PROJECT_NAME}-${ENVIRONMENT}-app")

# Update ECS service
echo -e "${YELLOW}Updating ECS service...${NC}"
aws ecs update-service \
    --cluster ${CLUSTER_NAME} \
    --service ${SERVICE_NAME} \
    --force-new-deployment \
    --region ${AWS_REGION}

# Wait for deployment to complete
echo -e "${YELLOW}Waiting for deployment to complete...${NC}"
aws ecs wait services-stable \
    --cluster ${CLUSTER_NAME} \
    --services ${SERVICE_NAME} \
    --region ${AWS_REGION}

# Get load balancer DNS name
ALB_DNS=$(cd terraform && terraform output -raw alb_dns_name 2>/dev/null || echo "")

if [ -n "$ALB_DNS" ]; then
    echo -e "${GREEN}Deployment completed successfully!${NC}"
    echo -e "${GREEN}Application is available at: http://${ALB_DNS}${NC}"
else
    echo -e "${GREEN}Deployment completed successfully!${NC}"
    echo -e "${YELLOW}Note: Could not retrieve ALB DNS name from Terraform outputs.${NC}"
fi

echo -e "${GREEN}ECS deployment script completed.${NC}"
