# Data Sources Rules

**Last Updated:** November 14, 2025  
**Version:** 1.0  
**Applies To:** Argo Trading Engine

---

## Overview

Rules for data source integration, optimization, and configuration in the Argo trading system. Ensures optimal data quality, cost efficiency, and system reliability.

**Strategic Context:** Data source optimization aligns with strategic goals for signal quality (96%+ win rate) and cost efficiency defined in [24_VISION_MISSION_GOALS.md](24_VISION_MISSION_GOALS.md).

---

## Data Source Architecture

### Current Data Sources (6 Total)

1. **Alpaca Pro** (40% weight)
   - **Type:** Primary market data
   - **Priority:** First (tried before Massive.com)
   - **Fallback:** Massive.com
   - **Coverage:** Stocks and crypto
   - **Cost:** Already paid (Alpaca Pro subscription)

2. **Massive.com** (40% weight)
   - **Type:** Market data (formerly Polygon.io)
   - **Priority:** Fallback for Alpaca Pro
   - **Coverage:** Stocks and crypto
   - **Plan:** Currencies Starter ($49/month)
   - **Features:** Unlimited API calls, real-time data, 10+ years historical, WebSockets
   - **Optimization:** 10-second cache for performance (not rate limiting)

3. **yfinance** (25% weight)
   - **Type:** Technical indicators (free)
   - **Priority:** First (tried before Alpha Vantage)
   - **Fallback:** Alpha Vantage
   - **Coverage:** Stocks and crypto
   - **Cost:** Free

4. **Alpha Vantage** (25% weight)
   - **Type:** Technical indicators
   - **Priority:** Supplement to yfinance
   - **Coverage:** Stocks and crypto
   - **Cost:** Paid subscription

5. **xAI Grok** (20% weight)
   - **Type:** Sentiment analysis (Option 2B optimized)
   - **Model:** grok-4-fast-reasoning
   - **Optimization:** Market hours for stocks, 24/7 for crypto, 90s cache
   - **Coverage:** Stocks (market hours) and crypto (24/7)
   - **Cost:** ~$15/month (97% cost reduction)

6. **Sonar AI** (15% weight)
   - **Type:** AI analysis (Perplexity)
   - **Optimization:** Market hours for stocks, 24/7 for crypto, 120s cache
   - **Coverage:** Stocks (market hours) and crypto (24/7)
   - **Cost:** Paid subscription

---

## Data Source Rules

### Priority and Fallback Rules

**Rule:** Primary sources are tried first, fallbacks used if primary fails
- Alpaca Pro → Massive.com (market data)
- yfinance → Alpha Vantage (technical indicators)

**Rule:** Multiple sources can contribute to same signal
- Highest confidence source signal is used
- Consensus combines all available sources

**Rule:** System continues operating if some sources fail
- Minimum 1 source required for signal generation
- All sources checked in parallel for speed

### Optimization Rules

#### xAI Grok (Option 2B)

**Rule:** Market hours detection for stocks
- Stocks: Only during 9:30 AM - 4:00 PM ET
- Crypto: 24/7 coverage
- Implementation: `_is_market_hours()` and `_is_crypto_symbol()`

**Rule:** Sentiment caching
- Cache duration: 90 seconds
- Reduces API calls by ~50%
- Implementation: `_get_cached_sentiment()`

**Rule:** Model selection
- Use `grok-4-fast-reasoning` (cost-effective, high quality)
- Balance cost and quality

#### Sonar AI

**Rule:** Market hours detection for stocks
- Stocks: Only during 9:30 AM - 4:00 PM ET
- Crypto: 24/7 coverage
- Implementation: `_is_market_hours()` and `_is_crypto_symbol()`

**Rule:** Analysis caching
- Cache duration: 120 seconds
- Reduces API calls
- Implementation: `_get_cached_analysis()`

### Configuration Rules

**Rule:** All data sources must have `enabled` flag
- Check `enabled` before making API calls
- Graceful degradation if disabled

**Rule:** API keys stored in `config.json` (dev) or AWS Secrets Manager (prod)
- Never commit actual API keys
- Use `config.json.example` as template

**Rule:** Data source weights must sum to ~1.0 (±0.05 tolerance)
- Configured in `config.json` under `strategy` section
- Weights automatically normalized if needed

### Error Handling Rules

**Rule:** All data source calls must have timeout
- Default: 15 seconds
- Prevents hanging requests

**Rule:** All data source calls must be async
- Use `asyncio.to_thread()` for blocking calls
- Fallback to `run_in_executor` for Python < 3.9

**Rule:** Log all data source errors
- Use appropriate log level (WARNING for expected failures, ERROR for unexpected)
- Include symbol and error details

**Rule:** Never fail signal generation due to single source failure
- Continue with remaining sources
- Log source failures for monitoring

---

## API Key Management

### Required API Keys

1. **xAI Grok**
   - Key: `xai.api_key` in config.json
   - Format: `xai-...`
   - Source: xAI Console (https://console.x.ai)

2. **Sonar AI (Perplexity)**
   - Key: `sonar.api_key` in config.json
   - Format: `pplx-...`
   - Source: Perplexity API (https://www.perplexity.ai)

3. **Massive.com**
   - Key: `massive.api_key` in config.json
   - Format: Alphanumeric string
   - Source: Massive.com (formerly Polygon.io)

4. **Alpha Vantage**
   - Key: `alpha_vantage.api_key` in config.json
   - Format: Alphanumeric string
   - Source: Alpha Vantage (https://www.alphavantage.co)

5. **Alpaca Pro**
   - Keys: `alpaca.dev.api_key` and `alpaca.production.api_key`
   - Format: Alphanumeric strings
   - Source: Alpaca Markets (https://alpaca.markets)

### API Key Verification

**Rule:** Verify API keys on service initialization
- Check if key exists and is not empty
- Log warning if key missing (service continues with fallback)

**Rule:** Test API keys during health checks
- Include in Level 3 comprehensive health check
- Report status but don't fail if optional source unavailable

---

## Cost Optimization

### xAI Grok Cost Optimization (Option 2B)

**Strategy:**
- Model: `grok-4-fast-reasoning` (cost-effective)
- Market hours only for stocks (reduces calls by ~60%)
- 24/7 for crypto (maintains coverage)
- 90-second cache (reduces calls by ~50%)
- **Result:** ~$15/month (97% reduction from $191/month)

**Rule:** Monitor API usage monthly
- Track actual costs vs. estimates
- Adjust cache duration if needed
- Review market hours coverage

### General Cost Rules

**Rule:** Use free sources when possible
- yfinance is free and high quality
- Prefer free sources for technical indicators

**Rule:** Cache aggressively
- Cache duration: 90-120 seconds for AI sources
- Reduces API calls significantly

**Rule:** Market hours optimization
- Only call stock sources during market hours
- Crypto sources can run 24/7

---

## Data Source Integration

### Adding New Data Sources

**Rule:** Follow data source interface
- Implement `fetch_*()` method (async)
- Implement `generate_signal()` method
- Include `enabled` flag check
- Add to `signal_generation_service.py` initialization

**Rule:** Add to weighted consensus engine
- Update weights in `config.json`
- Update `weighted_consensus_engine.py` if needed
- Ensure weights sum to ~1.0

**Rule:** Document new data source
- Add to this rules file
- Update signal generation guide
- Document API key requirements

### Removing Data Sources

**Rule:** Mark as disabled first
- Set `enabled: false` in config
- Monitor system behavior
- Remove code after confirmation period

---

## Monitoring and Health Checks

### Data Source Health Checks

**Rule:** Include in Level 3 health check
- Check API key presence
- Test connectivity (optional, non-blocking)
- Report status

**Rule:** Monitor data source failures
- Track failure rates per source
- Alert if failure rate > 10%
- Log all failures for analysis

### Signal Generation Monitoring

**Rule:** Track source contribution
- Log which sources contributed to each signal
- Monitor source availability
- Report source usage statistics

---

## Related Rules

- [13_TRADING_OPERATIONS.md](13_TRADING_OPERATIONS.md) - Trading operations and signal generation
- [06_CONFIGURATION.md](06_CONFIGURATION.md) - Configuration management
- [14_MONITORING_OBSERVABILITY.md](14_MONITORING_OBSERVABILITY.md) - Monitoring and health checks
- [07_SECURITY.md](07_SECURITY.md) - Security practices for API keys

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

**Note:** These rules ensure optimal data source integration, cost efficiency, and system reliability. Always follow these rules when working with data sources.

