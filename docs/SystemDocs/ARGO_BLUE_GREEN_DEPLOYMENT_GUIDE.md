# Argo Blue-Green Deployment Guide

**Version:** 1.0  
**Date:** November 14, 2025  
**Status:** Active

---

## Overview

Argo Capital now uses **zero-downtime blue-green deployment** for all production deployments. This ensures no service interruption during deployments and provides instant rollback capability.

---

## Quick Start

### Deploy to Production

```bash
# Zero-downtime blue-green deployment
./scripts/deploy-argo-blue-green.sh
```

### Rollback (If Needed)

```bash
# Quick rollback to previous environment
./scripts/rollback-argo-blue-green.sh
```

---

## Architecture

### Directory Structure

```
/root/
├── argo-production-blue/          # Blue environment
│   ├── argo/                      # Argo codebase
│   ├── venv/                      # Python virtual environment
│   ├── .env                       # Environment variables
│   ├── config.json                # Configuration
│   └── .current                   # Marker file (if active)
│
└── argo-production-green/         # Green environment
    ├── argo/                      # Argo codebase
    ├── venv/                      # Python virtual environment
    ├── .env                       # Environment variables
    ├── config.json                # Configuration
    └── .current                   # Marker file (if active)
```

### Port Allocation

- **Active Environment**: Port 8000 (public-facing)
- **Staging Environment**: Port 8001 (internal, for deployment testing)
- **Traffic Switch**: Port swap after health checks pass

---

## Deployment Process

### Step-by-Step

1. **Detect Current Active Environment**
   - Checks which environment is serving traffic on port 8000
   - Defaults to blue if uncertain

2. **Deploy to Inactive Environment**
   - Deploys code to opposite environment
   - Excludes local-only files (same as before)

3. **Setup Target Environment**
   - Creates/updates virtual environment
   - Installs dependencies
   - Verifies configuration

4. **Start Service on Internal Port**
   - Starts service on port 8001 (staging)
   - Logs to `/tmp/argo-{color}.log`

5. **Health Checks (Gate 11 - MANDATORY)**
   - Level 1: Basic health endpoint
   - Level 3: Comprehensive health check
   - **100% pass rate required** before proceeding

6. **Alpaca Account Verification**
   - Verifies correct environment (production)
   - Checks account connection
   - Validates portfolio access

7. **API Endpoint Verification**
   - Tests `/api/signals/latest` endpoint
   - Verifies response format

8. **Switch Traffic (If All Checks Pass)**
   - Stops current service on port 8000
   - Moves target service to port 8000
   - Keeps old service on port 8001 for rollback

9. **Grace Period & Verification**
   - Waits 30 seconds
   - Verifies new service stability
   - Keeps old service available for quick rollback

---

## Safety Mechanisms

### Health Check Requirements (Gate 11)

**ALL checks must pass before traffic switch:**

1. ✅ Basic Health Endpoint (`/health`)
2. ✅ Comprehensive Health Check (Level 3)
   - Environment detection
   - Trading engine connectivity
   - Signal generation service
   - Alpaca account connection
   - Data sources
   - Risk management
3. ✅ Alpaca Account Verification
   - Correct environment (production)
   - Account connected
   - Portfolio accessible
4. ✅ API Endpoints
   - `/api/signals/latest` working
   - Response format correct

### Automatic Rollback

Deployment will **automatically rollback** if:
- ❌ Health checks fail
- ❌ Alpaca connection fails
- ❌ Service won't start
- ❌ API endpoints not responding
- ❌ Environment detection fails

**Rollback Process:**
1. Stop target environment
2. Keep current environment running
3. Exit with error
4. No traffic switch occurs

---

## Rollback Procedures

### Quick Rollback

```bash
# Automatic rollback script
./scripts/rollback-argo-blue-green.sh
```

### Manual Rollback

```bash
# SSH to production server
ssh root@178.156.194.174

# Stop current service
pkill -f 'uvicorn.*--port 8000'

# Start previous environment
cd /root/argo-production-{previous-color}
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/argo-{color}.log 2>&1 &
```

---

## Migration from Legacy Deployment

### First-Time Setup

The deployment script automatically migrates from legacy deployment:

1. **Detects Legacy Path**: Checks for `/root/argo-production`
2. **Creates Blue Environment**: Copies legacy to blue
3. **Proceeds with Blue-Green**: Uses blue-green for all future deployments

### Legacy Deployment Script

The old `deploy-argo.sh` script is still available but deprecated:
- ✅ Still works for emergency use
- ⚠️  Causes downtime (5-30 seconds)
- 📝 Use blue-green script for all new deployments

---

## Monitoring

### Check Active Environment

```bash
# Check which environment is active
ssh root@178.156.194.174 "lsof -i :8000 | grep uvicorn"

# Check marker files
ssh root@178.156.194.174 "ls -la /root/argo-production-*/.current"
```

### View Logs

```bash
# Active environment logs
ssh root@178.156.194.174 "tail -f /tmp/argo-{color}.log"

# Both environments
ssh root@178.156.194.174 "tail -f /tmp/argo-blue.log /tmp/argo-green.log"
```

### Health Checks

```bash
# Active service
curl http://178.156.194.174:8000/health

# Staging service (if running)
curl http://178.156.194.174:8001/health
```

---

## Troubleshooting

### Issue: Port Conflicts

**Problem**: Both environments try to use same port

**Solution**:
- Script automatically handles port allocation
- Active: 8000, Staging: 8001
- Check for existing processes before starting

### Issue: Environment Detection Fails

**Problem**: Wrong environment detected

**Solution**:
- Check marker files: `/root/argo-production-{color}/.current`
- Check process working directory
- Defaults to blue if uncertain

### Issue: Health Checks Fail

**Problem**: Health checks fail but service seems OK

**Solution**:
- Check service logs: `/tmp/argo-{color}.log`
- Verify Alpaca connection
- Check environment configuration
- Review comprehensive health check output

### Issue: Rollback Needed

**Problem**: New deployment has issues

**Solution**:
- Run rollback script: `./scripts/rollback-argo-blue-green.sh`
- Or manually switch ports
- Old environment kept on port 8001 for quick rollback

---

## Benefits

### Before (Direct Deployment)
- ⚠️  5-30 seconds downtime
- ⚠️  Rollback takes 30-60 seconds
- ⚠️  No health check before going live
- ⚠️  Risk of missed trades during restart

### After (Blue-Green)
- ✅ Zero downtime
- ✅ Instant rollback (< 5 seconds)
- ✅ Health checks before traffic switch
- ✅ Safe to deploy during trading hours
- ✅ Old version available for rollback

---

## Best Practices

### DO
- ✅ Use blue-green deployment for all production deployments
- ✅ Monitor health checks during deployment
- ✅ Keep old environment available for rollback
- ✅ Test rollback procedure regularly
- ✅ Deploy during low-traffic periods when possible

### DON'T
- ❌ Stop old service immediately after switch
- ❌ Skip health checks
- ❌ Deploy without testing locally first
- ❌ Ignore health check failures

---

## Comparison with Alpine

Both Argo and Alpine now use blue-green deployment:

| Aspect | Argo | Alpine |
|--------|------|--------|
| **Strategy** | Process-based | Docker-based |
| **Ports** | 8000 (active), 8001 (staging) | 8001/3000 (blue), 8002/3002 (green) |
| **Switch Method** | Port swap | Nginx config update |
| **Zero Downtime** | ✅ Yes | ✅ Yes |
| **Rollback** | ✅ Instant | ✅ Instant |

---

## Related Documentation

- [Deployment Rules](../Rules/04_DEPLOYMENT.md)
- [System Architecture](COMPLETE_SYSTEM_ARCHITECTURE.md)
- [Operational Guide](OPERATIONAL_GUIDE.md)
- [Health Check Guide](SYSTEM_MONITORING_COMPLETE_GUIDE.md)

---

## Support

For issues or questions:
1. Check deployment logs: `/tmp/argo-{color}.log`
2. Review health check output
3. Verify environment configuration
4. Check rollback script if needed

