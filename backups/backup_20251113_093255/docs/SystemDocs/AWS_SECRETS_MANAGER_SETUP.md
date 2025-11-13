# AWS Secrets Manager Setup Guide

This guide explains how to set up and use AWS Secrets Manager for centralized secret management across the Argo-Alpine monorepo.

## Overview

AWS Secrets Manager provides secure, centralized storage for all secrets used by:
- **Argo Trading Engine** - API keys, Redis credentials, trading secrets
- **Alpine Backend** - Stripe keys, JWT secrets, database URLs, Redis credentials
- **Alpine Frontend** - API keys (via backend)

## Architecture

### Secret Naming Convention

Secrets are organized by service with the following naming pattern:
```
argo-alpine/{service}/{secret-key}
```

Examples:
- `argo-alpine/argo/redis-password`
- `argo-alpine/argo/alpaca-api-key`
- `argo-alpine/alpine-backend/stripe-secret-key`
- `argo-alpine/alpine-backend/jwt-secret`

### Fallback Strategy

The system uses a three-tier fallback strategy:
1. **AWS Secrets Manager** (primary) - Production secrets
2. **Environment Variables** (fallback) - Local development
3. **Default Values** (last resort) - Non-sensitive defaults

This ensures:
- ✅ Production uses secure AWS Secrets Manager
- ✅ Local development works without AWS setup
- ✅ Services continue working if AWS is temporarily unavailable

## Prerequisites

### 1. AWS Account Setup

1. **Create AWS Account** (if you don't have one)
2. **Install AWS CLI**:
   ```bash
   pip install awscli
   # or
   brew install awscli
   ```

3. **Configure AWS Credentials**:
   ```bash
   aws configure
   ```
   Enter:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region (e.g., `us-east-1`)
   - Default output format: `json`

### 2. IAM Permissions

Create an IAM user or role with the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret",
        "secretsmanager:CreateSecret",
        "secretsmanager:PutSecretValue",
        "secretsmanager:UpdateSecret"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:argo-alpine/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:ListSecrets"
      ],
      "Resource": "*"
    }
  ]
}
```

### 3. Install Dependencies

```bash
# Argo
cd argo
pip install -r requirements.txt

# Alpine Backend
cd alpine-backend
pip install -r backend/requirements.txt
```

## Migration Process

### Step 1: Dry Run Migration

First, test the migration without actually uploading secrets:

```bash
python scripts/migrate-secrets-to-aws.py --dry-run
```

This will show you what secrets would be migrated without actually uploading them.

### Step 2: Migrate Secrets

Run the migration script to upload all secrets:

```bash
python scripts/migrate-secrets-to-aws.py --verify
```

The script will:
1. Read secrets from `.env` files and `config.json`
2. Upload them to AWS Secrets Manager
3. Verify that secrets were uploaded correctly

### Step 3: Verify Secrets

Verify that secrets are accessible:

```bash
python scripts/migrate-secrets-to-aws.py --verify
```

Or manually check:

```bash
aws secretsmanager list-secrets --filters Key=name,Values=argo-alpine
```

### Step 4: Enable AWS Secrets Manager

Set the environment variable to enable AWS Secrets Manager:

```bash
export USE_AWS_SECRETS=true
```

Or add to your `.env` files:
```env
USE_AWS_SECRETS=true
```

### Step 5: Restart Services

Restart all services to use AWS Secrets Manager:

```bash
# Argo
cd argo
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Alpine Backend
cd alpine-backend
source venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 9001
```

### Step 6: Verify Health Checks

Check that all services are healthy:

```bash
# Argo
curl http://localhost:8000/health

# Alpine Backend
curl http://localhost:9001/health
```

## Secret Reference

### Argo Secrets

| Secret Key | Description | Required |
|------------|-------------|----------|
| `argo/redis-host` | Redis hostname | No (default: localhost) |
| `argo/redis-port` | Redis port | No (default: 6379) |
| `argo/redis-password` | Redis password | No |
| `argo/redis-db` | Redis database number | No (default: 0) |
| `argo/api-secret` | Argo API secret key | Yes |
| `argo/alpaca-api-key` | Alpaca API key | Yes (for trading) |
| `argo/alpaca-secret-key` | Alpaca secret key | Yes (for trading) |
| `argo/alpaca-paper` | Use paper trading (true/false) | No (default: true) |
| `argo/alpha-vantage-api-key` | Alpha Vantage API key | No |
| `argo/anthropic-api-key` | Anthropic API key | No |
| `argo/perplexity-api-key` | Perplexity API key | No |
| `argo/xai-api-key` | XAI API key | No |
| `argo/massive-api-key` | Massive API key | No |
| `argo/x-api-bearer-token` | X API bearer token | No |
| `argo/sonar-api-key` | Sonar API key | No |

### Alpine Backend Secrets

| Secret Key | Description | Required |
|------------|-------------|----------|
| `alpine-backend/stripe-secret-key` | Stripe secret key | Yes |
| `alpine-backend/stripe-publishable-key` | Stripe publishable key | Yes |
| `alpine-backend/stripe-webhook-secret` | Stripe webhook secret | Yes |
| `alpine-backend/stripe-account-id` | Stripe account ID | No |
| `alpine-backend/stripe-starter-price-id` | Stripe starter price ID | No |
| `alpine-backend/stripe-pro-price-id` | Stripe pro price ID | No |
| `alpine-backend/stripe-elite-price-id` | Stripe elite price ID | No |
| `alpine-backend/database-url` | PostgreSQL connection string | Yes |
| `alpine-backend/jwt-secret` | JWT signing secret | Yes |
| `alpine-backend/domain` | Domain name | Yes |
| `alpine-backend/frontend-url` | Frontend URL | Yes |
| `alpine-backend/redis-host` | Redis hostname | No (default: localhost) |
| `alpine-backend/redis-port` | Redis port | No (default: 6379) |
| `alpine-backend/redis-password` | Redis password | No |
| `alpine-backend/redis-db` | Redis database number | No (default: 0) |
| `alpine-backend/sendgrid-api-key` | SendGrid API key | No |

## Local Development

For local development, you can disable AWS Secrets Manager:

```bash
export USE_AWS_SECRETS=false
```

Or use environment variables directly (the system will automatically fall back).

## Production Deployment

### EC2/On-Premise Servers

1. **Install AWS CLI** on the server
2. **Configure IAM Role** (recommended) or IAM user credentials
3. **Set Environment Variable**:
   ```bash
   export USE_AWS_SECRETS=true
   export AWS_DEFAULT_REGION=us-east-1
   ```
4. **Deploy and Start Services**

### Docker Containers

1. **Mount AWS Credentials** (if using IAM user):
   ```yaml
   volumes:
     - ~/.aws:/root/.aws:ro
   ```

2. **Or Use IAM Role** (if running on EC2):
   - Attach IAM role to EC2 instance
   - No credentials needed in container

3. **Set Environment Variables**:
   ```yaml
   environment:
     - USE_AWS_SECRETS=true
     - AWS_DEFAULT_REGION=us-east-1
   ```

### Kubernetes

1. **Create Secret for AWS Credentials** (if using IAM user):
   ```bash
   kubectl create secret generic aws-credentials \
     --from-file=credentials=$HOME/.aws/credentials \
     --from-file=config=$HOME/.aws/config
   ```

2. **Or Use IAM Role for Service Account** (IRSA) - Recommended

3. **Set Environment Variables** in deployment:
   ```yaml
   env:
     - name: USE_AWS_SECRETS
       value: "true"
     - name: AWS_DEFAULT_REGION
       value: "us-east-1"
   ```

## Security Best Practices

1. **Least Privilege**: Grant only necessary permissions
2. **Rotation**: Enable automatic rotation for critical secrets (e.g., database passwords)
3. **Encryption**: All secrets are encrypted at rest and in transit
4. **Audit**: Enable CloudTrail to audit secret access
5. **Versioning**: AWS Secrets Manager automatically versions secrets
6. **Backup**: Secrets are automatically backed up by AWS

## Troubleshooting

### Secrets Not Found

**Error**: `Required secret not found: argo-alpine/argo/api-secret`

**Solution**:
1. Verify secret exists: `aws secretsmanager describe-secret --secret-id argo-alpine/argo/api-secret`
2. Check IAM permissions
3. Verify AWS credentials are configured
4. Check region matches

### Fallback to Environment Variables

If AWS Secrets Manager is unavailable, the system automatically falls back to environment variables. Check logs for warnings.

### Cache Issues

Secrets are cached for 5 minutes by default. To clear cache:
```python
from utils.secrets_manager import get_secrets_manager
get_secrets_manager().clear_cache()
```

## Cost Considerations

AWS Secrets Manager pricing:
- **$0.40 per secret per month**
- **$0.05 per 10,000 API calls**

For this setup:
- ~20 secrets = $8/month
- API calls: Minimal (cached for 5 minutes)

**Cost Optimization**:
- Use caching (already implemented)
- Consider AWS Systems Manager Parameter Store for non-sensitive config (free tier available)

## Migration Checklist

- [ ] AWS account created and configured
- [ ] IAM permissions set up
- [ ] Dependencies installed (boto3)
- [ ] Migration script tested (dry-run)
- [ ] Secrets migrated to AWS
- [ ] Secrets verified
- [ ] USE_AWS_SECRETS=true set
- [ ] Services restarted
- [ ] Health checks passing
- [ ] Local development still works (fallback)
- [ ] Production deployment tested

## Support

For issues or questions:
1. Check logs for error messages
2. Verify AWS credentials and permissions
3. Test with `--dry-run` flag
4. Review this documentation

## Additional Resources

- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [boto3 Secrets Manager Client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

