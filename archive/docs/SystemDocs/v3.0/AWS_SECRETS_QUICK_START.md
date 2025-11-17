# AWS Secrets Manager - Quick Start Guide

## Quick Setup (5 minutes)

### 1. Install AWS CLI and Configure

```bash
# Install AWS CLI
pip install awscli
# or
brew install awscli

# Configure credentials
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region (e.g., us-east-1)
```

### 2. Install Dependencies

```bash
# Argo
cd argo
pip install -r requirements.txt

# Alpine Backend
cd alpine-backend
pip install -r backend/requirements.txt
```

### 3. Migrate Secrets

```bash
# Dry run first (see what will be migrated)
python scripts/migrate-secrets-to-aws.py --dry-run

# Actually migrate
python scripts/migrate-secrets-to-aws.py --verify
```

### 4. Enable AWS Secrets Manager

```bash
export USE_AWS_SECRETS=true
```

Or add to your `.env` files:
```env
USE_AWS_SECRETS=true
```

### 5. Restart Services

```bash
# Argo
cd argo && source venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Alpine Backend
cd alpine-backend && source venv/bin/activate && uvicorn backend.main:app --reload --host 0.0.0.0 --port 9001
```

### 6. Verify Everything Works

```bash
# Check secrets access
python scripts/verify-secrets-health.py

# Check health endpoints
curl http://localhost:8000/health
curl http://localhost:9001/health
```

## Common Commands

### List All Secrets

```bash
aws secretsmanager list-secrets --filters Key=name,Values=argo-alpine
```

### Get a Secret Value

```bash
aws secretsmanager get-secret-value --secret-id argo-alpine/argo/api-secret
```

### Update a Secret

```bash
aws secretsmanager put-secret-value \
  --secret-id argo-alpine/argo/api-secret \
  --secret-string "new-secret-value"
```

### Disable AWS Secrets Manager (Local Dev)

```bash
export USE_AWS_SECRETS=false
```

## Troubleshooting

### "Required secret not found"

1. Check if secret exists: `aws secretsmanager describe-secret --secret-id argo-alpine/argo/api-secret`
2. Verify IAM permissions
3. Check AWS credentials: `aws sts get-caller-identity`
4. Verify region matches

### Services using fallback (environment variables)

This is normal for local development. Check logs for warnings. To force AWS Secrets Manager, ensure:
- `USE_AWS_SECRETS=true`
- AWS credentials configured
- IAM permissions correct

### Health check shows "degraded" for secrets

This means the service is using environment variable fallback instead of AWS Secrets Manager. This is acceptable for local development but should be fixed in production.

## Secret Naming Reference

All secrets follow this pattern: `argo-alpine/{service}/{secret-key}`

**Argo**: `argo-alpine/argo/*`
- `api-secret`
- `redis-host`, `redis-port`, `redis-password`, `redis-db`
- `alpaca-api-key`, `alpaca-secret-key`
- `alpha-vantage-api-key`, `anthropic-api-key`, etc.

**Alpine Backend**: `argo-alpine/alpine-backend/*`
- `stripe-secret-key`, `stripe-publishable-key`, `stripe-webhook-secret`
- `database-url`, `jwt-secret`
- `domain`, `frontend-url`
- `redis-host`, `redis-port`, `redis-password`, `redis-db`

## Next Steps

- Read full documentation: [AWS_SECRETS_MANAGER_SETUP.md](./AWS_SECRETS_MANAGER_SETUP.md)
- Set up automatic secret rotation for production
- Configure IAM roles for EC2/ECS/Kubernetes
- Enable CloudTrail for audit logging

