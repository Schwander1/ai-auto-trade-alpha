# Signal Generation Performance Fixes

**Date:** 2025-11-19  
**Status:** ✅ Implemented

---

## Problem Identified

Signal generation was running at **~1,364 signals/hour** instead of expected **~4,320 signals/hour** (31% of expected rate).

### Root Causes:
1. **Slow cycles**: Each cycle taking ~25 seconds (should be ~2-5 seconds)
2. **Long timeouts**: Market data fetching had 20s timeout, causing delays
3. **No global timeout**: Entire cycles could run indefinitely
4. **Inefficient early exit**: Low-confidence signals still fetched all data sources
5. **Sequential bottlenecks**: Some operations not fully parallelized

---

## Fixes Applied

### 1. Reduced Market Data Timeout ⚡
- **Before**: 20s timeout for market data fetching
- **After**: 8s timeout (60% reduction)
- **Impact**: Faster failure detection, cycles complete sooner

**File**: `argo/argo/core/signal_generation_service.py` (line 1313)

### 2. Reduced Remaining Tasks Timeout ⚡
- **Before**: 10s timeout for remaining tasks
- **After**: 5s timeout (50% reduction)
- **Impact**: Faster cycle completion when some sources are slow

**File**: `argo/argo/core/signal_generation_service.py` (line 1370)

### 3. Added Independent Source Timeout ⚡
- **Before**: No timeout on independent source fetching (xAI Grok, Sonar AI)
- **After**: 5s timeout with partial results
- **Impact**: Prevents slow AI sources from blocking entire cycles

**File**: `argo/argo/core/signal_generation_service.py` (line 1520)

### 4. Added Batch Processing Timeout ⚡
- **Before**: No timeout on symbol batch processing
- **After**: 8s per symbol timeout (e.g., 48s for 6 symbols)
- **Impact**: Prevents one slow symbol from blocking entire batch

**File**: `argo/argo/core/signal_generation_service.py` (line 2610)

### 5. Added Global Cycle Timeout ⚡
- **Before**: No global timeout - cycles could run indefinitely
- **After**: 30s maximum timeout for entire cycle
- **Impact**: Ensures cycles complete within reasonable time, prevents hanging

**File**: `argo/argo/core/signal_generation_service.py` (line 3567)

### 6. Improved Early Exit Logic ⚡
- **Before**: Early exit only when feature flag enabled
- **After**: Always enabled, more aggressive (exits if partial confidence < 50%)
- **Impact**: Skips low-confidence signals faster, saves API calls and time

**File**: `argo/argo/core/signal_generation_service.py` (line 1089)

### 7. Enhanced Performance Logging 📊
- **Before**: Only logged successful cycles
- **After**: Warns when cycles take >10s with 0 signals
- **Impact**: Better visibility into performance issues

**File**: `argo/argo/core/signal_generation_service.py` (line 3581)

---

## Expected Improvements

### Performance Metrics:
- **Cycle Time**: 25s → **8-15s** (40-68% reduction)
- **Signals/Hour**: 1,364 → **2,400-3,600** (76-164% increase)
- **Timeout Failures**: Better handling, partial results used
- **Early Exits**: More aggressive, saves ~30-50% time on rejected signals

### Timeout Summary:
- Market data: 8s (was 20s)
- Remaining tasks: 5s (was 10s)
- Independent sources: 5s (new)
- Batch processing: 8s per symbol (new)
- Global cycle: 30s (new)

---

## Deployment

### To Deploy:
1. **Restart Unified Signal Generator**:
   ```bash
   ssh root@178.156.194.174
   systemctl restart argo-signal-generator.service
   ```

2. **Monitor Performance**:
   ```bash
   journalctl -u argo-signal-generator.service -f | grep -E "Generated|timeout|cycle"
   ```

3. **Verify Improvements**:
   ```bash
   python3 check_overnight_signals.py
   ```

---

## Monitoring

### Key Metrics to Watch:
- **Cycle duration**: Should be <15s (was ~25s)
- **Signals per hour**: Should be >2,400 (was ~1,364)
- **Timeout warnings**: Should see fewer, but better handled
- **Early exits**: Should see more early exits for low-confidence signals

### Expected Log Messages:
- `⚠️  Market data fetch timeout for {symbol} (8s timeout exceeded)` - Normal for slow sources
- `⚠️  Independent source fetch timeout for {symbol} (5s exceeded)` - Normal for slow AI sources
- `⏭️  Early exit: Partial confidence ({conf}%) too low for {symbol}` - Good, saves time
- `⚠️  Signal generation cycle took {time}s with 0 signals (performance issue)` - Warning if >10s

---

## Rollback Plan

If issues occur, revert changes:
```bash
cd /root/argo-production-unified
git checkout HEAD -- argo/argo/core/signal_generation_service.py
systemctl restart argo-signal-generator.service
```

---

## Next Steps

1. **Monitor for 24 hours** to verify improvements
2. **Tune timeouts** if needed based on actual performance
3. **Consider further optimizations**:
   - Reduce number of data sources for low-priority symbols
   - Implement adaptive timeout based on historical performance
   - Add circuit breakers for frequently failing sources

---

## Files Modified

- `argo/argo/core/signal_generation_service.py`
  - Lines 1313, 1370, 1432: Reduced market data timeouts
  - Lines 1518-1540: Added independent source timeout
  - Lines 2608-2626: Added batch processing timeout
  - Lines 3567, 3591-3605: Added global cycle timeout
  - Lines 1089-1120: Improved early exit logic
  - Line 3581: Enhanced performance logging

---

**Status**: ✅ Ready for deployment

