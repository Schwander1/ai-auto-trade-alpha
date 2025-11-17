# System Monitoring Complete Guide v3.0

**Date:** November 15, 2025  
**Version:** 3.0  
**Status:** ✅ Complete with Performance Metrics

---

## Overview

This guide covers comprehensive system monitoring, health checks, and performance metrics tracking for the Argo Trading Engine.

**v3.0 Updates:**
- Performance metrics integration
- Enhanced health endpoint
- Cache monitoring
- Rate limiter monitoring
- Circuit breaker monitoring

---

## Health Check Endpoints

### Primary Health Endpoint

**Endpoint:** `GET /api/v1/health`

**Response Structure:**
```json
{
  "status": "healthy",
  "version": "6.0",
  "timestamp": "2025-11-15T12:00:00Z",
  "uptime_seconds": 3600,
  "uptime_formatted": "1h 0m 0s",
  "services": {
    "api": "healthy",
    "database": "healthy",
    "redis": "healthy",
    "secrets": "healthy",
    "data_sources": {
      "total_sources": 6,
      "healthy": 5,
      "unhealthy": 0,
      "degraded": 1,
      "sources": {
        "massive": {
          "status": "healthy",
          "success_rate": 98.5,
          "avg_latency_ms": 120,
          "errors": 0
        }
      }
    },
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
      },
      "errors": {}
    }
  },
  "system": {
    "cpu_percent": 45.2,
    "memory_percent": 62.1,
    "disk_percent": 35.8
  }
}
```

### Prometheus Metrics

**Endpoint:** `GET /metrics`

**Key Metrics:**
- `argo_signal_generation_duration_seconds` - Signal generation time histogram
- `argo_data_source_requests_total` - Total API requests per source
- `argo_data_source_status` - Data source health status (1=healthy, 0=unhealthy)
- `argo_data_source_errors_total` - Total errors per source
- `argo_data_source_latency_seconds` - API latency per source
- `argo_cache_hits_total` - Total cache hits
- `argo_cache_misses_total` - Total cache misses
- `argo_skipped_symbols_total` - Total skipped symbols
- `argo_system_cpu_usage_percent` - CPU usage
- `argo_system_memory_usage_percent` - Memory usage
- `argo_system_disk_usage_percent` - Disk usage

---

## Performance Metrics

### Signal Generation Metrics

**Tracked:**
- Average signal generation time
- Signal generation time distribution
- Total signals generated
- Signals per symbol

**Monitoring:**
```bash
# Check average generation time
curl http://localhost:8000/api/v1/health | jq '.services.performance.avg_signal_generation_time'

# Target: <0.3s
```

### Cache Metrics

**Tracked:**
- Cache hit rate
- Total cache hits
- Total cache misses
- Cache TTL effectiveness

**Monitoring:**
```bash
# Check cache hit rate
curl http://localhost:8000/api/v1/health | jq '.services.performance.cache_hit_rate'

# Target: >80%
```

### Skip Rate Metrics

**Tracked:**
- Skip rate (unchanged symbols)
- Total skipped symbols
- Total symbols processed

**Monitoring:**
```bash
# Check skip rate
curl http://localhost:8000/api/v1/health | jq '.services.performance.skip_rate'

# Expected: 30-50% (good optimization)
```

### API Latency Metrics

**Tracked:**
- Average latency per data source
- Latency distribution
- Error rates per source

**Monitoring:**
```bash
# Check API latency
curl http://localhost:8000/api/v1/health | jq '.services.performance.data_source_latencies'

# Target: <200ms per source
```

---

## Data Source Health Monitoring

### Health Status

**Statuses:**
- **healthy:** Success rate >95%, latency <200ms
- **degraded:** Success rate 80-95%, or latency 200-500ms
- **unhealthy:** Success rate <80%, or latency >500ms

### Monitoring

**Check Data Source Health:**
```bash
curl http://localhost:8000/api/v1/health | jq '.services.data_sources'
```

**Key Metrics:**
- Success rate per source
- Average latency per source
- Error count per source
- Circuit breaker state

---

## Circuit Breaker Monitoring

### States

- **CLOSED:** Normal operation
- **OPEN:** Failing, rejecting requests
- **HALF_OPEN:** Testing recovery

### Monitoring

**Check Circuit Breaker State:**
- Monitor error rates
- Check for OPEN states
- Verify recovery (HALF_OPEN → CLOSED)

**Alerts:**
- Circuit breaker OPEN for >5 minutes
- Multiple circuit breakers OPEN
- Frequent state transitions

---

## Rate Limiter Monitoring

### Metrics

**Tracked:**
- Requests per second per source
- Queue depth
- Wait times
- Rate limit hits

### Monitoring

**Check Rate Limiter:**
- Monitor request rates
- Check for queuing
- Verify limits are appropriate

**Alerts:**
- High queue depth
- Frequent rate limit hits
- Inappropriate limits

---

## Grafana Dashboards

### Dashboard: Argo Trading Engine

**Panels:**
1. Signal Generation Performance
   - Average generation time
   - Generation time distribution
   - Signals generated per minute

2. Cache Performance
   - Cache hit rate
   - Cache hits vs misses
   - Cache TTL effectiveness

3. Data Source Health
   - Health status per source
   - Success rates
   - Latency per source

4. API Performance
   - API latency distribution
   - Error rates
   - Request rates

5. System Resources
   - CPU usage
   - Memory usage
   - Disk usage

6. Optimization Metrics
   - Skip rate
   - Cache hit rate
   - Performance improvements

---

## Alerting

### Critical Alerts

1. **Service Down**
   - Health endpoint unreachable
   - Status: unhealthy

2. **High Error Rate**
   - Error rate >10%
   - Multiple data sources failing

3. **Slow Signal Generation**
   - Average generation time >0.5s
   - P95 generation time >1.0s

4. **Low Cache Hit Rate**
   - Cache hit rate <50%
   - Significant API call increase

5. **Circuit Breaker OPEN**
   - Circuit breaker OPEN for >5 minutes
   - Multiple circuit breakers OPEN

### Warning Alerts

1. **Degraded Performance**
   - Generation time >0.3s
   - Cache hit rate <70%

2. **High Resource Usage**
   - CPU >80%
   - Memory >85%
   - Disk >90%

3. **Rate Limiting**
   - High queue depth
   - Frequent rate limit hits

---

## Monitoring Best Practices

1. **Regular Health Checks**
   - Check `/api/v1/health` every 5 minutes
   - Monitor Prometheus metrics continuously
   - Review Grafana dashboards daily

2. **Performance Monitoring**
   - Track signal generation time trends
   - Monitor cache hit rate trends
   - Watch for performance degradation

3. **Data Source Monitoring**
   - Monitor success rates
   - Track latency trends
   - Watch for circuit breaker states

4. **Optimization Validation**
   - Verify optimization improvements
   - Monitor skip rates
   - Track API call reductions

5. **Alert Response**
   - Respond to critical alerts immediately
   - Investigate warning alerts promptly
   - Document resolution steps

---

## Troubleshooting

### Low Cache Hit Rate

**Symptoms:**
- Cache hit rate <50%
- High API call volume

**Diagnosis:**
1. Check Redis connection
2. Verify cache TTL settings
3. Check price change threshold
4. Monitor market hours detection

**Solutions:**
- Verify Redis is running
- Adjust cache TTL
- Lower price change threshold
- Check market hours logic

### Slow Signal Generation

**Symptoms:**
- Generation time >0.5s
- High CPU usage

**Diagnosis:**
1. Check performance metrics
2. Monitor cache hit rate
3. Check skip rate
4. Verify database query time

**Solutions:**
- Review performance metrics
- Improve cache hit rate
- Optimize database queries
- Check for bottlenecks

### High API Latency

**Symptoms:**
- API latency >500ms
- Rate limit errors

**Diagnosis:**
1. Check rate limiter configuration
2. Monitor circuit breaker state
3. Verify network connectivity
4. Check API provider status

**Solutions:**
- Adjust rate limits
- Check circuit breaker logs
- Verify network
- Contact API provider

---

**See Also:**
- `PERFORMANCE_OPTIMIZATIONS.md` - Optimization details
- `SIGNAL_GENERATION_COMPLETE_GUIDE.md` - Signal generation
- `COMPLETE_SYSTEM_ARCHITECTURE.md` - System architecture

