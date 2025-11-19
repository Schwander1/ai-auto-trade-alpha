# Production Debugging Guide

## Overview

This guide describes the comprehensive production debugging tools available for the Argo-Alpine trading system.

## Quick Start

### Run Comprehensive Debugging

```bash
# Using the wrapper script (recommended)
./debug_production.sh

# Or directly with Python
python3 debug_production_comprehensive.py
```

## What Gets Checked

The comprehensive debugging script performs the following checks:

### 1. Docker Containers Status
- Checks if Docker daemon is running
- Verifies all production containers are running
- Checks container health status
- Lists container ports and status

**Containers Checked:**
- `alpine-backend-1`, `alpine-backend-2`, `alpine-backend-3`
- `alpine-frontend-1`, `alpine-frontend-2`
- `alpine-postgres`, `alpine-redis`
- `alpine-prometheus`, `alpine-grafana`
- `alpine-node-exporter`, `alpine-postgres-exporter`, `alpine-redis-exporter`

### 2. Service Health Endpoints
- Tests all backend health endpoints (ports 8001, 8002, 8003)
- Tests all frontend endpoints (ports 3000, 3002)
- Verifies HTTP status codes
- Extracts service version and uptime information

### 3. Database Connectivity
- Verifies PostgreSQL container is running
- Tests database connection
- Checks database size
- Counts rows in key tables (users, signals, roles, notifications)
- Detects database locks

### 4. Redis Connectivity
- Verifies Redis container is running
- Tests Redis connection (PING)
- Checks Redis statistics
- Monitors memory usage
- Counts active keys

### 5. API Endpoints
- Tests all API health endpoints
- Verifies metrics endpoints
- Checks API documentation endpoints

### 6. Log Analysis
- Scans container logs for errors
- Detects exceptions and tracebacks
- Identifies warnings
- Shows recent error patterns

**Error Patterns Detected:**
- ERROR, Exception, Traceback
- FATAL, CRITICAL
- WARNING, WARN

### 7. Resource Usage
- CPU usage monitoring
- Memory usage monitoring
- Disk usage monitoring
- Container resource usage (CPU, memory per container)

**Thresholds:**
- CPU: >80% error, >60% warning
- Memory: >90% error, >75% warning
- Disk: >90% error, >80% warning

### 8. Network Connectivity
- Checks if required ports are listening
- Tests external connectivity (DNS servers)
- Verifies port accessibility

**Ports Checked:**
- 8001, 8002, 8003 (Backend APIs)
- 3000, 3002 (Frontend)
- 5433 (PostgreSQL)
- 6380 (Redis)
- 9090 (Prometheus)
- 3100 (Grafana)

### 9. Monitoring Services
- Checks Prometheus health
- Checks Grafana health
- Verifies all exporters are accessible
  - Node Exporter (port 9100)
  - Postgres Exporter (port 9187)
  - Redis Exporter (port 9121)

### 10. Trading System Status
- Checks trading status endpoints
- Verifies environment configuration
- Tests Alpaca connectivity
- Monitors trading mode

## Output Format

The script provides color-coded output:

- ✅ **Green**: Success/Healthy
- ❌ **Red**: Error/Critical Issue
- ⚠️ **Yellow**: Warning/Non-Critical Issue
- ℹ️ **Cyan**: Informational

## Report Summary

At the end of execution, the script generates a comprehensive report including:

1. **Execution Time**: How long the debugging took
2. **Issues Found**: List of all critical issues
3. **Warnings**: List of non-critical warnings
4. **Metrics**: Key system metrics collected
5. **Overall Status**: System health assessment

## Exit Codes

- `0`: All systems operational (may have warnings)
- `1`: Critical issues detected

## Dependencies

### Required
- Python 3.6+
- `requests` library (`pip3 install requests`)

### Optional (for enhanced resource monitoring)
- `psutil` library (`pip3 install psutil`)

If `psutil` is not available, the script will use system commands (`top`, `vm_stat`, `df`) as fallbacks.

## Troubleshooting

### Script Fails to Run

1. **Check Python version:**
   ```bash
   python3 --version
   ```

2. **Install missing dependencies:**
   ```bash
   pip3 install requests psutil
   ```

3. **Check script permissions:**
   ```bash
   chmod +x debug_production.sh
   chmod +x debug_production_comprehensive.py
   ```

### Docker Commands Fail

1. **Verify Docker is running:**
   ```bash
   docker ps
   ```

2. **Check Docker permissions:**
   ```bash
   # On Linux, add user to docker group
   sudo usermod -aG docker $USER
   ```

### Connection Errors

1. **Verify services are running:**
   ```bash
   docker ps | grep alpine
   ```

2. **Check if ports are accessible:**
   ```bash
   curl http://localhost:8001/health
   ```

3. **Review container logs:**
   ```bash
   docker logs alpine-backend-1 --tail 50
   ```

## Integration with Other Tools

### Run with Health Check Scripts

```bash
# Run comprehensive debug
./debug_production.sh

# Then run specific health checks
./scripts/check_all_production_status.sh
./scripts/health_check_production.sh
```

### Automated Monitoring

You can schedule this script to run periodically:

```bash
# Add to crontab (runs every hour)
0 * * * * /path/to/debug_production.sh >> /var/log/production_debug.log 2>&1
```

## Best Practices

1. **Run regularly**: Schedule daily or hourly checks
2. **Review reports**: Check the summary for trends
3. **Act on warnings**: Address warnings before they become issues
4. **Document issues**: Keep track of recurring problems
5. **Update thresholds**: Adjust resource thresholds based on your system

## Related Scripts

- `comprehensive_status_check.py`: Trading system status check
- `check_service_state.py`: Service internal state check
- `investigate_current_state.py`: Current trading state investigation
- `scripts/check_all_production_status.sh`: Production status check
- `scripts/health_check_production.sh`: Health check script

## Support

For issues or questions:
1. Review the troubleshooting section
2. Check container logs
3. Review the comprehensive report output
4. Consult the main troubleshooting guide: `docs/SystemDocs/TROUBLESHOOTING_RECOVERY_COMPLETE_GUIDE.md`

