# Dual Alpaca Account Setup - Complete Documentation

## Overview

This document describes the complete setup for running separate Alpaca paper trading accounts for development and production environments, with AWS Secrets Manager integration.

## Architecture

### Account Structure

- **Development Account**: Used for local development and testing
  - Account Name: Dev Trading Account
  - Account Number: PA31C9WZ7GWR
  - Stored in: AWS Secrets Manager (`alpaca-api-key-dev`, `alpaca-secret-key-dev`)

- **Production Account**: Used for production trading
  - Account Name: Production Trading Account
  - Account Number: PA3H4L4I74RL
  - Stored in: AWS Secrets Manager (`alpaca-api-key-production`, `alpaca-secret-key-production`)

### Environment Detection

The system automatically detects the environment using:
1. `ARGO_ENVIRONMENT` environment variable (highest priority)
2. Presence of `/root/argo-production/config.json` (production indicator)
3. Hostname containing "production" or "prod"
4. Working directory path containing `/root/argo-production`
5. Defaults to "development" if none of the above

### Credential Selection Priority

1. **AWS Secrets Manager** (primary)
   - Environment-specific secrets first (`alpaca-api-key-dev` or `alpaca-api-key-production`)
   - Generic secrets as fallback (`alpaca-api-key`)

2. **config.json** (fallback)
   - Environment-specific sections (`alpaca.dev` or `alpaca.production`)
   - Legacy structure as fallback

3. **Environment Variables** (last resort)
   - `ALPACA_API_KEY` and `ALPACA_SECRET_KEY`

## Setup Instructions

### 1. AWS Secrets Manager Setup

#### Prerequisites
- AWS account with Secrets Manager access
- IAM user/role with Secrets Manager permissions
- AWS CLI installed and configured

#### Required IAM Permissions

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

#### Adding Secrets

Run the setup script on production:

```bash
ssh root@178.156.194.174
cd /root/argo-production
./scripts/setup_aws_secrets_manager.sh
```

Or manually add secrets:

```bash
python scripts/add_alpaca_secrets_to_aws.py
```

### 2. Configuration Files

#### config.json Structure

```json
{
  "alpaca": {
    "dev": {
      "api_key": "PKKTZHTVMTOW7DPPYNOGYPKHWD",
      "secret_key": "56mYiK5MBahHS6wRH7ghC6Mtqt2nxwcTBB9odMjcTMc2",
      "paper": true,
      "account_name": "Dev Trading Account"
    },
    "production": {
      "api_key": "PKVFBDORPHOCX5NEOVEZNDTWVT",
      "secret_key": "ErscqTCdo21raoiFFyDzASzHpfgWB8L7xWVWKFukVa6b",
      "paper": true,
      "account_name": "Production Trading Account"
    }
  }
}
```

#### .env Configuration

Production server `.env`:

```env
USE_AWS_SECRETS=true
AWS_DEFAULT_REGION=us-east-1
```

## Verification

### Check Account Status

**Production:**
```bash
ssh root@178.156.194.174
cd /root/argo-production
source venv/bin/activate
python scripts/check_account_status.py
```

**Development (Local):**
```bash
cd argo
python scripts/check_account_status.py
```

### Verify AWS Secrets Manager

```bash
python scripts/monitor_aws_secrets_health.py
```

### End-to-End Test

```bash
python scripts/test_end_to_end.py
```

## Monitoring

### Health Checks

1. **AWS Secrets Manager Health**
   - Run: `python scripts/monitor_aws_secrets_health.py`
   - Checks all required secrets are accessible
   - Alerts on missing or inaccessible secrets

2. **Account Verification**
   - Run: `python scripts/check_account_status.py`
   - Verifies correct account is being used
   - Shows current positions and portfolio status

3. **End-to-End Test**
   - Run: `python scripts/test_end_to_end.py`
   - Tests complete system flow
   - Verifies all components are operational

### Logging

The system logs environment detection and account selection:

```
INFO:AlpinePaperTrading:🌍 Environment detected: production
INFO:AlpinePaperTrading:📊 Using Production paper account: Production Trading Account
INFO:AlpinePaperTrading:✅ Alpaca connected (production) | Account: Production Trading Account
```

## Troubleshooting

### Issue: Wrong Account Being Used

**Symptoms:** Production using dev account or vice versa

**Solution:**
1. Check environment detection: `python -c "from argo.core.environment import detect_environment; print(detect_environment())"`
2. Verify AWS Secrets Manager has correct secrets
3. Check config.json structure
4. Review logs for environment detection messages

### Issue: AWS Secrets Manager Not Working

**Symptoms:** System falls back to config.json

**Solution:**
1. Verify AWS credentials: `aws sts get-caller-identity`
2. Check IAM permissions
3. Verify secrets exist: `aws secretsmanager list-secrets --filters Key=name,Values=argo-alpine`
4. Check .env has `USE_AWS_SECRETS=true`

### Issue: Environment Detection Incorrect

**Symptoms:** Wrong environment detected

**Solution:**
1. Set explicit environment variable: `export ARGO_ENVIRONMENT=production`
2. Check hostname: `hostname`
3. Verify file paths exist
4. Review `argo/core/environment.py` logic

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use AWS Secrets Manager** for production secrets
3. **Rotate credentials** regularly
4. **Monitor access** via CloudTrail
5. **Use least privilege** IAM permissions
6. **Separate accounts** for dev and production

## Deployment

### Production Deployment

The deployment script (`scripts/deploy-argo.sh`) automatically:
1. Deploys code to production server
2. Verifies Alpaca account configuration
3. Confirms correct account is being used

### Development Setup

Local development automatically:
1. Detects development environment
2. Uses dev Alpaca account
3. Falls back to config.json if AWS unavailable

## Scripts Reference

- `scripts/check_account_status.py` - Verify which account is active
- `scripts/add_alpaca_secrets_to_aws.py` - Add secrets to AWS Secrets Manager
- `scripts/setup_aws_secrets_manager.sh` - Complete AWS setup automation
- `scripts/monitor_aws_secrets_health.py` - Monitor secrets health
- `scripts/test_end_to_end.py` - End-to-end system test

## Status

✅ **Complete and Operational**

- Environment detection: Working
- Account selection: Working
- AWS Secrets Manager: Configured
- Production: Operational (16 positions)
- Development: Ready
- Monitoring: Available

## Support

For issues or questions:
1. Check logs: `/tmp/argo.log` (production)
2. Run health checks: `python scripts/monitor_aws_secrets_health.py`
3. Verify account: `python scripts/check_account_status.py`
4. Review this documentation

