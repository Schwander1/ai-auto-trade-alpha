# Performance Optimizations Guide v3.0

**Date:** November 15, 2025  
**Version:** 3.0  
**Status:** ✅ Complete Implementation

---

## Executive Summary

This document details all performance optimizations implemented in v3.0, including implementation details, expected improvements, and monitoring guidelines.

---

## Optimization Overview

### Implemented Optimizations

1. ✅ **Adaptive Cache TTL** - Market-hours aware caching
2. ✅ **Skip Unchanged Symbols** - Skip regeneration for unchanged prices
3. ✅ **Redis Distributed Caching** - Persistent, shared cache
4. ✅ **Rate Limiting** - Token bucket algorithm
5. ✅ **Circuit Breaker Pattern** - Automatic failure handling
6. ✅ **Priority-Based Processing** - Volatility-based prioritization
7. ✅ **Database Optimization** - Composite indexes
8. ✅ **Performance Metrics** - Comprehensive tracking

---

## 1. Adaptive Cache TTL

### Implementation

**File:** `argo/argo/core/adaptive_cache.py`

**Features:**
- Market-hours detection (9:30 AM - 4:00 PM ET)
- Volatility tracking per symbol
- Dynamic TTL calculation
- Price-change based refresh

**Cache TTL Logic:**
```python
# Crypto symbols (24/7)
if high_volatility:
    ttl = 10 seconds
else:
    ttl = 30 seconds

# Stock symbols
if market_hours:
    if high_volatility:
        ttl = 10 seconds
    else:
        ttl = 20 seconds
else:
    ttl = 5 minutes (300 seconds)
```

**Integration:**
- Integrated into `massive_source.py`
- Used in `signal_generation_service.py`
- Redis cache uses adaptive TTL

**Expected Impact:**
- Cache hit rate: 29% → >80% (3x improvement)
- API calls: 60%+ reduction
- Cost savings: Significant

---

## 2. Skip Unchanged Symbols

### Implementation

**File:** `argo/argo/core/signal_generation_service.py`

**Logic:**
```python
# Track last price
last_price = self._last_prices.get(symbol)

# Calculate price change
price_change = abs(current_price - last_price) / last_price

# Skip if change < threshold (0.5%)
if price_change < 0.005:
    return cached_signal  # Skip regeneration
```

**Features:**
- Tracks last price per symbol
- Calculates price change percentage
- Returns cached signal if unchanged
- Updates price tracking after generation

**Expected Impact:**
- CPU usage: 40-50% reduction
- Signal generation: 30-40% faster
- Only process symbols with meaningful changes

---

## 3. Redis Distributed Caching

### Implementation

**File:** `argo/argo/core/redis_cache.py`

**Features:**
- Persistent cache across restarts
- Shared cache across blue/green deployments
- In-memory fallback if Redis unavailable
- Automatic TTL management
- Pickle serialization for complex objects

**Usage:**
```python
from argo.core.redis_cache import get_redis_cache

cache = get_redis_cache()
value = cache.get('key')
cache.set('key', value, ttl=60)
```

**Integration:**
- Used in `massive_source.py` for price data
- Fallback to in-memory cache
- Automatic cleanup of expired entries

**Expected Impact:**
- Better cache persistence
- Shared cache across instances
- Faster recovery after restart

---

## 4. Rate Limiting

### Implementation

**File:** `argo/argo/core/rate_limiter.py`

**Algorithm:** Token Bucket

**Features:**
- Per-source rate limits
- Automatic request queuing
- Configurable limits
- Burst support

**Configuration:**
```python
# Per-source limits
massive: 5.0 req/s, burst=10
alpha_vantage: 0.2 req/s (5/min), burst=5
xai: 1.0 req/s, burst=5
sonar: 1.0 req/s, burst=5
```

**Usage:**
```python
from argo.core.rate_limiter import get_rate_limiter

limiter = get_rate_limiter()
await limiter.wait_for_permission('massive')
```

**Integration:**
- Integrated into `massive_source.py`
- Integrated into `alpha_vantage_source.py`
- Automatic queuing when rate limited

**Expected Impact:**
- Zero rate limit errors
- Better API utilization
- Predictable request patterns

---

## 5. Circuit Breaker Pattern

### Implementation

**File:** `argo/argo/core/circuit_breaker.py`

**States:**
- **CLOSED:** Normal operation
- **OPEN:** Failing, reject requests
- **HALF_OPEN:** Testing recovery

**Configuration:**
```python
CircuitBreakerConfig(
    failure_threshold=5,  # Open after 5 failures
    success_threshold=2,  # Close after 2 successes
    timeout=60.0  # Wait 60s before testing
)
```

**Usage:**
```python
from argo.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

breaker = CircuitBreaker('massive', CircuitBreakerConfig(...))
result = await breaker.call_async(fetch_function)
```

**Integration:**
- Integrated into `massive_source.py`
- Integrated into `alpha_vantage_source.py`
- Automatic state transitions

**Expected Impact:**
- Faster failure detection
- Automatic recovery
- Better resilience
- Prevents cascading failures

---

## 6. Priority-Based Processing

### Implementation

**File:** `argo/argo/core/signal_generation_service.py`

**Logic:**
```python
# Calculate volatility
volatility = calculate_volatility(symbol, price_history)

# Sort by volatility (high first)
sorted_symbols = sorted(symbols, key=get_volatility, reverse=True)

# Process high-volatility symbols first
for symbol in sorted_symbols:
    generate_signal(symbol)
```

**Features:**
- Tracks volatility per symbol
- Sorts symbols by volatility
- Processes high-volatility first
- Dynamic volatility calculation

**Expected Impact:**
- Better signal quality
- Faster response to market changes
- More efficient resource usage

---

## 7. Database Optimization

### Implementation

**File:** `argo/argo/core/signal_tracker.py`

**Indexes Added:**
```sql
-- Single-column indexes
CREATE INDEX idx_confidence ON signals(confidence);
CREATE INDEX idx_created_at ON signals(created_at);

-- Composite indexes
CREATE INDEX idx_symbol_timestamp ON signals(symbol, timestamp);
CREATE INDEX idx_symbol_outcome ON signals(symbol, outcome);
CREATE INDEX idx_timestamp_outcome ON signals(timestamp, outcome);
```

**Features:**
- Additional single-column indexes
- Composite indexes for common queries
- Optimized query patterns
- Better concurrent access

**Expected Impact:**
- Query time: 30-40% reduction
- Better concurrent access
- Faster signal retrieval

---

## 8. Performance Metrics

### Implementation

**File:** `argo/argo/core/performance_metrics.py`

**Tracked Metrics:**
- Signal generation time
- Cache hit/miss counts
- Skip rate (unchanged symbols)
- API latency per source
- Error counts
- Total symbols processed

**Usage:**
```python
from argo.core.performance_metrics import get_performance_metrics

metrics = get_performance_metrics()
metrics.record_signal_generation_time(0.25)
metrics.record_cache_hit()
summary = metrics.get_summary()
```

**Integration:**
- Integrated into `signal_generation_service.py`
- Exposed via `/api/v1/health` endpoint
- Prometheus metrics export

**Expected Impact:**
- Better observability
- Performance monitoring
- Optimization validation

---

## Performance Targets

### Before Optimizations

| Metric | Value |
|--------|-------|
| Signal Generation | ~0.72s |
| Cache Hit Rate | ~29% |
| API Calls/Cycle | ~36 |
| CPU Usage | Baseline |
| Memory Usage | Baseline |

### After Optimizations (Expected)

| Metric | Target | Improvement |
|--------|--------|-------------|
| Signal Generation | <0.3s | 60% faster |
| Cache Hit Rate | >80% | 3x improvement |
| API Calls/Cycle | <15 | 60% reduction |
| CPU Usage | -40-50% | 40-50% reduction |
| Memory Usage | -30% | 30% reduction |
| API Costs | -60-70% | 60-70% savings |

---

## Monitoring

### Performance Metrics Endpoint

**Endpoint:** `GET /api/v1/health`

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "performance": {
      "uptime_seconds": 3600,
      "avg_signal_generation_time": 0.25,
      "cache_hit_rate": 82.5,
      "skip_rate": 35.0,
      "total_cache_hits": 1000,
      "total_cache_misses": 250,
      "total_skipped_symbols": 350,
      "total_symbols_processed": 1000,
      "avg_api_latency": 0.15,
      "data_source_latencies": {
        "massive": 0.12,
        "alpha_vantage": 0.25
      }
    }
  }
}
```

### Prometheus Metrics

**Endpoint:** `GET /metrics`

**Metrics:**
- `argo_signal_generation_duration_seconds` - Signal generation time
- `argo_data_source_requests_total` - API requests
- `argo_data_source_status` - Data source health
- `argo_cache_hits_total` - Cache hits
- `argo_cache_misses_total` - Cache misses

---

## Configuration

### Cache Configuration

```python
# Base TTL
base_ttl = 10  # seconds

# Price change threshold
price_change_threshold = 0.005  # 0.5%

# Market hours
market_open = 9.5  # 9:30 AM ET
market_close = 16.0  # 4:00 PM ET
```

### Rate Limits

```python
# Per-source configuration
rate_limits = {
    'massive': RateLimitConfig(requests_per_second=5.0, burst_size=10),
    'alpha_vantage': RateLimitConfig(requests_per_second=0.2, burst_size=5),
    'xai': RateLimitConfig(requests_per_second=1.0, burst_size=5),
    'sonar': RateLimitConfig(requests_per_second=1.0, burst_size=5)
}
```

### Circuit Breaker

```python
# Per-source configuration
circuit_breaker_config = CircuitBreakerConfig(
    failure_threshold=5,
    success_threshold=2,
    timeout=60.0
)
```

---

## Troubleshooting

### Low Cache Hit Rate

**Symptoms:**
- Cache hit rate < 50%
- High API call volume
- Increased latency

**Diagnosis:**
1. Check Redis connection
2. Verify cache TTL settings
3. Check price change threshold
4. Monitor market hours detection

**Solutions:**
- Verify Redis is running and accessible
- Adjust TTL based on market conditions
- Lower price change threshold if needed
- Check market hours detection logic

### High API Latency

**Symptoms:**
- Slow signal generation
- Rate limit errors
- Circuit breaker opening

**Diagnosis:**
1. Check rate limiter configuration
2. Monitor circuit breaker state
3. Verify network connectivity
4. Check API provider status

**Solutions:**
- Adjust rate limits based on API provider limits
- Check circuit breaker logs for patterns
- Verify network connectivity
- Contact API provider if issues persist

### Signal Generation Slow

**Symptoms:**
- Signal generation time > 0.5s
- High CPU usage
- Slow response times

**Diagnosis:**
1. Check performance metrics
2. Monitor cache hit rate
3. Check skip rate
4. Verify database query time

**Solutions:**
- Review performance metrics for bottlenecks
- Improve cache hit rate (adjust TTL)
- Optimize database queries
- Check for resource constraints

---

## Best Practices

1. **Monitor Performance Metrics Regularly**
   - Check `/api/v1/health` daily
   - Track cache hit rates
   - Monitor API latency

2. **Optimize Cache Settings**
   - Adjust TTL based on market conditions
   - Monitor cache hit rates
   - Fine-tune price change threshold

3. **Configure Rate Limits Properly**
   - Set limits per API provider
   - Monitor rate limit errors
   - Adjust based on usage patterns

4. **Monitor Circuit Breakers**
   - Check circuit states regularly
   - Adjust thresholds based on failure patterns
   - Test recovery scenarios

5. **Database Optimization**
   - Monitor query performance
   - Add indexes as needed
   - Optimize batch inserts

---

## Future Enhancements

### Request Batching
- Batch multiple symbol requests where APIs support it
- Reduce connection overhead
- **Status:** Pending (requires API support analysis)

### Config Hot Reload
- Watch config files for changes
- Reload without restart
- **Status:** Pending

### Incremental Signal Updates
- Only update changed components
- Reduce computation
- **Status:** Pending

---

**See Also:**
- `SIGNAL_GENERATION_COMPLETE_GUIDE.md` - Signal generation details
- `SYSTEM_MONITORING_COMPLETE_GUIDE.md` - Monitoring setup
- `COMPLETE_SYSTEM_ARCHITECTURE.md` - Overall architecture

