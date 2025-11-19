# API Keys Missing - Action Required

**Date**: November 18, 2025  
**Status**: ⚠️ **ACTION REQUIRED**

---

## Missing API Keys

### 1. Alpha Vantage ❌
- **Status**: No API key found
- **Location**: `config.json` → `api_keys.alpha_vantage`
- **Impact**: Alpha Vantage not contributing signals for stocks
- **Action**: Add Alpha Vantage API key to `config.json`

### 2. Sonar AI (Perplexity) ❌
- **Status**: No API key found
- **Location**: `config.json` → `api_keys.perplexity` or `api_keys.sonar`
- **Impact**: Sonar AI not contributing signals (401 authentication errors)
- **Action**: Add Perplexity API key to `config.json`

---

## Current Config Status

```json
{
  "api_keys": {
    "argo_api_key": "present"
    // Missing: "alpha_vantage"
    // Missing: "perplexity" or "sonar"
  }
}
```

---

## Impact on Signal Generation

- **Alpha Vantage**: Should contribute 30% weight for stocks
- **Sonar AI**: Should contribute 5% weight (15% base, but low priority)
- **Current**: Only massive, yfinance, and xAI Grok contributing
- **Missing**: 2 sources that could boost confidence

---

## Next Steps

1. Add Alpha Vantage API key to `config.json`
2. Add Perplexity API key to `config.json`
3. Restart signal generator service
4. Verify sources are contributing signals

---

## Expected Improvement

Once API keys are added:
- **Alpha Vantage**: +1 source for stocks (30% weight)
- **Sonar AI**: +1 source for all symbols (5% weight)
- **Total sources**: 5-6 per symbol (up from 2-3)
- **Expected confidence**: 75-85% (up from 64.72%)

