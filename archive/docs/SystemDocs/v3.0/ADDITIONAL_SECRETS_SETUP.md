# Additional Secrets Setup - Manual Instructions

## Status

The script has been created and code has been updated, but the current AWS IAM user (`argo-compliance-backup`) doesn't have permission to create secrets. 

## What Was Done

✅ **Code Updates:**
- Updated `argo/argo/integrations/premium_apis.py` to use AWS Secrets Manager
- Updated `argo/argo/integrations/complete_tracking.py` to use AWS Secrets Manager
- Created `scripts/add-additional-secrets.py` script

✅ **Secrets Ready to Add:**
- Anthropic API key
- Perplexity Sonar API key
- X.AI (Grok) API key
- Sonar Administration key
- Figma API key
- NextAuth secret

## Required IAM Permissions

The IAM user/role needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:CreateSecret",
        "secretsmanager:PutSecretValue",
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:argo-alpine/*"
    }
  ]
}
```

## Option 1: Add Secrets via AWS CLI (Recommended)

If you have AWS CLI configured with proper permissions, run these commands:

```bash
# Anthropic API Key
aws secretsmanager create-secret \
  --name argo-alpine/argo/anthropic-api-key \
  --secret-string "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" \
  --description "Anthropic Claude API key for sentiment analysis" \
  --region us-east-1

# Perplexity Sonar API Key
aws secretsmanager create-secret \
  --name argo-alpine/argo/perplexity-api-key \
  --secret-string "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" \
  --description "Perplexity Sonar API key for news research" \
  --region us-east-1

# X.AI (Grok) API Key
aws secretsmanager create-secret \
  --name argo-alpine/argo/xai-api-key \
  --secret-string "xai-ZZrAK9BXQNAlCeaem6cZMVMZtOB42pE9WtAmXGcPyFz6Yuiha8TuC2Y4wxKWiQ0rt3vlNFDnsumf3q3h" \
  --description "X.AI (Grok) API key" \
  --region us-east-1

# Sonar Administration Key
aws secretsmanager create-secret \
  --name argo-alpine/argo/sonar-admin-key \
  --secret-string "squ_4a0d61cdd0e37e20d2c5928c639f5bc6e4beb478" \
  --description "Sonar Administration API key" \
  --region us-east-1

# Figma API Key
aws secretsmanager create-secret \
  --name argo-alpine/argo/figma-api-key \
  --secret-string "figd_UBvI6J7L_N7XLqCuY0cpPi1jb7GMVW00PYn11Epr" \
  --description "Figma API key (Primary)" \
  --region us-east-1

# NextAuth Secret
aws secretsmanager create-secret \
  --name argo-alpine/alpine-frontend/nextauth-secret \
  --secret-string "iOgv8d7F96pLruaD9t+2Bc2b/5x38jWf4zqX2mRgj+o=" \
  --description "NextAuth.js secret for session encryption" \
  --region us-east-1
```

## Option 2: Add Secrets via AWS Console

1. Go to AWS Secrets Manager Console
2. Click "Store a new secret"
3. Select "Other type of secret"
4. Enter the secret value
5. Name it following the pattern: `argo-alpine/{service}/{secret-key}`
6. Add description
7. Click "Store"

## Option 3: Update IAM Permissions

If you want to use the script, update the IAM user/role permissions:

1. Go to IAM Console
2. Find the user/role: `argo-compliance-backup`
3. Add the policy shown above
4. Run the script again: `python scripts/add-additional-secrets.py`

## Tradervue Gold Credentials

To add Tradervue Gold credentials later (when you have them):

```bash
# Using AWS CLI
aws secretsmanager create-secret \
  --name argo-alpine/argo/tradervue-username \
  --secret-string "YOUR_USERNAME" \
  --description "Tradervue Gold username" \
  --region us-east-1

aws secretsmanager create-secret \
  --name argo-alpine/argo/tradervue-api-token \
  --secret-string "YOUR_TOKEN" \
  --description "Tradervue Gold API token" \
  --region us-east-1

# Or using the script (after fixing permissions)
python scripts/add-additional-secrets.py --tradervue-username YOUR_USERNAME --tradervue-token YOUR_TOKEN
```

## Verification

After adding secrets, verify they're accessible:

```bash
# List all argo-alpine secrets
aws secretsmanager list-secrets \
  --filters Key=name,Values=argo-alpine \
  --region us-east-1

# Verify a specific secret
aws secretsmanager get-secret-value \
  --secret-id argo-alpine/argo/anthropic-api-key \
  --region us-east-1
```

## Secret Names Summary

| Secret | Full Name |
|--------|-----------|
| Anthropic API | `argo-alpine/argo/anthropic-api-key` |
| Perplexity Sonar | `argo-alpine/argo/perplexity-api-key` |
| X.AI (Grok) | `argo-alpine/argo/xai-api-key` |
| Sonar Admin | `argo-alpine/argo/sonar-admin-key` |
| Figma API | `argo-alpine/argo/figma-api-key` |
| NextAuth Secret | `argo-alpine/alpine-frontend/nextauth-secret` |
| Tradervue Username | `argo-alpine/argo/tradervue-username` |
| Tradervue Token | `argo-alpine/argo/tradervue-api-token` |

## Next Steps

1. **Add secrets** using one of the options above
2. **Verify secrets** are accessible
3. **Restart services** to use the new secrets
4. **Test functionality** to ensure everything works

## Code Already Updated

The following code files have been updated to use AWS Secrets Manager:

- ✅ `argo/argo/integrations/premium_apis.py` - Uses AWS Secrets Manager for API keys
- ✅ `argo/argo/integrations/complete_tracking.py` - Uses AWS Secrets Manager for tracking credentials

Once secrets are added to AWS Secrets Manager, the code will automatically use them (with fallback to environment variables).

