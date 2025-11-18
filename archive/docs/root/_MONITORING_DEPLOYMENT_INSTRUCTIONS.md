# Monitoring Configuration Deployment Instructions

## Overview

The monitoring configuration files are ready for deployment to your Prometheus server.

## Files Ready for Deployment

- `infrastructure/monitoring/prometheus.yml` - Prometheus configuration with health check monitoring
- `infrastructure/monitoring/alerts.yml` - Alert rules for health checks

## Deployment Methods

### Method 1: Automated Deployment Script

```bash
./scripts/deploy_monitoring_config.sh
```

This script will:
1. Prompt for Prometheus server address
2. Copy configuration files
3. Validate configuration
4. Restart Prometheus (optional)

### Method 2: Manual Deployment

```bash
# 1. Copy configuration files to Prometheus server
scp infrastructure/monitoring/prometheus.yml root@<monitoring-server>:/etc/prometheus/
scp infrastructure/monitoring/alerts.yml root@<monitoring-server>:/etc/prometheus/

# 2. Validate configuration (if promtool is available)
ssh root@<monitoring-server> "promtool check config /etc/prometheus/prometheus.yml"

# 3. Restart Prometheus
ssh root@<monitoring-server> "systemctl restart prometheus"

# 4. Verify Prometheus is running
ssh root@<monitoring-server> "systemctl status prometheus"
```

## Configuration Details

### Health Check Monitoring

The Prometheus configuration includes:
- Health check monitoring for all services (Argo, Alpine Backend, Alpine Frontend)
- Blackbox exporter integration
- 30-second scrape interval
- Production URLs configured

### Alert Rules

The alert rules include:
- `HealthCheckFailed` - Health check failing for 2+ minutes
- `ReadinessCheckFailed` - Service not ready
- `LivenessCheckFailed` - Service not alive
- `HealthCheckSlow` - Health check taking >5 seconds

## Verification

After deployment, verify:
1. Prometheus targets are up: `http://<monitoring-server>:9090/targets`
2. Health check metrics are being collected
3. Alert rules are loaded: `http://<monitoring-server>:9090/api/v1/rules`

## Production URLs

The configuration monitors:
- Argo: `http://178.156.194.174:8000`
- Alpine Backend: `http://91.98.153.49:8001`
- Alpine Frontend: `http://91.98.153.49:3000`

