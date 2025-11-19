# API Keys Setup Guide

## Status: ⚠️ ACTION REQUIRED

### Missing API Keys
1. **Alpha Vantage** - Need to obtain and add API key
2. **Perplexity/Sonar** - ✅ Key found in docs, adding to AWS Secrets Manager

---

## How to Get API Keys

### 1. Alpha Vantage API Key
- **Website**: https://www.alphavantage.co/support/#api-key
- **Free Tier**: 5 API calls per minute, 500 calls per day
- **Steps**:
  1. Visit https://www.alphavantage.co/support/#api-key
  2. Fill out the form (name, email, organization)
  3. Get your free API key
  4. Add to AWS Secrets Manager (see below)

### 2. Perplexity API Key
- **Status**: ✅ Already have key from docs
- **Key**: `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`
- **Action**: Adding to AWS Secrets Manager

---

## Adding Keys to AWS Secrets Manager

### Secret Names (for `argo` service):
- Alpha Vantage: `argo-capital/argo/alpha-vantage-api-key` (or `argo-alpine/argo/alpha-vantage-api-key` for backward compatibility)
- Perplexity: `argo-capital/argo/perplexity-api-key` (or `argo-alpine/argo/perplexity-api-key` for backward compatibility)

### Using Python Script:
```python
from argo.utils.secrets_manager import get_secrets_manager

sm = get_secrets_manager()

# Add Alpha Vantage
sm.set_secret(
    'alpha-vantage-api-key',
    'YOUR_ALPHA_VANTAGE_KEY',
    service='argo',
    description='Alpha Vantage API key for technical indicators',
    force_create=True
)

# Add Perplexity (already have key)
sm.set_secret(
    'perplexity-api-key',
    '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',
    service='argo',
    description='Perplexity Sonar API key for news research',
    force_create=True
)
```

### Using AWS CLI:
```bash
# Alpha Vantage
aws secretsmanager create-secret \
  --name argo-capital/argo/alpha-vantage-api-key \
  --secret-string "YOUR_ALPHA_VANTAGE_KEY" \
  --description "Alpha Vantage API key for technical indicators" \
  --region us-east-1

# Perplexity
aws secretsmanager create-secret \
  --name argo-capital/argo/perplexity-api-key \
  --secret-string "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" \
  --description "Perplexity Sonar API key for news research" \
  --region us-east-1
```

---

## Verification

After adding keys, verify they're accessible:

```python
from argo.utils.secrets_manager import get_secret

alpha = get_secret('alpha-vantage-api-key', service='argo')
perplexity = get_secret('perplexity-api-key', service='argo')

print(f'Alpha Vantage: {"✅ Found" if alpha else "❌ Not found"}')
print(f'Perplexity: {"✅ Found" if perplexity else "❌ Not found"}')
```

---

## Next Steps

1. ✅ Add Perplexity key (already have it)
2. ⚠️ Get Alpha Vantage API key from website
3. ⚠️ Add Alpha Vantage key to AWS Secrets Manager
4. Restart signal generator service
5. Verify sources are contributing signals

---

## Expected Impact

Once both keys are added:
- **Alpha Vantage**: +1 source for stocks (25% weight)
- **Sonar AI**: +1 source for all symbols (15% weight)
- **Total sources**: 5-6 per symbol (up from 2-3)
- **Expected confidence**: 75-85% (up from 64.99%)

