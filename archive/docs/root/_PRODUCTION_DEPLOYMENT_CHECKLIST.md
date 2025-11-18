# Production Deployment Checklist

**Date:** 2025-01-27  
**Purpose:** Ensure all health check improvements are properly deployed to production

---

## Pre-Deployment Checklist

### Code Changes
- [x] All health check improvements implemented
- [x] Database connectivity check added to Argo
- [x] Timeout handling added to all endpoints
- [x] System metrics added to Alpine Backend
- [x] Uptime tracking added to Alpine Backend
- [x] Frontend health endpoints created
- [x] Readiness/liveness endpoints added to all services
- [x] Error handling improved across all endpoints

### Configuration Files
- [x] Prometheus configuration updated with health check monitoring
- [x] Alert rules added for health check failures
- [x] Docker Compose health probes configured
- [x] Health check scripts updated

### Documentation
- [x] API documentation created
- [x] Implementation summary created
- [x] Deployment verification script created

---

## Deployment Steps

### 1. Deploy Code Changes

#### Argo Service
```bash
# Option 1: Blue-Green Deployment (Recommended)
./scripts/deploy-argo-blue-green.sh

# Option 2: Direct Deployment
./scripts/deploy-argo.sh

# Option 3: Using deployment command
./commands/deploy argo to production
```

**Verification:**
- [ ] Code deployed to production server
- [ ] Service restarted
- [ ] Health endpoints accessible

#### Alpine Backend Service
```bash
# Option 1: Blue-Green Deployment (Recommended)
./scripts/deploy-alpine.sh

# Option 2: Using deployment command
./commands/deploy alpine to production
```

**Verification:**
- [ ] Code deployed to production server
- [ ] Docker containers restarted
- [ ] Health endpoints accessible

#### Alpine Frontend Service
```bash
# Deploy frontend (if separate deployment)
cd alpine-frontend
npm run build
# Deploy to hosting platform (Vercel, etc.)
```

**Verification:**
- [ ] Frontend deployed
- [ ] Health endpoints accessible

---

### 2. Update Monitoring Configuration

#### Prometheus Configuration
```bash
# Copy updated Prometheus config to production
scp infrastructure/monitoring/prometheus.yml root@<monitoring-server>:/etc/prometheus/prometheus.yml

# Restart Prometheus
ssh root@<monitoring-server> "systemctl restart prometheus"
# OR if using Docker:
ssh root@<monitoring-server> "docker restart prometheus"
```

**Verification:**
- [ ] Prometheus configuration updated
- [ ] Prometheus restarted
- [ ] Health check targets visible in Prometheus UI
- [ ] Health check metrics being collected

#### Alert Configuration
```bash
# Copy updated alert rules to production
scp infrastructure/monitoring/alerts.yml root@<monitoring-server>:/etc/prometheus/alerts.yml

# Reload Prometheus configuration
ssh root@<monitoring-server> "curl -X POST http://localhost:9090/-/reload"
```

**Verification:**
- [ ] Alert rules updated
- [ ] Prometheus configuration reloaded
- [ ] Alert rules visible in Prometheus UI
- [ ] Test alerts can be triggered

---

### 3. Update Docker Health Probes

#### Argo Service
The health probe is already configured in `argo/docker-compose.yml`. If using Docker Compose:

```bash
# Restart Argo service to apply health probe changes
ssh root@178.156.194.174 "cd /root/argo-production && docker-compose restart argo-api"
```

**Verification:**
- [ ] Docker health probe using readiness endpoint
- [ ] Health checks running in Docker
- [ ] Container health status visible

#### Alpine Backend Service
The health probes are already configured in `alpine-backend/docker-compose.production.yml`. If using Docker Compose:

```bash
# Restart Alpine backend services to apply health probe changes
ssh root@91.98.153.49 "cd /root/alpine-production && docker-compose -f docker-compose.production.yml restart"
```

**Verification:**
- [ ] All backend instances using readiness endpoint
- [ ] Health checks running in Docker
- [ ] Container health status visible

---

### 4. Verify Deployment

#### Run Verification Script
```bash
./scripts/verify_production_deployment.sh
```

**Expected Output:**
- ✅ All health endpoints responding
- ✅ Database checks working
- ✅ System metrics included
- ✅ Uptime tracking working
- ✅ Readiness/liveness probes working
- ✅ Configuration files updated

#### Manual Verification

**Argo Service:**
```bash
# Comprehensive health check
curl http://178.156.194.174:8000/api/v1/health | jq

# Readiness probe
curl http://178.156.194.174:8000/api/v1/health/readiness | jq

# Liveness probe
curl http://178.156.194.174:8000/api/v1/health/liveness | jq
```

**Alpine Backend:**
```bash
# Comprehensive health check
curl http://91.98.153.49:8001/health | jq

# Readiness probe
curl http://91.98.153.49:8001/health/readiness | jq

# Liveness probe
curl http://91.98.153.49:8001/health/liveness | jq
```

**Alpine Frontend:**
```bash
# Health check
curl http://91.98.153.49:3000/api/health | jq

# Readiness probe
curl http://91.98.153.49:3000/api/health/readiness | jq

# Liveness probe
curl http://91.98.153.49:3000/api/health/liveness | jq
```

---

### 5. Update Monitoring Dashboards

#### Grafana Dashboards
1. **Add Health Check Panels:**
   - Health check success rate
   - Health check duration
   - Service status (healthy/degraded/unhealthy)
   - Dependency status

2. **Add Alert Panels:**
   - Health check failures
   - Readiness check failures
   - Liveness check failures

3. **Update Existing Dashboards:**
   - Add health check metrics to service dashboards
   - Add dependency health indicators

**Verification:**
- [ ] Dashboards updated
- [ ] Health check metrics visible
- [ ] Alerts configured in Grafana

---

### 6. Test Monitoring and Alerting

#### Test Health Check Monitoring
```bash
# Check Prometheus targets
curl http://<prometheus-server>:9090/api/v1/targets | jq '.data.activeTargets[] | select(.job=="health-checks")'

# Check health check metrics
curl http://<prometheus-server>:9090/api/v1/query?query=probe_success{job="health-checks"} | jq
```

#### Test Alerts
1. **Simulate Health Check Failure:**
   - Temporarily stop a service
   - Verify alert triggers
   - Restore service
   - Verify alert resolves

2. **Verify Alert Notifications:**
   - Check Alertmanager for alerts
   - Verify notifications sent (email, Slack, PagerDuty, etc.)

**Verification:**
- [ ] Health checks monitored in Prometheus
- [ ] Alerts trigger correctly
- [ ] Notifications sent correctly
- [ ] Alerts resolve when issues fixed

---

## Post-Deployment Verification

### Immediate (Within 5 minutes)
- [ ] All health endpoints responding
- [ ] Database checks working
- [ ] System metrics included
- [ ] Uptime tracking working
- [ ] Readiness/liveness probes working
- [ ] No errors in service logs

### Extended (Within 15 minutes)
- [ ] Prometheus collecting health check metrics
- [ ] Grafana dashboards showing health data
- [ ] No false alerts triggered
- [ ] All services stable
- [ ] Performance metrics normal

### Ongoing (Within 1 hour)
- [ ] Health check metrics trending normally
- [ ] No degradation in service health
- [ ] Alert rules working correctly
- [ ] Monitoring dashboards accurate
- [ ] Documentation updated

---

## Rollback Plan

If deployment issues occur:

### Rollback Code Changes
```bash
# Argo
ssh root@178.156.194.174 "cd /root/argo-production && git checkout <previous-commit> && docker-compose restart"

# Alpine Backend
ssh root@91.98.153.49 "cd /root/alpine-production && git checkout <previous-commit> && docker-compose -f docker-compose.production.yml restart"
```

### Rollback Monitoring Configuration
```bash
# Restore previous Prometheus config
scp infrastructure/monitoring/prometheus.yml.backup root@<monitoring-server>:/etc/prometheus/prometheus.yml

# Restart Prometheus
ssh root@<monitoring-server> "systemctl restart prometheus"
```

---

## Production URLs

### Argo Service
- **Health:** http://178.156.194.174:8000/api/v1/health
- **Readiness:** http://178.156.194.174:8000/api/v1/health/readiness
- **Liveness:** http://178.156.194.174:8000/api/v1/health/liveness
- **Metrics:** http://178.156.194.174:8000/metrics

### Alpine Backend
- **Health:** http://91.98.153.49:8001/health
- **Readiness:** http://91.98.153.49:8001/health/readiness
- **Liveness:** http://91.98.153.49:8001/health/liveness
- **Metrics:** http://91.98.153.49:8001/metrics

### Alpine Frontend
- **Health:** http://91.98.153.49:3000/api/health
- **Readiness:** http://91.98.153.49:3000/api/health/readiness
- **Liveness:** http://91.98.153.49:3000/api/health/liveness

---

## Support and Troubleshooting

### Common Issues

1. **Health Check Timeout:**
   - Check service logs for slow dependencies
   - Verify timeout settings (5 seconds default)
   - Check network connectivity

2. **Database Check Failing:**
   - Verify database is accessible
   - Check database connection string
   - Verify database permissions

3. **Prometheus Not Collecting Metrics:**
   - Verify Prometheus configuration
   - Check blackbox exporter is running
   - Verify network connectivity to targets

4. **Alerts Not Triggering:**
   - Verify alert rules syntax
   - Check Prometheus is evaluating rules
   - Verify Alertmanager configuration

### Documentation
- `docs/HEALTH_CHECK_API_DOCUMENTATION.md` - Complete API reference
- `HEALTH_CHECK_IMPLEMENTATION_SUMMARY.md` - Implementation details
- `HEALTH_CHECK_COMPREHENSIVE_REPORT.md` - Original analysis

---

## Sign-Off

**Deployment Verified By:** _________________  
**Date:** _________________  
**All Checks Passed:** [ ] Yes [ ] No

**Notes:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

**Checklist Version:** 1.0  
**Last Updated:** 2025-01-27

