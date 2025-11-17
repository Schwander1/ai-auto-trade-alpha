# Deployment Quick Reference - Performance Optimizations

**Quick Start Guide for Deploying All 5 Optimizations**

---

## 🚀 Quick Deployment

### Option 1: Automated Script
```bash
# Staging
./scripts/deploy-optimizations.sh staging

# Production
./scripts/deploy-optimizations.sh production
```

### Option 2: Manual Steps
```bash
# 1. Deploy services
./commands/deploy all to production

# 2. Setup Turbo cache
./scripts/setup-turbo-cache.sh vercel

# 3. Health checks
./commands/health check all production

# 4. Monitor
./commands/logs follow all production
```

---

## ⚡ Turbo Cache Setup

### Vercel (Recommended)
```bash
./scripts/setup-turbo-cache.sh vercel
# Or manually:
npx turbo login
npx turbo link
```

### Self-Hosted
```bash
./scripts/setup-turbo-cache.sh self-hosted
```

### S3
```bash
./scripts/setup-turbo-cache.sh s3
```

---

## 📊 Performance Monitoring

### Redis Cache
```bash
# Check cache stats
redis-cli INFO stats

# Monitor cache operations
redis-cli MONITOR

# Check cache keys
redis-cli KEYS cache:*
```

### API Performance
```bash
# Test pagination optimization
curl -H "Authorization: Bearer $TOKEN" \
  "https://your-domain.com/api/v1/signals/subscribed?limit=10&offset=0"

# Check response time (should be < 100ms for cached)
time curl ...
```

### Frontend Performance
```bash
# Build and check bundle size
cd alpine-frontend
npm run build
du -sh .next/static/chunks/*.js | sort -h

# Lighthouse audit
npm install -g @lhci/cli
lhci autorun --collect.url=http://localhost:3000
```

### Database Queries
```sql
-- Check slow queries
SELECT query, calls, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

---

## ✅ Verification Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Docker images built successfully
- [ ] Redis running in production
- [ ] Backup created

### Post-Deployment
- [ ] Health checks passing
- [ ] Cache hit rate > 75%
- [ ] API response times < 100ms (p95)
- [ ] No errors in logs
- [ ] Frontend bundle size reduced
- [ ] Build times improved

---

## 🔍 Troubleshooting

### Redis Not Working
```bash
# Check Redis is running
docker ps | grep redis

# Test connection
redis-cli ping

# Check environment variables
docker exec -it container env | grep REDIS
```

### Cache Not Hitting
```bash
# Check cache keys
redis-cli KEYS cache:*

# Check TTL
redis-cli TTL cache:signals:all:false

# Clear and retry
redis-cli FLUSHDB
```

### Slow Builds
```bash
# Check Turbo cache
npx turbo build --dry-run

# Clear cache and rebuild
rm -rf .turbo
pnpm build
```

---

## 📈 Success Metrics

| Metric | Target | How to Check |
|--------|--------|--------------|
| API Response (p95) | < 100ms | `time curl ...` |
| Cache Hit Rate | > 75% | `redis-cli INFO stats` |
| Bundle Size | < 1.5MB | `du -sh .next/static/chunks/*.js` |
| Build Time | < 2min | `time docker build ...` |
| Lighthouse Score | > 90 | `lhci autorun` |

---

## 🆘 Quick Rollback

```bash
# Rollback all
./commands/rollback all production

# Rollback specific service
./commands/rollback alpine production
./commands/rollback argo production
```

---

## 📚 Full Documentation

- **Complete Guide:** [DEPLOYMENT_GUIDE_OPTIMIZATIONS.md](./DEPLOYMENT_GUIDE_OPTIMIZATIONS.md)
- **Optimization Details:** [OPTIMIZATION_RECOMMENDATIONS.md](./OPTIMIZATION_RECOMMENDATIONS.md)
- **Implementation Summary:** [OPTIMIZATION_IMPLEMENTATION_SUMMARY.md](./OPTIMIZATION_IMPLEMENTATION_SUMMARY.md)
- **Commands Reference:** [../commands/README.md](../commands/README.md)

---

**Need Help?** Check the full deployment guide for detailed steps and troubleshooting.

