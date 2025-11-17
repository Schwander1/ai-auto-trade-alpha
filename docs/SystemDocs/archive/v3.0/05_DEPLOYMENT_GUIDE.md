# Deployment Guide v3.0

**Date:** November 15, 2025  
**Version:** 3.0  
**Status:** ✅ Complete with Optimizations

---

## Overview

This guide covers deployment procedures for the Argo Trading Engine with all v3.0 optimizations.

**v3.0 Updates:**
- New optimization modules deployment
- Redis cache setup
- Performance metrics verification
- Enhanced health checks

---

## Pre-Deployment Checklist

### 1. Code Verification

- [ ] All optimization modules present
- [ ] No linting errors
- [ ] Tests passing
- [ ] Configuration updated

### 2. Dependencies

- [ ] Redis installed and running
- [ ] Python dependencies updated
- [ ] All new modules importable

### 3. Configuration

- [ ] Redis connection configured
- [ ] Rate limits configured
- [ ] Circuit breaker thresholds set
- [ ] Cache TTL settings reviewed

---

## Deployment Process

### Step 1: Backup Current Deployment

```bash
# Backup current deployment
ssh root@178.156.194.174
cd /root/argo-production-blue
tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz .
```

### Step 2: Deploy Code

```bash
# Use deployment script
./commands/deploy argo to production
```

**Or manually:**
```bash
# Deploy to green environment
rsync -avz --exclude-from=.deployignore \
  argo/ root@178.156.194.174:/root/argo-production-green/
```

### Step 3: Install Dependencies

```bash
ssh root@178.156.194.174
cd /root/argo-production-green
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Verify New Modules

```bash
# Test imports
python -c "from argo.core.adaptive_cache import AdaptiveCache"
python -c "from argo.core.rate_limiter import get_rate_limiter"
python -c "from argo.core.circuit_breaker import CircuitBreaker"
python -c "from argo.core.redis_cache import get_redis_cache"
python -c "from argo.core.performance_metrics import get_performance_metrics"
```

### Step 5: Start Service

```bash
cd /root/argo-production-green
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8001 > /tmp/argo-green.log 2>&1 &
```

### Step 6: Health Checks

```bash
# Level 3 comprehensive health check
curl http://178.156.194.174:8001/api/v1/health | jq

# Verify performance metrics
curl http://178.156.194.174:8001/api/v1/health | jq '.services.performance'

# Check Prometheus metrics
curl http://178.156.194.174:8001/metrics | grep argo
```

### Step 7: Switch Traffic

```bash
# Switch Nginx to green (if applicable)
# Or update port mapping
```

### Step 8: Monitor

```bash
# Monitor logs
tail -f /tmp/argo-green.log

# Monitor performance
watch -n 5 'curl -s http://178.156.194.174:8001/api/v1/health | jq .services.performance'
```

---

## Post-Deployment Verification

### Performance Metrics

**Check:**
1. Signal generation time <0.3s
2. Cache hit rate >80%
3. Skip rate 30-50%
4. API latency <200ms

**Commands:**
```bash
# Check performance
curl http://178.156.194.174:8001/api/v1/health | jq '.services.performance'
```

### Data Source Health

**Check:**
1. All sources healthy
2. Success rates >95%
3. Latency <200ms
4. No circuit breakers OPEN

**Commands:**
```bash
# Check data sources
curl http://178.156.194.174:8001/api/v1/health | jq '.services.data_sources'
```

### Cache Verification

**Check:**
1. Redis connection working
2. Cache hits increasing
3. Cache TTL working
4. Adaptive cache functioning

**Commands:**
```bash
# Check Redis
redis-cli ping

# Check cache keys
redis-cli keys "massive:price:*"
```

---

## Rollback Procedure

### If Issues Detected

```bash
# Stop green service
pkill -f "uvicorn.*8001"

# Switch back to blue
# Or restore from backup
cd /root/argo-production-blue
# Restart service
```

---

## Configuration Updates

### Redis Configuration

**Required:**
- Redis host/port configured
- Redis password (if applicable)
- Redis DB number

**Check:**
```bash
# In config or environment
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=...
REDIS_DB=0
```

### Rate Limits

**Configuration:**
```python
# In rate_limiter.py or config
rate_limits = {
    'massive': 5.0 req/s,
    'alpha_vantage': 0.2 req/s,
    'xai': 1.0 req/s,
    'sonar': 1.0 req/s
}
```

### Circuit Breaker

**Configuration:**
```python
# In circuit_breaker.py or config
failure_threshold = 5
success_threshold = 2
timeout = 60.0
```

---

## Troubleshooting

### Module Import Errors

**Error:** `ModuleNotFoundError: No module named 'argo.core.adaptive_cache'`

**Solution:**
```bash
# Verify module exists
ls -la argo/argo/core/adaptive_cache.py

# Reinstall dependencies
pip install -r requirements.txt
```

### Redis Connection Errors

**Error:** `Redis connection failed`

**Solution:**
```bash
# Check Redis is running
redis-cli ping

# Verify configuration
echo $REDIS_HOST
echo $REDIS_PORT
```

### Performance Not Improved

**Symptoms:**
- Cache hit rate still low
- Signal generation still slow

**Diagnosis:**
1. Check Redis connection
2. Verify cache is being used
3. Check skip logic is working
4. Monitor performance metrics

**Solutions:**
- Verify Redis is accessible
- Check cache keys in Redis
- Verify price tracking
- Review performance metrics

---

## Best Practices

1. **Always Backup Before Deployment**
   - Backup current deployment
   - Keep backups for 7 days

2. **Deploy to Inactive Environment First**
   - Use blue/green deployment
   - Test thoroughly before switching

3. **Monitor Performance Metrics**
   - Check metrics immediately after deployment
   - Monitor for 1 hour minimum
   - Verify improvements

4. **Verify All Modules**
   - Test imports
   - Verify configuration
   - Check connections

5. **Have Rollback Plan Ready**
   - Know rollback procedure
   - Test rollback process
   - Keep backups accessible

---

**See Also:**
- `ARGO_BLUE_GREEN_DEPLOYMENT_GUIDE.md` - Blue/green deployment
- `PERFORMANCE_OPTIMIZATIONS.md` - Optimization details
- `SYSTEM_MONITORING_COMPLETE_GUIDE.md` - Monitoring setup

