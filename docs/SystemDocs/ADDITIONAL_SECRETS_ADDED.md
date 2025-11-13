# Additional Secrets Added to AWS Secrets Manager

## Overview

The following additional API keys and secrets have been added to AWS Secrets Manager:

## Secrets Added

### Argo Service (`argo-alpine/argo/*`)

1. **Anthropic API Key**
   - Secret Name: `argo-alpine/argo/anthropic-api-key`
   - Description: Anthropic Claude API key for sentiment analysis
   - Used in: `argo/argo/integrations/premium_apis.py`

2. **Perplexity Sonar API Key**
   - Secret Name: `argo-alpine/argo/perplexity-api-key`
   - Description: Perplexity Sonar API key for news research
   - Used in: `argo/argo/integrations/premium_apis.py`

3. **X.AI (Grok) API Key**
   - Secret Name: `argo-alpine/argo/xai-api-key`
   - Description: X.AI (Grok) API key
   - Used in: `argo/argo/integrations/premium_apis.py`

4. **Sonar Administration Key**
   - Secret Name: `argo-alpine/argo/sonar-admin-key`
   - Description: Sonar Administration API key
   - Used for: Sonar admin operations

5. **Figma API Key**
   - Secret Name: `argo-alpine/argo/figma-api-key`
   - Description: Figma API key (Primary)
   - Used for: Design system integration

6. **Tradervue Gold Username** (if provided)
   - Secret Name: `argo-alpine/argo/tradervue-username`
   - Description: Tradervue Gold username
   - Used in: `argo/argo/integrations/complete_tracking.py`

7. **Tradervue Gold API Token** (if provided)
   - Secret Name: `argo-alpine/argo/tradervue-api-token`
   - Description: Tradervue Gold API token
   - Used in: `argo/argo/integrations/complete_tracking.py`

### Alpine Frontend Service (`argo-alpine/alpine-frontend/*`)

1. **NextAuth Secret**
   - Secret Name: `argo-alpine/alpine-frontend/nextauth-secret`
   - Description: NextAuth.js secret for session encryption
   - Used in: `alpine-frontend/lib/auth.ts` (via `NEXTAUTH_SECRET` env var)

## How to Add These Secrets

### Option 1: Using the Script (Recommended)

```bash
# Dry run first
python scripts/add-additional-secrets.py --dry-run

# Add all secrets
python scripts/add-additional-secrets.py

# Add Tradervue credentials (if you have them)
python scripts/add-additional-secrets.py --tradervue-username YOUR_USERNAME --tradervue-token YOUR_TOKEN
```

### Option 2: Using AWS CLI

```bash
# Anthropic API Key
aws secretsmanager create-secret \
  --name argo-alpine/argo/anthropic-api-key \
  --secret-string "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" \
  --description "Anthropic Claude API key for sentiment analysis"

# Perplexity Sonar API Key
aws secretsmanager create-secret \
  --name argo-alpine/argo/perplexity-api-key \
  --secret-string "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" \
  --description "Perplexity Sonar API key for news research"

# X.AI (Grok) API Key
aws secretsmanager create-secret \
  --name argo-alpine/argo/xai-api-key \
  --secret-string "xai-ZZrAK9BXQNAlCeaem6cZMVMZtOB42pE9WtAmXGcPyFz6Yuiha8TuC2Y4wxKWiQ0rt3vlNFDnsumf3q3h" \
  --description "X.AI (Grok) API key"

# Sonar Administration Key
aws secretsmanager create-secret \
  --name argo-alpine/argo/sonar-admin-key \
  --secret-string "squ_4a0d61cdd0e37e20d2c5928c639f5bc6e4beb478" \
  --description "Sonar Administration API key"

# Figma API Key
aws secretsmanager create-secret \
  --name argo-alpine/argo/figma-api-key \
  --secret-string "figd_UBvI6J7L_N7XLqCuY0cpPi1jb7GMVW00PYn11Epr" \
  --description "Figma API key (Primary)"

# NextAuth Secret
aws secretsmanager create-secret \
  --name argo-alpine/alpine-frontend/nextauth-secret \
  --secret-string "iOgv8d7F96pLruaD9t+2Bc2b/5x38jWf4zqX2mRgj+o=" \
  --description "NextAuth.js secret for session encryption"
```

## Code Updates

### Argo Integrations

The following files have been updated to use AWS Secrets Manager:

1. **`argo/argo/integrations/premium_apis.py`**
   - Now uses AWS Secrets Manager for:
     - Anthropic API key
     - Perplexity API key
     - X.AI API key

2. **`argo/argo/integrations/complete_tracking.py`**
   - Now uses AWS Secrets Manager for:
     - Notion API key
     - Tradervue username and token
     - Power BI stream URL

### Alpine Frontend

**NextAuth Secret:**
- NextAuth.js automatically reads `NEXTAUTH_SECRET` from environment variables
- In production, set this from AWS Secrets Manager during deployment
- For local development, continue using `.env.local`

## Verification

After adding secrets, verify they're accessible:

```bash
# Verify secrets are accessible
python scripts/verify-secrets-health.py

# Or manually check a secret
aws secretsmanager get-secret-value --secret-id argo-alpine/argo/anthropic-api-key
```

## Next Steps

1. **Run the script** to add all secrets:
   ```bash
   python scripts/add-additional-secrets.py
   ```

2. **Add Tradervue credentials** (if you have them):
   ```bash
   python scripts/add-additional-secrets.py --tradervue-username USERNAME --tradervue-token TOKEN
   ```

3. **Verify secrets** are accessible:
   ```bash
   python scripts/verify-secrets-health.py
   ```

4. **Restart services** to use the new secrets:
   ```bash
   # Argo
   cd argo && source venv/bin/activate && uvicorn main:app --reload

   # Alpine Backend
   cd alpine-backend && source venv/bin/activate && uvicorn backend.main:app --reload
   ```

## Notes

- **Tradervue Gold**: If you have the credentials, add them using the `--tradervue-username` and `--tradervue-token` flags
- **NextAuth Secret**: This is used by Next.js at build/runtime. In production, ensure the environment variable is set from AWS Secrets Manager
- **Figma API**: Currently not used in codebase but stored for future use
- **Sonar Admin Key**: Separate from the Perplexity Sonar API key, used for admin operations

## Security

All secrets are:
- ✅ Encrypted at rest with AWS KMS
- ✅ Encrypted in transit with TLS
- ✅ Access controlled via IAM
- ✅ Audited via CloudTrail
- ✅ Version controlled automatically

