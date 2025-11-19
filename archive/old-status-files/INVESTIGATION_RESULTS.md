# Investigation Results - Signal Storage & Prop Firm

## Historical Signal Analysis

**Single Historical Signal Found:**
- **Signal ID**: 2ce3c3fc36020ad5
- **Symbol**: AAPL
- **Action**: BUY
- **Confidence**: 92.5%
- **Timestamp**: 2025-11-12T04:40:07.435855
- **Strategy**: alpine_consensus
- **Age**: 6 days ago (November 12, 2025)

## Issues Found

### 1. Signal Storage Issue
- Only 1 signal stored in database (from 6 days ago)
- No recent signals being stored despite generation activity
- Batch flush mechanism may not be working correctly
- Signals may be filtered out before storage (confidence threshold, validation)

### 2. Prop Firm Configuration
- **Argo Service**: Prop firm disabled (correct - should be standard trading)
- **Prop Firm Service**: Prop firm enabled (correct)
- Both services have auto-execute and 24/7 mode enabled

### 3. Service Status
- **Argo Service**: ✅ ACTIVE, prop_firm_enabled: false
- **Prop Firm Service**: ✅ ACTIVE, prop_firm_enabled: true
- Both services connected to Alpaca
- Both services have background tasks running

## Fixes Applied

1. ✅ Updated both config files to ensure proper prop firm settings
2. ✅ Restarted both services
3. ✅ Verified prop firm service is in prop firm mode
4. ✅ Verified argo service is in standard mode

## Next Steps

1. Monitor signal generation and storage
2. Check why signals aren't being stored (batch flush, validation)
3. Verify both services are generating and storing signals
4. Monitor trade execution for both services

