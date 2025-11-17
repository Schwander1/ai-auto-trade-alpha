# Health Check API Documentation

**Last Updated:** 2025-01-27  
**Version:** 2.0

---

## Overview

This document describes all health check endpoints available across the Argo-Alpine trading platform. All services now have comprehensive health checks with timeout handling, error handling, and Kubernetes compatibility.

---

## Argo Service

### Base URL
- **Production:** `http://178.156.194.174:8000`
- **Local:** `http://localhost:8000`

### Endpoints

#### 1. Comprehensive Health Check
**Endpoint:** `GET /api/v1/health`

**Description:** Comprehensive health check with all dependency checks including database, Redis, secrets, data sources, and performance metrics.

**Response:**
```json
{
  "status": "healthy",
  "version": "6.0",
  "timestamp": "2025-01-27T12:00:00Z",
  "uptime_seconds": 86400,
  "uptime_formatted": "1d 0h 0m",
  "services": {
    "api": "healthy",
    "database": "healthy",
    "database_info": {
      "accessible": true,
      "signal_count": 1247
    },
    "redis": "healthy",
    "secrets": "healthy",
    "data_sources": {
      "total_sources": 6,
      "healthy": 5,
      "unhealthy": 0,
      "degraded": 1
    },
    "performance": {
      "uptime_seconds": 86400,
      "avg_signal_generation_time": 0.25
    }
  },
  "system": {
    "cpu_percent": 25.5,
    "memory_percent": 45.2,
    "disk_percent": 30.1
  }
}
```

**Status Codes:**
- `200` - Service is healthy
- `503` - Service is degraded or unhealthy

**Timeout:** 5 seconds maximum per check

---

#### 2. Readiness Probe
**Endpoint:** `GET /api/v1/health/readiness`

**Description:** Kubernetes readiness probe. Returns 200 only if service is ready to handle traffic (all critical dependencies healthy).

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2025-01-27T12:00:00Z"
}
```

**Status Codes:**
- `200` - Service is ready
- `503` - Service is not ready (database or other critical dependency unhealthy)

**Use Case:** Kubernetes uses this to determine if the service can receive traffic.

---

#### 3. Liveness Probe
**Endpoint:** `GET /api/v1/health/liveness`

**Description:** Kubernetes liveness probe. Quick check to verify service is alive (no dependency checks).

**Response:**
```json
{
  "status": "alive",
  "timestamp": "2025-01-27T12:00:00Z",
  "uptime_seconds": 86400
}
```

**Status Codes:**
- `200` - Service is alive
- `503` - Service is not responding

**Use Case:** Kubernetes uses this to determine if the service needs to be restarted.

---

#### 4. Uptime
**Endpoint:** `GET /api/v1/health/uptime`

**Description:** Get service uptime information.

**Response:**
```json
{
  "uptime_seconds": 86400,
  "uptime_formatted": "1d 0h 0m",
  "started_at": "2025-01-26T12:00:00Z",
  "current_time": "2025-01-27T12:00:00Z"
}
```

---

#### 5. Health Metrics
**Endpoint:** `GET /api/v1/health/metrics`

**Description:** Get health-specific metrics.

**Response:**
```json
{
  "signals_generated": 1247,
  "win_rate": 96.3,
  "active_trades": 45,
  "api_latency_ms": 245.5,
  "error_rate": 0.5,
  "requests_per_minute": 125.3
}
```

---

#### 6. Prometheus Metrics
**Endpoint:** `GET /api/v1/health/prometheus`

**Description:** Get Prometheus metrics in raw format.

**Response:** Prometheus text format

---

#### 7. Legacy Health Check (Deprecated)
**Endpoint:** `GET /health`

**Description:** Legacy health check endpoint. **Deprecated** - use `/api/v1/health` instead.

**Response:**
```json
{
  "status": "healthy",
  "version": "6.0",
  "deprecated": true,
  "recommended_endpoint": "/api/v1/health"
}
```

---

## Alpine Backend Service

### Base URL
- **Production:** `http://91.98.153.49:8001`
- **Local:** `http://localhost:9001`

### Endpoints

#### 1. Comprehensive Health Check
**Endpoint:** `GET /health`

**Description:** Comprehensive health check with database, Redis, secrets, system metrics, and uptime.

**Response:**
```json
{
  "status": "healthy",
  "service": "Alpine Analytics API",
  "version": "1.0.0",
  "domain": "91.98.153.49",
  "timestamp": "2025-01-27T12:00:00Z",
  "uptime_seconds": 86400,
  "uptime_formatted": "1d 0h 0m",
  "checks": {
    "database": "healthy",
    "redis": "healthy",
    "secrets": "healthy"
  },
  "system": {
    "cpu_percent": 25.5,
    "memory_percent": 45.2,
    "disk_percent": 30.1
  }
}
```

**Status Codes:**
- `200` - Service is healthy
- `503` - Service is degraded or unhealthy

**Timeout:** 
- Database: 5 seconds
- Redis: 2 seconds
- Secrets: 3 seconds

---

#### 2. Readiness Probe
**Endpoint:** `GET /health/readiness`

**Description:** Kubernetes readiness probe. Checks database connectivity.

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2025-01-27T12:00:00Z"
}
```

**Status Codes:**
- `200` - Service is ready
- `503` - Service is not ready (database unavailable)

---

#### 3. Liveness Probe
**Endpoint:** `GET /health/liveness`

**Description:** Kubernetes liveness probe. Quick service alive check.

**Response:**
```json
{
  "status": "alive",
  "timestamp": "2025-01-27T12:00:00Z",
  "uptime_seconds": 86400
}
```

**Status Codes:**
- `200` - Service is alive
- `503` - Service is not responding

---

#### 4. Prometheus Metrics
**Endpoint:** `GET /metrics`

**Description:** Prometheus metrics endpoint.

**Response:** Prometheus text format

---

## Alpine Frontend Service

### Base URL
- **Production:** `http://91.98.153.49:3000`
- **Local:** `http://localhost:3000`

### Endpoints

#### 1. Health Check
**Endpoint:** `GET /api/health`

**Description:** Frontend service health check.

**Response:**
```json
{
  "status": "healthy",
  "service": "Alpine Frontend",
  "version": "1.0.0",
  "environment": "production",
  "timestamp": "2025-01-27T12:00:00Z",
  "build": {
    "node_version": "v20.10.0",
    "next_version": "14.0.0"
  }
}
```

**Status Codes:**
- `200` - Service is healthy
- `503` - Service is unhealthy

---

#### 2. Readiness Probe
**Endpoint:** `GET /api/health/readiness`

**Description:** Kubernetes readiness probe.

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2025-01-27T12:00:00Z"
}
```

**Status Codes:**
- `200` - Service is ready
- `503` - Service is not ready

---

#### 3. Liveness Probe
**Endpoint:** `GET /api/health/liveness`

**Description:** Kubernetes liveness probe.

**Response:**
```json
{
  "status": "alive",
  "timestamp": "2025-01-27T12:00:00Z"
}
```

**Status Codes:**
- `200` - Service is alive
- `503` - Service is not responding

---

## Health Status Values

### Overall Status
- `healthy` - All checks passing, service fully operational
- `degraded` - Some non-critical checks failing, service partially operational
- `unhealthy` - Critical checks failing, service not operational

### Individual Check Status
- `healthy` - Check passed
- `unhealthy` - Check failed
- `not_configured` - Service not configured (e.g., Redis optional)
- `degraded` - Check passed but using fallback (e.g., secrets manager)

---

## Timeout Handling

All health checks have timeout protection:
- **Argo:** 5 seconds maximum per check
- **Alpine Backend:** 
  - Database: 5 seconds
  - Redis: 2 seconds
  - Secrets: 3 seconds
- **Alpine Frontend:** No timeout (quick checks only)

If a check times out, the service status will be marked as `degraded` or `unhealthy` depending on the criticality of the check.

---

## Error Handling

All health endpoints have comprehensive error handling:
- Exceptions are caught and logged
- Errors are returned in response with appropriate HTTP status codes
- Timeout errors are handled gracefully
- Dependency failures don't crash the health endpoint

---

## Kubernetes Integration

### Recommended Configuration

**Readiness Probe:**
```yaml
readinessProbe:
  httpGet:
    path: /api/v1/health/readiness  # Argo
    path: /health/readiness          # Alpine Backend
    path: /api/health/readiness      # Alpine Frontend
    port: 8000  # or appropriate port
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  successThreshold: 1
  failureThreshold: 3
```

**Liveness Probe:**
```yaml
livenessProbe:
  httpGet:
    path: /api/v1/health/liveness   # Argo
    path: /health/liveness           # Alpine Backend
    path: /api/health/liveness       # Alpine Frontend
    port: 8000  # or appropriate port
  initialDelaySeconds: 30
  periodSeconds: 30
  timeoutSeconds: 5
  successThreshold: 1
  failureThreshold: 3
```

---

## Docker Compose Integration

Health checks are configured in docker-compose files:

**Alpine Backend:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health/readiness"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

**Argo:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/readiness"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

---

## Monitoring Integration

### Prometheus

Health checks are monitored via Prometheus blackbox exporter:
- Job: `health-checks`
- Scrape interval: 30 seconds
- Metrics: `probe_success`, `probe_http_status_code`, `probe_http_duration_seconds`

### Alerts

The following alerts are configured:
- `HealthCheckFailed` - Health check failing for 2+ minutes
- `ReadinessCheckFailed` - Readiness check failing (service cannot handle traffic)
- `LivenessCheckFailed` - Liveness check failing (service may need restart)
- `HealthCheckSlow` - Health check taking >5 seconds

---

## Testing

### Manual Testing

```bash
# Test Argo health endpoints
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/health/readiness
curl http://localhost:8000/api/v1/health/liveness

# Test Alpine Backend health endpoints
curl http://localhost:9001/health
curl http://localhost:9001/health/readiness
curl http://localhost:9001/health/liveness

# Test Alpine Frontend health endpoints
curl http://localhost:3000/api/health
curl http://localhost:3000/api/health/readiness
curl http://localhost:3000/api/health/liveness
```

### Automated Testing

Use the test script:
```bash
./scripts/test_health_endpoints.sh local
./scripts/test_health_endpoints.sh production
```

---

## Migration Guide

### From Legacy Endpoints

**Argo:**
- Old: `GET /health`
- New: `GET /api/v1/health` (recommended)
- Legacy endpoint still works but is deprecated

**Alpine Backend:**
- No change - `/health` endpoint remains the same but now includes more checks

**Alpine Frontend:**
- New: `GET /api/health` (previously client-side only)

### For Monitoring Tools

1. **Update Prometheus configuration** to use new endpoints
2. **Update Grafana dashboards** to use new health check metrics
3. **Update alerting rules** to use new health check alerts
4. **Update Kubernetes probes** to use readiness/liveness endpoints

---

## Best Practices

1. **Use Readiness Probes for Load Balancing**
   - Only route traffic to services that pass readiness checks
   - Prevents sending traffic to services that can't handle it

2. **Use Liveness Probes for Restart Logic**
   - Restart services that fail liveness checks
   - Don't restart on temporary failures (use readiness instead)

3. **Monitor Health Check Duration**
   - Alert if health checks take too long (>5 seconds)
   - Indicates potential performance issues

4. **Use Comprehensive Health for Monitoring**
   - Use `/api/v1/health` or `/health` for detailed monitoring
   - Provides full dependency status and system metrics

5. **Handle Timeouts Gracefully**
   - Health checks have timeouts to prevent hanging
   - Services should handle timeout errors gracefully

---

## Troubleshooting

### Health Check Failing

1. **Check logs** for error messages
2. **Verify dependencies** (database, Redis, etc.) are accessible
3. **Check timeout settings** - may need to increase for slow systems
4. **Verify endpoint paths** - ensure using correct endpoint

### Readiness Check Failing

1. **Check database connectivity** - most common cause
2. **Verify all critical dependencies** are healthy
3. **Check service logs** for startup errors
4. **Verify configuration** is correct

### Liveness Check Failing

1. **Service may be crashed** - check process status
2. **Service may be hung** - check for deadlocks or infinite loops
3. **Network issues** - verify service is listening on correct port
4. **Resource exhaustion** - check CPU/memory usage

---

## Support

For issues or questions:
1. Check service logs
2. Review health check response for error details
3. Consult monitoring dashboards
4. Contact DevOps team

---

**Document Version:** 2.0  
**Last Updated:** 2025-01-27

