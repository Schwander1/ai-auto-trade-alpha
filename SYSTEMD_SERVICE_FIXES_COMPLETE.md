# Systemd Service Startup Fixes - Complete

**Date:** 2025-01-27  
**Status:** ✅ **ALL FIXES IMPLEMENTED**

---

## 🎯 Overview

Comprehensive fixes have been implemented to permanently resolve systemd service startup issues. Argo services now have proper dependency management, health checks, and startup verification.

---

## ✅ Fixes Implemented

### 1. **Dependency Waiting Scripts** ✅

#### `wait-for-dependencies.sh`
- **Waits for Redis:** Up to 30 retries (60 seconds) with connection testing
- **Waits for Database:** Verifies SQLite database is accessible and writable
- **Uses Python libraries:** `redis` and `sqlite3` (standard library)
- **Proper error handling:** Exits with error code if dependencies don't become ready
- **Logging:** Timestamped status messages during startup
- **Location:** `infrastructure/systemd/wait-for-dependencies.sh`

#### `verify-service-health.sh`
- **Verifies service health:** Checks health endpoint after startup
- **Non-blocking:** Doesn't fail service if health check fails (service may still be starting)
- **Multiple endpoint support:** Tries both `/health` and `/api/v1/health`
- **Retry logic:** Up to 15 retries (30 seconds) with 2-second delays
- **Location:** `infrastructure/systemd/verify-service-health.sh`

---

### 2. **Systemd Service File Updates** ✅

#### Argo Trading Service (`argo-trading.service`)
- **Dependencies:** Changed from `network.target` to `network-online.target` (waits for actual network connectivity)
- **ExecStartPre:** Runs `wait-for-dependencies.sh` before starting service
- **ExecStartPost:** Runs `verify-service-health.sh` after service starts (non-blocking)
- **RestartSec:** Increased from 10s to 30s (allows proper initialization)
- **StartLimitInterval:** Added 300s window
- **StartLimitBurst:** Added limit of 5 restarts per window
- **TimeoutStartSec:** Added 120s timeout for startup
- **Environment variables:** Added Redis configuration variables
- **Logging:** Added `SyslogIdentifier` for better log filtering

#### Argo Prop Firm Service (`argo-trading-prop-firm.service`)
- **Same improvements as Argo Trading Service**
- **Port:** Configured for port 8001
- **Service name:** `argo-trading-prop-firm`

---

### 3. **Service Installation Script** ✅

#### `install-services.sh`
- **New script:** Centralized installation of all systemd services
- **Helper script setup:** Ensures helper scripts are executable
- **Service file copying:** Copies both service files to `/etc/systemd/system/`
- **Validation:** Validates service files with `systemd-analyze`
- **Location:** `infrastructure/systemd/install-services.sh`

---

### 4. **Updated Installation Scripts** ✅

#### `scripts/install-systemd-service.sh`
- **Updated:** Now verifies helper scripts are executable
- **Improved:** Better error handling and logging

---

## 📋 Files Created/Modified

### New Files
1. `infrastructure/systemd/wait-for-dependencies.sh` - Dependency waiting script
2. `infrastructure/systemd/verify-service-health.sh` - Health verification script
3. `infrastructure/systemd/install-services.sh` - Service installation script

### Modified Files
4. `infrastructure/systemd/argo-trading.service` - Updated with dependency management
5. `infrastructure/systemd/argo-trading-prop-firm.service` - Updated with dependency management
6. `scripts/install-systemd-service.sh` - Updated to handle helper scripts

---

## 🔍 How It Works

### Startup Sequence

1. **Systemd Starts Service**
   - Waits for `network-online.target` (actual network connectivity)
   - Optional: Waits for `redis.service` if it's a systemd service

2. **ExecStartPre: Wait for Dependencies**
   - Runs `wait-for-dependencies.sh`
   - Checks Redis connectivity (up to 60 seconds)
   - Checks database accessibility (up to 60 seconds)
   - Service fails to start if dependencies aren't ready

3. **ExecStart: Start Application**
   - Starts uvicorn with proper configuration
   - Application initializes with dependencies already available

4. **ExecStartPost: Verify Health**
   - Runs `verify-service-health.sh` (non-blocking)
   - Checks health endpoint (up to 30 seconds)
   - Logs result but doesn't fail service

5. **Service Running**
   - Service is marked as active
   - Health checks continue via systemd monitoring

---

## 🚀 Deployment Instructions

### 1. Install Services
```bash
cd /root/argo-alpine-workspace
sudo bash infrastructure/systemd/install-services.sh
```

### 2. Enable Services (Start on Boot)
```bash
sudo systemctl enable argo-trading.service
sudo systemctl enable argo-trading-prop-firm.service
```

### 3. Start Services
```bash
sudo systemctl start argo-trading.service
sudo systemctl start argo-trading-prop-firm.service
```

### 4. Check Status
```bash
# Check service status
sudo systemctl status argo-trading.service
sudo systemctl status argo-trading-prop-firm.service

# Check logs
sudo journalctl -u argo-trading.service -f
sudo journalctl -u argo-trading-prop-firm.service -f

# Check for dependency waiting messages
sudo journalctl -u argo-trading.service | grep -E "Waiting for|dependencies|Redis|Database"
```

### 5. Verify Health
```bash
# Check Argo service
curl http://localhost:8000/health

# Check Prop Firm service
curl http://localhost:8001/health
```

---

## 🛡️ Failure Prevention

### What These Fixes Prevent

1. **Race Conditions**
   - Services no longer start before Redis is ready
   - Services no longer start before database is accessible
   - Network connectivity verified before startup

2. **Connection Failures**
   - Dependency waiting scripts verify connectivity before starting
   - Retry logic handles transient network issues
   - Clear error messages if dependencies fail

3. **Startup Timeouts**
   - Increased `RestartSec` to 30s (from 10s)
   - Added `TimeoutStartSec` of 120s
   - Sufficient time for application initialization

4. **Restart Loops**
   - Added `StartLimitInterval` and `StartLimitBurst`
   - Prevents infinite restart loops
   - Systemd will stop restarting after 5 failures in 5 minutes

5. **Silent Failures**
   - Health verification after startup
   - Clear logging in dependency scripts
   - Timestamped log messages

---

## 📊 Expected Behavior

### Normal Startup
- Total startup time: ~30-60 seconds
- Dependencies checked before service starts
- Health verified after startup
- Service marked as active
- No connection errors in logs

### Redis Slow to Start
- Dependency script retries up to 60 seconds
- Service waits until Redis is ready
- Clear logging of retry attempts
- Service starts successfully once Redis is ready

### Database Issues
- Dependency script retries up to 60 seconds
- Service waits until database is accessible
- Clear logging of retry attempts
- Service starts successfully once database is ready

### Partial Failure
- If Redis never becomes ready: Service fails to start (expected)
- If database never becomes ready: Service fails to start (expected)
- Clear error messages in logs
- Systemd marks service as failed

---

## 🔧 Troubleshooting

### Service Won't Start

1. **Check Dependency Script Logs**
   ```bash
   sudo journalctl -u argo-trading.service | grep -A 20 "ExecStartPre"
   ```
   Look for:
   - "Waiting for dependencies..."
   - "Redis is ready" or "Redis not ready yet"
   - "Database is ready" or "Database not ready yet"

2. **Check Service Status**
   ```bash
   sudo systemctl status argo-trading.service
   ```
   Look for:
   - Active state
   - Any error messages
   - Last few log lines

3. **Check Redis Manually**
   ```bash
   redis-cli -h localhost -p 6379 ping
   # Or with password:
   redis-cli -h localhost -p 6379 -a "password" ping
   ```

4. **Check Database Manually**
   ```bash
   # Check if database file exists and is writable
   ls -la /root/argo-production-green/data/signals.db
   # Or for prop firm:
   ls -la /root/argo-production-prop-firm/data/signals.db
   ```

### Service Starts But Health Check Fails

1. **Check Application Logs**
   ```bash
   tail -f /tmp/argo-green.log
   # Or for prop firm:
   tail -f /tmp/argo-prop-firm.log
   ```

2. **Check Health Endpoint Manually**
   ```bash
   curl -v http://localhost:8000/health
   curl -v http://localhost:8000/api/v1/health
   ```

3. **Check Service Process**
   ```bash
   ps aux | grep uvicorn
   netstat -tlnp | grep 8000
   ```

### Service Restarts Repeatedly

1. **Check Restart Count**
   ```bash
   sudo systemctl status argo-trading.service | grep "Main PID"
   ```

2. **Check Logs for Errors**
   ```bash
   sudo journalctl -u argo-trading.service -n 100 | grep -i error
   ```

3. **Check Start Limit**
   ```bash
   sudo systemctl show argo-trading.service | grep StartLimit
   ```

---

## ✅ Verification Checklist

- [x] Helper scripts created and executable
- [x] Service files updated with ExecStartPre
- [x] Service files updated with ExecStartPost
- [x] RestartSec increased to 30s
- [x] StartLimitInterval and StartLimitBurst added
- [x] TimeoutStartSec added (120s)
- [x] Network dependency changed to network-online.target
- [x] Redis environment variables added
- [x] Installation script created
- [x] Service files validated

---

## 📝 Key Improvements

### Before
- Services started immediately without checking dependencies
- No health verification after startup
- Short restart delay (10s) causing restart loops
- No protection against infinite restart loops
- Services could start before network was fully ready

### After
- Services wait for dependencies (Redis, database)
- Health verification after startup
- Longer restart delay (30s) for proper initialization
- Protection against restart loops (5 restarts per 5 minutes)
- Services wait for actual network connectivity
- Clear logging and error messages

---

## 🎉 Summary

All systemd service startup issues have been comprehensively addressed:

1. ✅ Dependency waiting scripts created
2. ✅ Health verification scripts created
3. ✅ Service files updated with proper dependency management
4. ✅ Restart policies improved
5. ✅ Installation scripts updated
6. ✅ Clear logging and error messages

**Services should now start reliably with proper dependency management and health verification.**

---

**Status:** ✅ **COMPLETE - READY FOR DEPLOYMENT**

