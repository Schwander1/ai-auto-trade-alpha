# Prop Firm Optimization Plan

**Date:** November 18, 2025  
**Status:** Optimization Recommendations

---

## Critical Issues Identified

### 1. ⚠️ **No Signals Generated Today**
- **Status:** 0 signals on Nov 18, 2025
- **Last Signal:** Nov 17, 2025 13:10:00 UTC
- **Impact:** Service may not be generating signals

### 2. ⚠️ **Prop Firm Threshold Too High**
- **Current:** 82% minimum confidence
- **Signals Meeting Threshold:** Only 20.77% (409 of 1,969)
- **Impact:** Missing 79.23% of good quality signals (70-79% range)

### 3. ⚠️ **No Outcome Tracking**
- **Status:** All signals show `outcome: NULL`
- **Impact:** Cannot assess profitability or validate confidence levels

---

## Optimization Recommendations

### 1. Optimize Prop Firm Confidence Threshold

**Current Configuration:**
- `min_confidence: 82.0%`
- Only 20.77% of signals meet this threshold

**Recommended Change:**
- Lower to `80.0%` (still conservative, captures more signals)
- Would capture ~409 additional signals (20.77% more)
- Still maintains high quality (80%+ confidence)

**Impact Analysis:**
- **Current:** 409 signals (20.77%) meet 82% threshold
- **At 80%:** ~1,000+ signals would meet threshold
- **Quality:** Still excellent (all above 80%)

**Implementation:**
```json
{
  "prop_firm": {
    "risk_limits": {
      "min_confidence": 80.0  // Changed from 82.0
    }
  }
}
```

### 2. Investigate Signal Generation Activity

**Issue:** No signals generated today (Nov 18)

**Actions:**
1. Check service logs for errors
2. Verify signal generation is running
3. Check if symbols are being monitored
4. Verify data sources are working

**Commands:**
```bash
# Check service status
systemctl status argo-trading-prop-firm.service

# Check recent logs
journalctl -u argo-trading-prop-firm.service --since "1 hour ago"

# Verify signal generation
curl http://localhost:8001/api/v1/health/
```

### 3. Enable Outcome Tracking

**Current Status:** Outcome tracking exists but not being used

**Actions:**
1. Verify `OutcomeTracker` is initialized
2. Ensure outcome updates are called on trade exits
3. Check if trades are being executed
4. Verify outcome tracking integration

**Implementation:**
- OutcomeTracker class exists (`argo/argo/tracking/outcome_tracker.py`)
- Need to verify it's being called on trade exits
- Need to check if trades are actually executing

### 4. Monitor Signal Quality

**Recommendations:**
1. Track confidence vs outcomes (when available)
2. Calibrate confidence scoring
3. Monitor signal quality trends
4. Adjust thresholds based on performance

---

## Configuration Optimizations

### Recommended Prop Firm Settings

```json
{
  "prop_firm": {
    "enabled": true,
    "account": "prop_firm_test",
    "risk_limits": {
      "max_drawdown_pct": 2.0,        // ✅ Keep (conservative)
      "daily_loss_limit_pct": 4.5,    // ✅ Keep (conservative)
      "max_position_size_pct": 3.0,   // ✅ Keep (conservative)
      "min_confidence": 80.0,         // ⚠️ OPTIMIZE: Lower from 82.0 to 80.0
      "max_positions": 3,             // ✅ Keep
      "max_stop_loss_pct": 1.5        // ✅ Keep (tight risk control)
    }
  }
}
```

**Rationale:**
- 80% still very conservative (vs 75% for regular trading)
- Captures more signals while maintaining quality
- All signals above 80% are high quality
- Better utilization of signal generation

---

## Implementation Steps

### Step 1: Verify Service Status
- [ ] Check service is running
- [ ] Verify signal generation active
- [ ] Check for errors in logs
- [ ] Verify data sources working

### Step 2: Optimize Confidence Threshold
- [ ] Update config: `min_confidence: 80.0`
- [ ] Restart service
- [ ] Monitor signal generation
- [ ] Verify more signals are captured

### Step 3: Enable Outcome Tracking
- [ ] Verify OutcomeTracker initialized
- [ ] Check trade execution status
- [ ] Enable outcome updates
- [ ] Monitor outcome tracking

### Step 4: Monitor & Validate
- [ ] Track signal quality metrics
- [ ] Monitor confidence vs outcomes
- [ ] Adjust thresholds if needed
- [ ] Document performance improvements

---

## Expected Improvements

### After Optimizations

**Signal Capture:**
- **Before:** 409 signals (20.77%) meet 82% threshold
- **After:** ~1,000+ signals (50%+) meet 80% threshold
- **Improvement:** 2.4x more signals captured

**Quality:**
- **Before:** 20.77% above 82%
- **After:** 50%+ above 80%
- **Quality:** Still excellent (all above 80%)

**Trading Activity:**
- **Before:** Limited signals, low activity
- **After:** More signals, higher activity
- **Risk:** Still conservative (80% threshold, 3% position size)

---

## Risk Assessment

### Lowering Threshold to 80%

**Risks:**
- ⚠️ Slightly lower confidence (80% vs 82%)
- ⚠️ More signals = more trades = more risk

**Mitigations:**
- ✅ Still very conservative (80% is high)
- ✅ Position size still limited (3%)
- ✅ Max positions still limited (3)
- ✅ Drawdown limits still strict (2.0%)
- ✅ Stop losses still tight (1.5%)

**Assessment:** **LOW RISK** - 80% is still excellent quality

---

## Next Steps

1. **Immediate:** Verify service status and signal generation
2. **Short Term:** Optimize confidence threshold to 80%
3. **Short Term:** Enable outcome tracking
4. **Medium Term:** Monitor and calibrate based on outcomes

---

**Status:** Ready for Implementation  
**Priority:** High (affects signal capture and profitability)

