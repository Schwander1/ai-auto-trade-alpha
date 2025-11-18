# Fixes Applied - Signal Storage and Generation

**Date:** November 18, 2025  
**Status:** ✅ **FIXES APPLIED**

---

## Issues Fixed

### 1. ✅ Database Path Detection
**Problem:** Prop firm service was using wrong database path (`/root/argo-production` instead of `/root/argo-production-prop-firm`)

**Fix Applied:**
- Updated `signal_tracker.py` to check for prop firm path first
- Updated `main.py` database connection to check for prop firm path first
- Now correctly detects: prop-firm → green → production → dev

**Files Changed:**
- `argo/argo/core/signal_tracker.py` (lines 32-41)
- `argo/main.py` (lines 797-805)

---

### 2. ✅ API Endpoint Signal Generation
**Problem:** `/api/signals/latest` was using mock data instead of real signal service when database was empty

**Fix Applied:**
- Changed fallback to use real `SignalGenerationService` instead of mock `get_signals()`
- Signals generated on-demand are now stored in database
- Proper error handling with multiple fallback levels

**Files Changed:**
- `argo/main.py` (lines 898-984)

**Behavior:**
1. First: Try to get signals from database
2. Second: Generate using real signal service (stores to DB)
3. Third: Fallback to mock data (only if service fails)

---

## What This Fixes

### Signal Storage
- ✅ Signals now stored in correct database for each service
- ✅ Prop firm signals go to `/root/argo-production-prop-firm/data/signals.db`
- ✅ Regular trading signals go to `/root/argo-production-green/data/signals.db`
- ✅ On-demand generated signals are persisted

### Signal Generation
- ✅ API endpoint uses real signal generation service
- ✅ Generated signals are automatically stored
- ✅ Background generation continues to work (already running)

---

## Next Steps

1. **Deploy to Production:**
   ```bash
   # Deploy to prop firm service
   scp argo/argo/core/signal_tracker.py root@178.156.194.174:/root/argo-production-prop-firm/argo/argo/core/
   scp argo/main.py root@178.156.194.174:/root/argo-production-prop-firm/
   
   # Deploy to regular trading service
   scp argo/argo/core/signal_tracker.py root@178.156.194.174:/root/argo-production-green/argo/argo/core/
   scp argo/main.py root@178.156.194.174:/root/argo-production-green/
   ```

2. **Restart Services:**
   ```bash
   ssh root@178.156.194.174 'systemctl restart argo-trading-prop-firm.service'
   ssh root@178.156.194.174 'systemctl restart argo-trading.service'
   ```

3. **Verify:**
   ```bash
   # Check database is being used
   ssh root@178.156.194.174 'ls -lh /root/argo-production-prop-firm/data/signals.db'
   
   # Check signals are being stored
   ssh root@178.156.194.174 'sqlite3 /root/argo-production-prop-firm/data/signals.db "SELECT COUNT(*) FROM signals;"'
   
   # Test API endpoint
   curl http://178.156.194.174:8001/api/signals/latest?limit=5
   ```

---

## Expected Results

After deployment:
- ✅ Signals stored in correct database
- ✅ Database file size increases as signals are generated
- ✅ API returns real signals from database
- ✅ Background generation continues storing signals every 5 seconds

---

**Status:** ✅ **READY FOR DEPLOYMENT**

