# Complete Data Sources Guide

**Date:** November 14, 2025  
**Version:** 1.0  
**Status:** Complete Implementation Guide

---

## Executive Summary

This document provides a comprehensive guide to all data sources in the Argo trading system, including configuration, optimization, cost management, and best practices.

---

## Table of Contents

1. [Overview](#overview)
2. [Data Source Architecture](#data-source-architecture)
3. [Individual Data Sources](#individual-data-sources)
4. [Configuration](#configuration)
5. [Optimization Strategies](#optimization-strategies)
6. [Cost Management](#cost-management)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Overview

### Current Data Sources (6 Total)

The Argo trading system uses 6 data sources with intelligent priority and fallback mechanisms:

1. **Alpaca Pro** (40% weight) - Primary market data
2. **Massive.com** (40% weight) - Fallback market data
3. **yfinance** (25% weight) - Primary technical indicators (free)
4. **Alpha Vantage** (25% weight) - Supplement technical indicators
5. **xAI Grok** (20% weight) - Sentiment analysis (Option 2B optimized)
6. **Sonar AI** (15% weight) - AI analysis (optimized)

### Key Features

- **Priority System:** Primary sources tried first, fallbacks used if needed
- **Cost Optimization:** Aggressive caching and market hours optimization
- **High Availability:** System continues with remaining sources if some fail
- **Quality Focus:** Multiple sources combined for highest confidence signals

---

## Data Source Architecture

### Priority and Fallback Flow

```
Market Data:
  Alpaca Pro (primary) → Massive.com (fallback)

Technical Indicators:
  yfinance (primary) → Alpha Vantage (supplement)

Sentiment Analysis:
  xAI Grok (Option 2B optimized)

AI Analysis:
  Sonar AI (optimized with caching)
```

### Weight Distribution

- **Market Data:** 40% (Alpaca Pro or Massive.com)
- **Technical Indicators:** 25% (yfinance or Alpha Vantage)
- **Sentiment:** 20% (xAI Grok)
- **AI Analysis:** 15% (Sonar AI)

**Total:** 100% (weights sum to 1.0)

---

## Individual Data Sources

### 1. Alpaca Pro

**Purpose:** Primary market data source (real-time, high quality)

**Configuration:**
```json
{
  "alpaca": {
    "dev": {
      "api_key": "...",
      "secret_key": "...",
      "paper": true
    },
    "production": {
      "api_key": "...",
      "secret_key": "...",
      "paper": true
    }
  }
}
```

**Features:**
- Real-time market data
- Stocks and crypto support
- High-quality data
- Already paid (Alpaca Pro subscription)

**Priority:** First (tried before Massive.com)

**Fallback:** Massive.com

**File:** `argo/argo/core/data_sources/alpaca_pro_source.py`

---

### 2. Massive.com (formerly Polygon.io)

**Purpose:** Fallback market data source

**Configuration:**
```json
{
  "massive": {
    "api_key": "...",
    "enabled": true
  }
}
```

**Features:**
- Market data for stocks and crypto
- Fallback when Alpaca Pro unavailable
- **Plan:** Currencies Starter ($49/month)
- **Unlimited API calls** (no rate limits)
- Real-time data available
- 10+ years historical data
- WebSockets, second aggregates, crypto trades & quotes
- **Optimization:** 10-second cache for performance (faster signal updates)

**Priority:** Fallback for Alpaca Pro

**File:** `argo/argo/core/data_sources/massive_source.py`

---

### 3. yfinance

**Purpose:** Primary technical indicators (free, high quality)

**Configuration:**
- No API key required (free)
- Automatically enabled if library installed

**Features:**
- Free technical indicators
- MACD, RSI, SMA, EMA
- Stocks and crypto support
- High-quality data

**Priority:** First (tried before Alpha Vantage)

**Fallback:** Alpha Vantage

**File:** `argo/argo/core/data_sources/yfinance_source.py`

**Installation:**
```bash
pip install yfinance
```

---

### 4. Alpha Vantage

**Purpose:** Supplement technical indicators

**Configuration:**
```json
{
  "alpha_vantage": {
    "api_key": "...",
    "enabled": true
  }
}
```

**Features:**
- Technical indicators (RSI, MACD, SMA, EMA)
- Stocks and crypto support
- Paid subscription

**Priority:** Supplement to yfinance

**File:** `argo/argo/core/data_sources/alpha_vantage_source.py`

---

### 5. xAI Grok (Option 2B Optimized)

**Purpose:** Sentiment analysis with cost optimization

**Configuration:**
```json
{
  "xai": {
    "api_key": "xai-...",
    "enabled": true
  }
}
```

**Optimizations:**
- **Model:** `grok-4-fast-reasoning` (cost-effective, high quality)
- **Market Hours:** Stocks only during 9:30 AM - 4:00 PM ET
- **24/7 Coverage:** Crypto symbols (BTC-USD, ETH-USD, etc.)
- **Caching:** 90-second cache (reduces API calls by ~50%)

**Cost:** ~$15/month (97% reduction from $191/month)

**Priority:** Sentiment analysis

**File:** `argo/argo/core/data_sources/xai_grok_source.py`

**API Key:** Get from https://console.x.ai

---

### 6. Sonar AI (Perplexity)

**Purpose:** AI-powered analysis with optimization

**Configuration:**
```json
{
  "sonar": {
    "api_key": "pplx-...",
    "enabled": true
  }
}
```

**Optimizations:**
- **Market Hours:** Stocks only during 9:30 AM - 4:00 PM ET
- **24/7 Coverage:** Crypto symbols
- **Caching:** 120-second cache (reduces API calls)

**Priority:** AI analysis

**File:** `argo/argo/core/data_sources/sonar_source.py`

**API Key:** Get from https://www.perplexity.ai

---

## Configuration

### Complete Configuration Example

```json
{
  "massive": {
    "api_key": "...",
    "enabled": true
  },
  "alpha_vantage": {
    "api_key": "...",
    "enabled": true
  },
  "xai": {
    "api_key": "xai-...",
    "enabled": true
  },
  "sonar": {
    "api_key": "pplx-...",
    "enabled": true
  },
  "alpaca": {
    "dev": {
      "api_key": "...",
      "secret_key": "...",
      "paper": true
    },
    "production": {
      "api_key": "...",
      "secret_key": "...",
      "paper": true
    }
  },
  "strategy": {
    "use_multi_source": true,
    "weight_massive": 0.4,
    "weight_alpha_vantage": 0.25,
    "weight_x_sentiment": 0.2,
    "weight_sonar": 0.15
  }
}
```

### Environment-Specific Configuration

**Development:**
- API keys in `config.json`
- All sources enabled for testing

**Production:**
- API keys in AWS Secrets Manager (preferred)
- Fallback to `config.json` if Secrets Manager unavailable
- Environment variables as final fallback

---

## Optimization Strategies

### xAI Grok Optimization (Option 2B)

**Strategy:**
1. Use cost-effective model (`grok-4-fast-reasoning`)
2. Market hours only for stocks (reduces calls by ~60%)
3. 24/7 for crypto (maintains coverage)
4. 90-second cache (reduces calls by ~50%)

**Result:**
- Cost: ~$15/month (97% reduction)
- Quality: 94-96% maintained
- Coverage: Market hours stocks, 24/7 crypto

### Sonar AI Optimization

**Strategy:**
1. Market hours only for stocks
2. 24/7 for crypto
3. 120-second cache

**Result:**
- Reduced API calls
- Maintained quality
- Cost savings

### General Optimization Rules

1. **Cache Aggressively:** 90-120 seconds for AI sources
2. **Market Hours:** Only call stock sources during market hours
3. **Free First:** Use free sources (yfinance) when possible
4. **Priority System:** Try primary sources first, fallbacks second

---

## Cost Management

### Monthly Cost Estimates

| Data Source | Cost | Notes |
|-------------|------|-------|
| Alpaca Pro | Already paid | Subscription included |
| Massive.com | Paid | Subscription required |
| yfinance | Free | No cost |
| Alpha Vantage | Paid | Subscription required |
| xAI Grok | ~$15/mo | Option 2B optimized |
| Sonar AI | Paid | Subscription required |

### Cost Optimization Tips

1. **Use Free Sources:** yfinance is free and high quality
2. **Cache Aggressively:** Reduces API calls significantly
3. **Market Hours:** Only call stock sources during market hours
4. **Monitor Usage:** Track actual costs vs. estimates

---

## Troubleshooting

### Common Issues

#### API Key Errors

**Symptom:** `401 Unauthorized` or `Invalid API key`

**Solution:**
1. Verify API key in `config.json`
2. Check API key format (xAI: `xai-...`, Sonar: `pplx-...`)
3. Verify API key is active in provider dashboard
4. Check AWS Secrets Manager if in production

#### Source Not Available

**Symptom:** Source fails to initialize

**Solution:**
1. Check `enabled` flag in config
2. Verify API key is present
3. Check network connectivity
4. Review logs for specific error

#### High API Costs

**Symptom:** Unexpected API costs

**Solution:**
1. Verify caching is working (check logs)
2. Review market hours optimization
3. Check cache duration settings
4. Monitor API usage in provider dashboard

---

## Best Practices

### DO
- ✅ Use primary sources first, fallbacks second
- ✅ Cache aggressively to reduce costs
- ✅ Optimize for market hours (stocks)
- ✅ Monitor API usage and costs
- ✅ Handle errors gracefully
- ✅ Log all source failures

### DON'T
- ❌ Fail signal generation if one source fails
- ❌ Make blocking API calls (use async)
- ❌ Skip timeout configuration
- ❌ Commit API keys to repository
- ❌ Ignore cost optimization opportunities
- ❌ Skip error handling

---

## Related Documentation

- **Rules:** [25_DATA_SOURCES.md](../../Rules/25_DATA_SOURCES.md)
- **Trading Operations:** [SIGNAL_GENERATION_COMPLETE_GUIDE.md](SIGNAL_GENERATION_COMPLETE_GUIDE.md)
- **Configuration:** [CONFIGURATION_MANAGEMENT_COMPLETE_GUIDE.md](CONFIGURATION_MANAGEMENT_COMPLETE_GUIDE.md)
- **Monitoring:** [SYSTEM_MONITORING_COMPLETE_GUIDE.md](SYSTEM_MONITORING_COMPLETE_GUIDE.md)

---

**Last Updated:** November 14, 2025

