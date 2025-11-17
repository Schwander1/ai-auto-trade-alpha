# Production Signal Generation Troubleshooting Report

**Date:** 2025-01-27  
**Status:** 🔍 Issues Identified

## Summary

Signal generation in production has several issues preventing signals from being synced to Alpine backend.

---

## Issues Found

### 1. ❌ Signals Not Being Generated Recently
- **Status:** CRITICAL
- **Evidence:** Latest signal in database is from 2025-11-12 (3 days ago)
- **Location:** `argo/data/signals.db`
- **Impact:** No new signals are being generated or stored

**Possible Causes:**
- Signal generation service not running
- Confidence threshold too high (88%) - signals not meeting threshold
- Service crashed or stopped
- Background task not running

**Action Required:**
- Check if signal generation service is running
- Verify background task is active
- Check logs for errors or warnings
- Lower confidence threshold temporarily to test

---

### 2. ❌ Alpine Sync Endpoint Not Registered (404)
- **Status:** CRITICAL
- **Evidence:** 
  - `GET /api/v1/external-signals/sync/health` returns 404
  - `POST /api/v1/external-signals/sync/signal` returns 404
  - OpenAPI spec shows 0 paths (no routes registered)
- **Expected:** Should return health status and accept signals
- **Impact:** Cannot sync signals to Alpine backend

**Root Cause:**
- Router is defined in code (`external_signal_sync.py`)
- Router is included in `main.py` (line 296)
- But router is NOT being registered at runtime
- OpenAPI spec confirms no routes are registered

**Possible Causes:**
- Backend is running old code (needs restart)
- Import error preventing router from loading (silent failure)
- Router import is failing but exception is caught

**Action Required:**
- **IMMEDIATE:** Restart Alpine backend to load latest code
- Check backend logs for import errors
- Verify router is actually being imported and registered
- Test with: `./argo/scripts/test_sync_endpoint.sh`

---

### 3. ⚠️ API Key Configuration Missing
- **Status:** WARNING
- **Evidence:** 
  - `ARGO_API_KEY` not set in environment
  - Not found in `config.json`
  - Alpine backend expects `EXTERNAL_SIGNAL_API_KEY` to match
- **Impact:** Sync will fail with 401 authentication error

**Action Required:**
- Set `ARGO_API_KEY` environment variable in Argo
- Set `EXTERNAL_SIGNAL_API_KEY` in Alpine backend (must match)
- Or add to `config.json` under `api_keys.argo_api_key`
- Test authentication

---

### 4. ✅ Alpine Backend is Running
- **Status:** OK
- **Evidence:** `GET /health` returns 200
- **Location:** `http://91.98.153.49:8001/health`

---

### 5. ✅ Alpine Sync Service is Initialized
- **Status:** OK
- **Evidence:** Service initializes successfully
- **Location:** `argo/argo/core/alpine_sync.py`
- **Note:** Service is enabled but may not be receiving signals to sync

---

## Diagnostic Steps

### Step 1: Check Signal Generation Service Status

```bash
# Check if service is running
ps aux | grep signal_generation

# Check recent logs
tail -100 argo/logs/service_*.log | grep -i "signal\|error\|warning"

# Check database for recent signals
sqlite3 argo/data/signals.db "SELECT COUNT(*) as total, MAX(timestamp) as latest FROM signals;"
```

### Step 2: Verify Alpine Backend Connectivity

```bash
# Test health endpoint
curl http://91.98.153.49:8001/health

# Test sync health endpoint (should work but currently 404)
curl http://91.98.153.49:8001/api/v1/external-signals/sync/health

# Test sync endpoint with dummy data
curl -X POST http://91.98.153.49:8001/api/v1/external-signals/sync/signal \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key" \
  -d '{"signal_id":"test","symbol":"AAPL","action":"BUY","entry_price":100,"target_price":105,"stop_price":98,"confidence":90,"strategy":"test","timestamp":"2025-01-27T00:00:00Z"}'
```

### Step 3: Check Configuration

```bash
# Verify Alpine sync setup
cd argo && python3 scripts/verify_alpine_sync_setup.py

# Test Alpine sync
cd argo && python3 scripts/test_alpine_sync.py
```

### Step 4: Check Signal Generation

```bash
# Check if signals are being generated
tail -f argo/logs/service_*.log | grep "Generated signal"

# Check confidence threshold
grep -i "confidence.*threshold\|88%" argo/logs/service_*.log | tail -10
```

---

## Recommended Fixes

### Fix 1: Restart Signal Generation Service

```bash
# Stop service
pkill -f signal_generation

# Start service (if using systemd)
systemctl restart argo-signal-generation

# Or start manually
cd argo && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Fix 2: Configure API Keys

```bash
# In Argo environment
export ARGO_API_KEY="your-secure-api-key-here"
export ALPINE_API_URL="http://91.98.153.49:8001"
export ALPINE_SYNC_ENABLED="true"

# In Alpine backend environment
export EXTERNAL_SIGNAL_API_KEY="your-secure-api-key-here"  # Must match ARGO_API_KEY
```

Or add to `argo/config.json`:
```json
{
  "api_keys": {
    "argo_api_key": "your-secure-api-key-here"
  },
  "alpine": {
    "api_url": "http://91.98.153.49:8001"
  }
}
```

### Fix 3: Lower Confidence Threshold (Temporarily for Testing)

Edit `argo/config.json`:
```json
{
  "trading": {
    "min_confidence": 75.0  // Lower from 88% to 75% for testing
  }
}
```

Or disable feature flag:
```json
{
  "feature_flags": {
    "confidence_threshold_88": false
  }
}
```

### Fix 4: Fix Alpine Sync Health Endpoint

The health endpoint should be accessible. Verify router registration in `alpine-backend/backend/main.py`:

```python
app.include_router(external_signal_sync.router)  # Should be registered
```

---

## Testing Checklist

- [ ] Signal generation service is running
- [ ] Signals are being generated (check logs)
- [ ] Signals are stored in Argo database
- [ ] Alpine backend is accessible
- [ ] API keys are configured and match
- [ ] Sync service is initialized
- [ ] Signals are being synced to Alpine (check Alpine logs)
- [ ] Signals appear in Alpine database

---

## Next Steps

1. **Immediate:** Restart signal generation service
2. **Immediate:** Configure API keys
3. **Immediate:** Lower confidence threshold to test
4. **Short-term:** Fix Alpine sync health endpoint
5. **Short-term:** Monitor signal generation and sync
6. **Long-term:** Set up proper monitoring and alerting

---

## Monitoring

After fixes, monitor:
- Signal generation rate
- Sync success rate
- Error logs
- Database growth
- API response times

