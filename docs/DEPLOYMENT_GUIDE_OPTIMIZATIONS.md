# Complete Deployment Guide - Performance Optimizations

**Date:** January 2025  
**Status:** Ready for Deployment  
**Version:** 1.0

---

## Overview

This guide covers the complete deployment process for the 5 performance optimizations, including staging testing, Turbo cache setup, performance monitoring, and production deployment.

---

## 📋 Pre-Deployment Checklist

### Code Quality ✅
- [x] All optimizations implemented
- [x] No linting errors
- [x] All files accepted by user
- [x] Backward compatible changes
- [ ] All tests passing (run before deployment)

### Environment Configuration
- [ ] Redis is running in production
- [ ] Environment variables configured
- [ ] Database migrations ready (if any)
- [ ] Docker images built and tested locally

### Infrastructure Readiness
- [ ] Production servers accessible
- [ ] SSH keys configured
- [ ] Backup of current production state
- [ ] Rollback plan documented

---

## 🧪 Phase 1: Staging Environment Testing

### Step 1.1: Setup Staging Environment

**For Alpine Backend:**
```bash
# Connect to production server (staging uses same server, different port)
ssh root@91.98.153.49

# Navigate to staging directory (or create if needed)
cd /root/alpine-staging  # or use blue/green inactive environment

# Ensure Redis is running
docker ps | grep redis
# If not running:
docker-compose -f docker-compose.production.yml up -d redis
```

**For Argo:**
```bash
# Connect to Argo production server
ssh root@178.156.194.174

# Use inactive blue/green environment for staging
cd /root/argo-production-green  # or blue, whichever is inactive
```

### Step 1.2: Deploy to Staging

**Option A: Use Existing Blue-Green Inactive Environment**
```bash
# Alpine: Deploy to inactive environment (port 8002/3002)
cd /path/to/workspace
./commands/deploy alpine to production
# This will deploy to inactive environment first

# Argo: Deploy to inactive environment (port 8001)
./commands/deploy argo to production
```

**Option B: Manual Staging Deployment**
```bash
# Build Docker images locally first
cd alpine-backend
docker build -t alpine-backend:optimized -f backend/Dockerfile backend/
docker build -t alpine-frontend:optimized -f frontend/Dockerfile frontend/

# Test locally
docker-compose -f docker-compose.local.yml up -d
```

### Step 1.3: Run Staging Tests

**Test 1: Pagination Optimization**
```bash
# Test signals endpoint with various offsets
curl -H "Authorization: Bearer $TOKEN" \
  "http://staging-server:8001/api/v1/signals/subscribed?limit=10&offset=0"
curl -H "Authorization: Bearer $TOKEN" \
  "http://staging-server:8001/api/v1/signals/subscribed?limit=10&offset=100"

# Verify:
# - Response times < 100ms for cached requests
# - Cache hit rate improves on subsequent requests
# - No errors with high offsets
```

**Test 2: Docker Build Optimization**
```bash
# Test build time
time docker build -t alpine-backend:test -f backend/Dockerfile backend/

# Verify:
# - Build time reduced by 40-60% on second build (with cache)
# - Dependencies only rebuild when requirements.txt changes
```

**Test 3: Frontend Lazy Loading**
```bash
# Start frontend
cd alpine-frontend
npm run build
npm start

# Test in browser:
# - Open DevTools Network tab
# - Load home page
# - Verify initial bundle size reduced
# - Verify components load on scroll (lazy loading)
# - Check Lighthouse score > 90
```

**Test 4: Database Query Optimization**
```bash
# Test admin endpoints
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://staging-server:8001/api/v1/admin/users?limit=20"

# Monitor Redis cache
redis-cli
> KEYS cache:*
> GET cache:admin:users:*

# Verify:
# - Query times reduced
# - Cache hits occurring
# - Count queries optimized
```

**Test 5: Turbo Remote Cache (Local)**
```bash
# Test local Turbo cache
cd /path/to/workspace
pnpm build

# Second build should be faster
pnpm build

# Verify:
# - Second build uses cache
# - Build artifacts cached
```

### Step 1.4: Performance Baseline Metrics

**Capture baseline metrics before optimization:**
```bash
# API Response Times
curl -w "@curl-format.txt" -o /dev/null -s \
  "http://staging-server:8001/api/v1/signals/subscribed?limit=10&offset=0"

# Create curl-format.txt:
cat > curl-format.txt << EOF
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
EOF

# Database Query Times
# Connect to database and run:
EXPLAIN ANALYZE SELECT COUNT(*) FROM users WHERE tier = 'pro';

# Frontend Bundle Size
cd alpine-frontend
npm run build
du -sh .next/static/chunks/*.js | sort -h
```

**Document Results:**
- API response times (p50, p95, p99)
- Database query execution times
- Frontend bundle sizes
- Docker build times
- Cache hit rates (if Redis already in use)

---

## ⚡ Phase 2: Configure Turbo Remote Cache

### Step 2.1: Choose Cache Backend

**Option A: Vercel Remote Cache (Recommended - Easiest)**

```bash
# Install Turbo CLI globally (if not already installed)
npm install -g turbo

# Login to Vercel
npx turbo login

# Link to Vercel team/organization
npx turbo link

# Verify connection
npx turbo build --dry-run
```

**Configuration:**
- Cache is automatically configured after linking
- No additional setup required
- Free tier available for small teams

**Option B: Self-Hosted Remote Cache**

```bash
# Run Turbo cache server in Docker
docker run -d \
  --name turbo-cache \
  -p 8080:8080 \
  -e TURBO_TOKEN=your-secret-token \
  vercel/turborepo-remote-cache

# Configure in environment
export TURBO_REMOTE_CACHE_URL=http://your-server:8080
export TURBO_TEAM=your-team
export TURBO_TOKEN=your-secret-token
```

**Option C: S3-Based Remote Cache (AWS)**

```bash
# Create S3 bucket
aws s3 mb s3://your-turbo-cache-bucket

# Configure environment
export TURBO_REMOTE_CACHE_URL=s3://your-turbo-cache-bucket/turbo-cache
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_REGION=us-east-1
```

### Step 2.2: Test Turbo Cache

```bash
# First build (will populate cache)
cd /path/to/workspace
pnpm build

# Second build (should use cache)
pnpm build

# Verify cache usage
# Look for "FULL TURBO" in build output
# Build time should be significantly reduced
```

### Step 2.3: CI/CD Integration

**For GitHub Actions:**
```yaml
# .github/workflows/ci.yml
- name: Setup Turbo
  run: |
    npm install -g turbo
    npx turbo login
    npx turbo link

- name: Build
  run: turbo run build
  env:
    TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
    TURBO_TEAM: ${{ secrets.TURBO_TEAM }}
```

**Add secrets to GitHub:**
- `TURBO_TOKEN`: From `npx turbo login`
- `TURBO_TEAM`: Your Vercel team name

---

## 📊 Phase 3: Setup Performance Monitoring

### Step 3.1: Redis Cache Monitoring

**Install Redis monitoring tools:**
```bash
# On production server
docker exec -it redis redis-cli

# Monitor cache operations
MONITOR

# Check cache stats
INFO stats

# Check memory usage
INFO memory

# List all cache keys
KEYS cache:*

# Check specific cache key
GET cache:signals:all:false
TTL cache:signals:all:false
```

**Create monitoring script:**
```bash
# scripts/monitor-redis-cache.sh
#!/bin/bash
redis-cli INFO stats | grep -E "keyspace_hits|keyspace_misses"
redis-cli INFO memory | grep used_memory_human
redis-cli DBSIZE
```

### Step 3.2: API Performance Monitoring

**Add Prometheus metrics (if not already configured):**

```python
# alpine-backend/backend/core/metrics.py (if exists)
from prometheus_client import Counter, Histogram, Gauge

# Cache metrics
cache_hits = Counter('cache_hits_total', 'Total cache hits', ['endpoint'])
cache_misses = Counter('cache_misses_total', 'Total cache misses', ['endpoint'])
cache_hit_rate = Gauge('cache_hit_rate', 'Cache hit rate', ['endpoint'])

# API response time metrics
api_response_time = Histogram(
    'api_response_time_seconds',
    'API response time',
    ['endpoint', 'method', 'status']
)
```

**Query Prometheus:**
```promql
# Cache hit rate
rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))

# API response times
histogram_quantile(0.95, api_response_time_seconds_bucket)

# Database query times
histogram_quantile(0.95, db_query_duration_seconds_bucket)
```

### Step 3.3: Database Query Monitoring

**Enable PostgreSQL query logging:**
```sql
-- On production database
ALTER DATABASE your_db SET log_min_duration_statement = 100; -- Log queries > 100ms
ALTER DATABASE your_db SET log_statement = 'all'; -- For detailed analysis
```

**Monitor slow queries:**
```bash
# View PostgreSQL logs
tail -f /var/log/postgresql/postgresql-*.log | grep "duration:"

# Or use pg_stat_statements extension
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Step 3.4: Frontend Performance Monitoring

**Lighthouse CI Setup:**
```bash
# Install Lighthouse CI
npm install -g @lhci/cli

# Run Lighthouse audit
lhci autorun --collect.url=http://localhost:3000

# Configure in CI/CD
# .github/workflows/lighthouse.yml
```

**Web Vitals Monitoring:**
```typescript
// alpine-frontend/lib/analytics.ts
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

function sendToAnalytics(metric) {
  // Send to your analytics service
  fetch('/api/analytics', {
    method: 'POST',
    body: JSON.stringify(metric)
  })
}

getCLS(sendToAnalytics)
getFID(sendToAnalytics)
getFCP(sendToAnalytics)
getLCP(sendToAnalytics)
getTTFB(sendToAnalytics)
```

### Step 3.5: Docker Build Monitoring

**Track build times:**
```bash
# scripts/track-build-time.sh
#!/bin/bash
START_TIME=$(date +%s)
docker build -t alpine-backend:test -f backend/Dockerfile backend/
END_TIME=$(date +%s)
BUILD_TIME=$((END_TIME - START_TIME))
echo "Build time: ${BUILD_TIME}s"
# Log to monitoring system
```

---

## 🚀 Phase 4: Production Deployment

### Step 4.1: Pre-Deployment Validation

```bash
# 1. Verify all changes committed
git status

# 2. Run final tests
cd alpine-backend
pytest tests/  # If tests exist

cd ../alpine-frontend
npm test  # If tests exist

# 3. Build Docker images locally
cd ../alpine-backend
docker build -t alpine-backend:production -f backend/Dockerfile backend/

cd ../alpine-frontend
docker build -t alpine-frontend:production -f frontend/Dockerfile frontend/

# 4. Verify Docker images
docker images | grep -E "alpine-backend|alpine-frontend"
```

### Step 4.2: Backup Current Production

```bash
# Backup database
ssh root@91.98.153.49
pg_dump -U postgres your_db > /root/backups/pre-optimization-$(date +%Y%m%d).sql

# Backup current code
cd /root/alpine-production-blue
tar -czf /root/backups/pre-optimization-code-$(date +%Y%m%d).tar.gz .

# Backup Redis data (if persistent)
redis-cli SAVE
cp /var/lib/redis/dump.rdb /root/backups/pre-optimization-redis-$(date +%Y%m%d).rdb
```

### Step 4.3: Deploy Alpine Backend

```bash
# From local machine
cd /path/to/workspace

# Deploy using blue-green deployment
./commands/deploy alpine to production

# Monitor deployment
./commands/logs follow alpine production

# In another terminal, check health
./commands/health check alpine production
```

**Manual deployment steps (if needed):**
```bash
# SSH to production server
ssh root@91.98.153.49

# Navigate to inactive environment (blue or green)
cd /root/alpine-production-green  # or blue

# Pull latest code
git pull origin main  # or your branch

# Rebuild Docker images
docker-compose -f docker-compose.production.yml build

# Start services (on inactive ports)
docker-compose -f docker-compose.production.yml up -d

# Run health checks
curl http://localhost:8002/health
curl http://localhost:3002/health

# If health checks pass, switch traffic (update nginx config)
# Then stop old environment
cd /root/alpine-production-blue
docker-compose -f docker-compose.production.yml down
```

### Step 4.4: Deploy Argo Backend

```bash
# From local machine
./commands/deploy argo to production

# Monitor deployment
./commands/logs follow argo production

# Check health
./commands/health check argo production
```

### Step 4.5: Verify Redis Configuration

```bash
# SSH to production server
ssh root@91.98.153.49

# Check Redis is running
docker ps | grep redis

# Test Redis connection from backend
docker exec -it alpine-backend-backend-1 python -c "
from backend.core.cache import redis_client
if redis_client:
    redis_client.ping()
    print('Redis connected')
else:
    print('Redis not configured')
"

# Verify Redis environment variables
docker exec -it alpine-backend-backend-1 env | grep REDIS
```

### Step 4.6: Verify All Optimizations

**Test 1: Pagination Cache**
```bash
# First request (cache miss)
time curl -H "Authorization: Bearer $TOKEN" \
  "https://your-domain.com/api/v1/signals/subscribed?limit=10&offset=0"

# Second request (cache hit - should be faster)
time curl -H "Authorization: Bearer $TOKEN" \
  "https://your-domain.com/api/v1/signals/subscribed?limit=10&offset=0"

# Check Redis
redis-cli GET "cache:signals:all:false"
```

**Test 2: Frontend Lazy Loading**
```bash
# Open browser DevTools
# Network tab -> Disable cache
# Load home page
# Verify:
# - Initial bundle smaller
# - Components load on scroll
# - Lighthouse score > 90
```

**Test 3: Database Query Optimization**
```bash
# Test admin endpoint
time curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "https://your-domain.com/api/v1/admin/users?limit=20"

# Check cache
redis-cli KEYS "cache:admin:*"
```

---

## ✅ Phase 5: Post-Deployment Validation

### Step 5.1: Health Checks

```bash
# Comprehensive health check
./commands/health check all production

# Individual service checks
curl https://your-domain.com/health
curl https://your-domain.com/api/health
curl https://api.argo.com/health
```

### Step 5.2: Performance Metrics Comparison

**Compare with baseline metrics:**

```bash
# API Response Times
# Before: ~150ms (p95)
# After: Target < 100ms (p95)

# Database Query Times
# Before: ~50ms average
# After: Target < 30ms average

# Frontend Bundle Size
# Before: ~2.5MB initial
# After: Target < 1.5MB initial

# Docker Build Time
# Before: ~5 minutes
# After: Target < 2 minutes (with cache)
```

### Step 5.3: Monitor for Issues

**Watch logs for 30 minutes:**
```bash
# Follow all logs
./commands/logs follow all production

# Watch for:
# - Cache errors
# - Database connection issues
# - Redis connection failures
# - API errors
# - Performance degradation
```

**Monitor metrics:**
```bash
# Cache hit rate (should be > 75%)
redis-cli INFO stats | grep keyspace_hits

# API error rate (should be < 1%)
# Check Prometheus/Grafana dashboards

# Database connection pool (should be healthy)
# Check database monitoring
```

### Step 5.4: User Acceptance Testing

**Test critical user flows:**
1. User login/authentication
2. Signal subscription and viewing
3. Dashboard loading
4. Admin panel access
5. API pagination
6. Frontend navigation

---

## 🔄 Phase 6: Rollback Plan (If Needed)

### Quick Rollback

```bash
# Rollback Alpine
./commands/rollback alpine production

# Rollback Argo
./commands/rollback argo production

# Rollback All
./commands/rollback all production
```

### Manual Rollback Steps

```bash
# 1. Stop new environment
cd /root/alpine-production-green
docker-compose -f docker-compose.production.yml down

# 2. Switch traffic back to old environment
# Update nginx config to point to old environment

# 3. Restart old environment
cd /root/alpine-production-blue
docker-compose -f docker-compose.production.yml up -d

# 4. Verify health
./commands/health check alpine production
```

### Database Rollback (If Needed)

```bash
# Restore database backup
psql -U postgres your_db < /root/backups/pre-optimization-YYYYMMDD.sql
```

---

## 📈 Phase 7: Ongoing Monitoring

### Daily Checks (First Week)

```bash
# Morning checks
./commands/health check all production
./commands/status check all production

# Check cache hit rates
redis-cli INFO stats

# Check error logs
./commands/logs view all production | grep -i error
```

### Weekly Reviews

1. **Performance Metrics:**
   - API response times (p50, p95, p99)
   - Cache hit rates
   - Database query times
   - Frontend bundle sizes
   - Build times

2. **Error Analysis:**
   - Review error logs
   - Check for cache failures
   - Monitor database connection issues

3. **Optimization Opportunities:**
   - Identify slow endpoints
   - Find cache misses
   - Optimize database queries

### Monthly Optimization Review

1. Review all performance metrics
2. Identify new optimization opportunities
3. Update cache TTLs if needed
4. Optimize database indexes
5. Review and update Docker images

---

## 🎯 Success Criteria

### Performance Targets

- ✅ **API Response Times:**
  - Simple GET: < 100ms (p95)
  - Complex GET: < 500ms (p95)
  - POST/PUT: < 200ms (p95)

- ✅ **Cache Hit Rates:**
  - Signals endpoint: > 80%
  - Admin endpoints: > 75%
  - User endpoints: > 70%

- ✅ **Frontend Performance:**
  - Initial bundle: < 1.5MB
  - Time to Interactive: < 3.5s
  - Lighthouse Score: > 90

- ✅ **Build Performance:**
  - Docker build: < 2 minutes (with cache)
  - Turbo build: < 1 minute (with cache)

- ✅ **Database Performance:**
  - Query times: < 30ms average
  - Connection pool: Healthy utilization

---

## 📝 Deployment Checklist

### Pre-Deployment
- [ ] All code reviewed and approved
- [ ] Tests passing
- [ ] Staging environment tested
- [ ] Performance baselines captured
- [ ] Backup created
- [ ] Rollback plan ready

### Deployment
- [ ] Turbo cache configured
- [ ] Redis running and accessible
- [ ] Docker images built
- [ ] Services deployed
- [ ] Health checks passing
- [ ] Performance metrics verified

### Post-Deployment
- [ ] All endpoints responding
- [ ] Cache working correctly
- [ ] No errors in logs
- [ ] Performance targets met
- [ ] User acceptance testing passed
- [ ] Monitoring configured

---

## 🆘 Troubleshooting

### Redis Connection Issues

```bash
# Check Redis is running
docker ps | grep redis

# Test connection
redis-cli ping

# Check environment variables
docker exec -it container env | grep REDIS

# Restart Redis
docker-compose restart redis
```

### Cache Not Working

```bash
# Check Redis connection from app
docker exec -it container python -c "from backend.core.cache import redis_client; print(redis_client.ping() if redis_client else 'None')"

# Check cache keys
redis-cli KEYS cache:*

# Clear cache if needed
redis-cli FLUSHDB
```

### Slow API Responses

```bash
# Check database queries
# Enable query logging
# Review slow query log

# Check cache hit rate
redis-cli INFO stats

# Check connection pool
# Review database connection metrics
```

### Frontend Build Issues

```bash
# Clear Next.js cache
rm -rf alpine-frontend/.next

# Clear node_modules
rm -rf alpine-frontend/node_modules
npm install

# Rebuild
npm run build
```

---

## 📚 Additional Resources

- [Optimization Recommendations](./OPTIMIZATION_RECOMMENDATIONS.md)
- [Implementation Summary](./OPTIMIZATION_IMPLEMENTATION_SUMMARY.md)
- [Deployment Commands](../commands/README.md)
- [Performance Rules](../Rules/28_PERFORMANCE.md)
- [Deployment Rules](../Rules/04_DEPLOYMENT.md)

---

**Ready for Deployment!** 🚀

Follow this guide step-by-step for a safe, monitored deployment of all optimizations.

