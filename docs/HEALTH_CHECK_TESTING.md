# Health Check Testing Guide

## Overview

Comprehensive health check testing for all services including the execution dashboard system.

## Test Scripts

### 1. Complete Health Check
```bash
./scripts/test_all_health.sh [local|production]
```

Tests all health endpoints:
- Argo service health
- Execution dashboard endpoints
- Alpine backend health
- Alpine frontend health

### 2. Execution Dashboard Health Check
```bash
./scripts/test_execution_dashboard_health.sh [local|production]
```

Tests execution dashboard specific endpoints.

### 3. Standard Health Check
```bash
./scripts/test_health_endpoints.sh [local|production]
```

Tests standard health endpoints.

## Health Endpoints Tested

### Argo Service

1. **Comprehensive Health** - `/api/v1/health`
   - Checks all components
   - Includes execution services
   - Returns detailed status

2. **Readiness Probe** - `/api/v1/health/readiness`
   - Kubernetes readiness
   - Critical dependencies only

3. **Liveness Probe** - `/api/v1/health/liveness`
   - Kubernetes liveness
   - Quick service check

4. **Uptime** - `/api/v1/health/uptime`
   - Service uptime information

5. **Metrics** - `/metrics`
   - Prometheus metrics

6. **Execution Dashboard** (Admin Only)
   - `/api/v1/execution/metrics`
   - `/api/v1/execution/queue`
   - `/api/v1/execution/account-states`
   - `/api/v1/execution/recent-activity`
   - `/api/v1/execution/rejection-reasons`
   - `/api/v1/execution/dashboard`

### Alpine Backend

1. **Health** - `/health`
2. **Readiness** - `/health/readiness`
3. **Liveness** - `/health/liveness`
4. **Metrics** - `/metrics`

### Alpine Frontend

1. **Health** - `/api/health`
2. **Readiness** - `/api/health/readiness`
3. **Liveness** - `/api/health/liveness`

## Running Tests

### Local Testing
```bash
# Test all health endpoints
./scripts/test_all_health.sh local

# Test execution dashboard
ADMIN_API_KEY=your-key ./scripts/test_execution_dashboard_health.sh local
```

### Production Testing
```bash
# Test all health endpoints
./scripts/test_all_health.sh production

# Test execution dashboard
ADMIN_API_KEY=your-key ./scripts/test_execution_dashboard_health.sh production
```

## Expected Results

### All Services Healthy
- ✅ All endpoints return 200
- ✅ Health status is "healthy"
- ✅ All components operational

### Degraded Service
- ⚠️ Some endpoints return 200
- ⚠️ Health status is "degraded"
- ⚠️ Some components may be down

### Unhealthy Service
- ❌ Health endpoints return 503
- ❌ Critical components down
- ❌ Service needs attention

## Health Check Components

### Execution Services Health
- Queue system status
- Account monitor status
- Queue statistics
- Executors monitored

### Signal Generation Health
- Service running status
- Background task status
- Generation rate

### Database Health
- Database accessible
- Signal count
- Query performance

### Trading Engine Health
- Alpaca connection
- Account status
- Trading enabled

## Troubleshooting

### Health Check Fails
1. Check service is running
2. Verify database is accessible
3. Check logs for errors
4. Verify configuration

### Execution Dashboard Fails
1. Verify ADMIN_API_KEY is set
2. Check queue database exists
3. Verify executors are running
4. Check account monitor status

## Continuous Monitoring

Health checks should be run:
- Every 5 minutes (automated)
- Before deployments
- After deployments
- During incidents

## Integration

Health checks integrate with:
- Kubernetes probes
- Prometheus monitoring
- Grafana dashboards
- Alert systems
