# 🚀 Complete AWS Deployment Guide

## Overview

This guide will help you deploy AutoTrader Pro to AWS with:
- ECS Fargate for containers
- RDS PostgreSQL for database
- ElastiCache Redis for caching
- Application Load Balancer
- Route 53 for DNS
- ACM for SSL certificates
- CloudWatch for monitoring

---

## 📋 Prerequisites

1. **AWS Account** with billing enabled
2. **AWS CLI** installed and configured
3. **Terraform** installed (v1.0+)
4. **Docker** installed
5. **Domain name** (optional, for custom domain)

---

## 🔧 Step 1: Configure AWS CLI

```bash
aws configure
# Enter your:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: ap-south-1 (Mumbai)
# - Default output format: json
```

Verify:
```bash
aws sts get-caller-identity
```

---

## 📦 Step 2: Prepare Configuration Files

### Create `infra/aws/terraform/terraform.tfvars`

```hcl
aws_region = "ap-south-1"  # Mumbai region

# Database
db_name     = "autotrader"
db_username = "admin"
db_password = "YourSecurePassword123!"  # Change this!

# Application
secret_key = "your-jwt-secret-key-min-32-chars-long"  # Change this!

# Razorpay (Get from dashboard.razorpay.com)
razorpay_key_id     = "rzp_live_xxxxx"
razorpay_key_secret = "your_secret"

# OAuth (Optional)
google_client_id     = "your-google-client-id"
facebook_app_id      = "your-facebook-app-id"

# Domain (Optional)
domain_name = "autotrader.yourdomain.com"
```

---

## 🏗️ Step 3: Deploy Infrastructure with Terraform

```bash
cd infra/aws/terraform

# Initialize Terraform
terraform init

# Review what will be created
terraform plan

# Deploy (takes ~10-15 minutes)
terraform apply

# Save the outputs
terraform output > outputs.txt
```

This creates:
- VPC with public/private subnets
- RDS PostgreSQL database
- ElastiCache Redis cluster
- ECS Cluster
- ECR repositories
- Application Load Balancer
- Security groups
- IAM roles

---

## 🐳 Step 4: Build and Push Docker Images

### Get ECR Login

```bash
# Get your account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Login to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com
```

### Build and Push Backend

```bash
cd backend

# Build
docker build -t autotrader-backend .

# Tag
docker tag autotrader-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/autotrader-backend:latest

# Push
docker push $AWS_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/autotrader-backend:latest
```

### Build and Push Frontend

```bash
cd ../frontend

# Build production image
docker build -f Dockerfile.prod -t autotrader-frontend .

# Tag
docker tag autotrader-frontend:latest $AWS_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/autotrader-frontend:latest

# Push
docker push $AWS_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/autotrader-frontend:latest
```

---

## 📝 Step 5: Create ECS Task Definitions

### Backend Task Definition

Create `backend-task-def.json`:

```json
{
  "family": "autotrader-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/autotrader-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://admin:password@DB_ENDPOINT:5432/autotrader"
        },
        {
          "name": "REDIS_URL",
          "value": "redis://REDIS_ENDPOINT:6379"
        },
        {
          "name": "SECRET_KEY",
          "value": "your-secret-key"
        },
        {
          "name": "BROKER_MODE",
          "value": "mock"
        },
        {
          "name": "RAZORPAY_KEY_ID",
          "value": "rzp_live_xxxxx"
        },
        {
          "name": "RAZORPAY_KEY_SECRET",
          "value": "your_secret"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/autotrader-backend",
          "awslogs-region": "ap-south-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Register:
```bash
aws ecs register-task-definition --cli-input-json file://backend-task-def.json
```

### Frontend Task Definition

Create `frontend-task-def.json`:

```json
{
  "family": "autotrader-frontend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/autotrader-frontend:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "NEXT_PUBLIC_API_URL",
          "value": "https://api.yourdomain.com"
        },
        {
          "name": "NEXT_PUBLIC_GOOGLE_CLIENT_ID",
          "value": "your-google-client-id"
        },
        {
          "name": "NEXT_PUBLIC_FACEBOOK_APP_ID",
          "value": "your-facebook-app-id"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/autotrader-frontend",
          "awslogs-region": "ap-south-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Register:
```bash
aws ecs register-task-definition --cli-input-json file://frontend-task-def.json
```

---

## 🚀 Step 6: Create ECS Services

### Create Backend Service

```bash
aws ecs create-service \
  --cluster autotrader-cluster \
  --service-name autotrader-backend \
  --task-definition autotrader-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:ap-south-1:ACCOUNT_ID:targetgroup/backend-tg/xxx,containerName=backend,containerPort=8000"
```

### Create Frontend Service

```bash
aws ecs create-service \
  --cluster autotrader-cluster \
  --service-name autotrader-frontend \
  --task-definition autotrader-frontend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:ap-south-1:ACCOUNT_ID:targetgroup/frontend-tg/xxx,containerName=frontend,containerPort=3000"
```

---

## 🔧 Step 7: Configure Load Balancer

### Create Target Groups

```bash
# Backend target group
aws elbv2 create-target-group \
  --name autotrader-backend-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxx \
  --target-type ip \
  --health-check-path /health

# Frontend target group
aws elbv2 create-target-group \
  --name autotrader-frontend-tg \
  --protocol HTTP \
  --port 3000 \
  --vpc-id vpc-xxx \
  --target-type ip \
  --health-check-path /
```

### Add Listener Rules

```bash
# HTTPS listener for frontend
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:ap-south-1:ACCOUNT_ID:loadbalancer/app/autotrader-alb/xxx \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:ap-south-1:ACCOUNT_ID:certificate/xxx \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:ap-south-1:ACCOUNT_ID:targetgroup/frontend-tg/xxx

# HTTPS listener for backend API
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:ap-south-1:ACCOUNT_ID:listener/app/autotrader-alb/xxx/xxx \
  --priority 1 \
  --conditions Field=path-pattern,Values='/api/*' \
  --actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:ap-south-1:ACCOUNT_ID:targetgroup/backend-tg/xxx
```

---

## 🌐 Step 8: Configure Domain & SSL

### Request SSL Certificate

```bash
aws acm request-certificate \
  --domain-name autotrader.yourdomain.com \
  --subject-alternative-names api.autotrader.yourdomain.com \
  --validation-method DNS \
  --region ap-south-1
```

### Create Route 53 Records

```bash
# Frontend
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "autotrader.yourdomain.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z1234567890ABC",
          "DNSName": "autotrader-alb-xxx.ap-south-1.elb.amazonaws.com",
          "EvaluateTargetHealth": false
        }
      }
    }]
  }'

# Backend API
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.autotrader.yourdomain.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z1234567890ABC",
          "DNSName": "autotrader-alb-xxx.ap-south-1.elb.amazonaws.com",
          "EvaluateTargetHealth": false
        }
      }
    }]
  }'
```

---

## 🗄️ Step 9: Initialize Database

### Connect to ECS Task

```bash
# Get task ID
TASK_ID=$(aws ecs list-tasks --cluster autotrader-cluster --service-name autotrader-backend --query 'taskArns[0]' --output text)

# Execute command
aws ecs execute-command \
  --cluster autotrader-cluster \
  --task $TASK_ID \
  --container backend \
  --interactive \
  --command "/bin/sh"
```

### Inside Container

```bash
# Initialize database
python init_db.py

# Exit
exit
```

---

## 📊 Step 10: Setup Monitoring

### Create CloudWatch Dashboard

```bash
aws cloudwatch put-dashboard \
  --dashboard-name AutoTrader \
  --dashboard-body file://cloudwatch-dashboard.json
```

### Create Alarms

```bash
# High CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name autotrader-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2

# High memory alarm
aws cloudwatch put-metric-alarm \
  --alarm-name autotrader-high-memory \
  --alarm-description "Alert when memory exceeds 80%" \
  --metric-name MemoryUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

---

## 🔄 Step 11: Setup Auto-Scaling

```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/autotrader-cluster/autotrader-backend \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/autotrader-cluster/autotrader-backend \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'
```

---

## 🔐 Step 12: Security Hardening

### Enable VPC Flow Logs

```bash
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-xxx \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /aws/vpc/autotrader
```

### Enable CloudTrail

```bash
aws cloudtrail create-trail \
  --name autotrader-trail \
  --s3-bucket-name autotrader-cloudtrail-logs
```

### Enable GuardDuty

```bash
aws guardduty create-detector --enable
```

---

## 💰 Cost Estimation (Mumbai Region)

### Development Environment
- ECS Fargate (2 tasks): $30/month
- RDS t3.micro: $15/month
- ElastiCache t3.micro: $12/month
- ALB: $20/month
- Data transfer: $10/month
- **Total: ~$87/month**

### Production Environment
- ECS Fargate (4-10 tasks): $60-150/month
- RDS t3.small: $30/month
- ElastiCache t3.small: $25/month
- ALB: $20/month
- Data transfer: $20/month
- CloudWatch: $10/month
- **Total: ~$165-255/month**

---

## ✅ Verification Checklist

- [ ] Terraform applied successfully
- [ ] Docker images pushed to ECR
- [ ] ECS services running
- [ ] Load balancer healthy
- [ ] Database initialized
- [ ] SSL certificate validated
- [ ] Domain resolving correctly
- [ ] API endpoints responding
- [ ] Frontend loading
- [ ] Login working
- [ ] Wallet functional
- [ ] Trading system operational
- [ ] Monitoring dashboards created
- [ ] Alarms configured
- [ ] Auto-scaling enabled
- [ ] Backups configured

---

## 🆘 Troubleshooting

### Services Won't Start
```bash
# Check service events
aws ecs describe-services --cluster autotrader-cluster --services autotrader-backend

# Check task logs
aws logs tail /ecs/autotrader-backend --follow
```

### Database Connection Issues
```bash
# Test connection from ECS task
aws ecs execute-command --cluster autotrader-cluster --task TASK_ID --container backend --interactive --command "psql -h DB_ENDPOINT -U admin -d autotrader"
```

### High Costs
- Scale down to 1 task per service
- Use t3.micro instances
- Enable auto-scaling with lower thresholds
- Set up billing alerts

---

## 📞 Support Resources

- **AWS Support:** https://console.aws.amazon.com/support
- **Terraform Docs:** https://registry.terraform.io/providers/hashicorp/aws
- **ECS Docs:** https://docs.aws.amazon.com/ecs
- **RDS Docs:** https://docs.aws.amazon.com/rds

---

## 🎉 Deployment Complete!

Your AutoTrader Pro is now running on AWS!

**Access your application:**
- Frontend: https://autotrader.yourdomain.com
- API: https://api.autotrader.yourdomain.com
- Health: https://api.autotrader.yourdomain.com/health

**Next steps:**
1. Test all functionality
2. Monitor CloudWatch dashboards
3. Set up automated backups
4. Configure CI/CD pipeline
5. Add custom domain email
6. Set up staging environment
7. Implement blue-green deployments

---

**Congratulations! Your production-grade trading platform is live! 🚀**
