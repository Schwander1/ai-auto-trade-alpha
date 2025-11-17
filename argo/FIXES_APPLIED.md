# Fixes Applied - Signal Generation Troubleshooting

**Date:** 2025-01-27

## ✅ Completed Fixes

### 1. API Key Configuration (Argo)
- **Status:** ✅ **DONE**
- **File:** `argo/config.json`
- **Changes:**
  ```json
  "api_keys": {
    "argo_api_key": "988807abc6a05772fd1900bcbfd35b6037f4f3ba4656e99e78f67b1242041736"
  },
  "alpine": {
    "api_url": "http://91.98.153.49:8001"
  }
  ```
- **Result:** Argo can now authenticate with Alpine backend

### 2. Confidence Threshold Lowered
- **Status:** ✅ **DONE**
- **File:** `argo/config.json`
- **Changes:**
  ```json
  "feature_flags": {
    "confidence_threshold_88": false  // Changed from true
  }
  ```
- **Result:** Signals will use 75% threshold instead of 88%, making it easier to generate signals

---

## ⏳ Pending Fixes

### 3. API Key Configuration (Alpine Backend)
- **Status:** ⏳ **PENDING**
- **File:** `alpine-backend/docker-compose.production.yml`
- **Action Required:** Add environment variable:
  ```yaml
  - EXTERNAL_SIGNAL_API_KEY=988807abc6a05772fd1900bcbfd35b6037f4f3ba4656e99e78f67b1242041736
  ```
- **Note:** Must match the `argo_api_key` in Argo config
- **Location:** Add to both `backend-1` and `backend-2` services

### 4. Restart Alpine Backend
- **Status:** ⏳ **PENDING**
- **Action Required:** Restart Alpine backend to:
  - Load the sync router
  - Apply the new API key configuration
- **Command:** (On remote server 91.98.153.49)
  ```bash
  docker-compose restart alpine-backend
  # or
  systemctl restart alpine-backend
  ```

### 5. Verify Signal Generation
- **Status:** ⏳ **PENDING**
- **Action Required:** 
  - Check if Argo signal generation service is running
  - Monitor logs for signal generation
  - Verify signals are being synced to Alpine

---

## Next Steps

1. **Add API key to Alpine backend docker-compose.production.yml**
   ```yaml
   environment:
     - EXTERNAL_SIGNAL_API_KEY=988807abc6a05772fd1900bcbfd35b6037f4f3ba4656e99e78f67b1242041736
   ```

2. **Restart Alpine backend** (on remote server)
   - This will load the sync router and apply API key config

3. **Test sync endpoint**
   ```bash
   ./argo/scripts/test_sync_endpoint.sh
   ```

4. **Monitor signal generation**
   ```bash
   tail -f argo/logs/service_*.log | grep "Generated signal"
   ```

---

## API Key Details

- **Generated:** `988807abc6a05772fd1900bcbfd35b6037f4f3ba4656e99e78f67b1242041736`
- **Length:** 64 characters (32 bytes hex)
- **Usage:** 
  - Argo sends this key in `X-API-Key` header
  - Alpine backend validates against `EXTERNAL_SIGNAL_API_KEY` environment variable
  - Must match exactly (case-sensitive)

---

## Verification Checklist

- [x] API key added to Argo config.json
- [x] Alpine URL configured in Argo
- [x] Confidence threshold lowered
- [ ] API key added to Alpine backend docker-compose
- [ ] Alpine backend restarted
- [ ] Sync endpoint accessible (test with test_sync_endpoint.sh)
- [ ] Signal generation running
- [ ] Signals syncing to Alpine

---

## Files Modified

1. `argo/config.json` - Added API keys and Alpine config, disabled 88% threshold
2. `alpine-backend/docker-compose.production.yml` - Needs API key added (pending)

---

## Status

**Overall Progress:** 2/5 fixes completed (40%)

**Remaining:** 
- Configure Alpine backend API key
- Restart Alpine backend
- Verify everything works

