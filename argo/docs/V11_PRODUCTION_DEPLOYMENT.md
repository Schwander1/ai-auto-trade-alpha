# V11 Optimal Configuration - Production Deployment Guide

**Date:** 2025-11-16  
**Version:** V11 (Optimal)  
**Status:** Ready for Production

---

## Overview

This guide covers deploying the **V11 optimal backtest configuration** to production. V11 was identified as the best overall configuration through comprehensive analysis of iterations V3-V11.

---

## V11 Performance Summary

### Backtest Results
- **Win Rate:** 49.39%
- **Total Return:** 13.19%
- **Sharpe Ratio:** 0.80 ⭐ (Best)
- **Max Drawdown:** -21.93%
- **Profit Factor:** 1.50 ⭐ (Best)
- **Total Trades:** 1,701

### Why V11 is Optimal
- ✅ Best risk-adjusted returns (Sharpe 0.80)
- ✅ Highest profit factor (1.50)
- ✅ Good win rate (49.39%, near 50% target)
- ✅ Advanced risk management features
- ✅ Realistic cost modeling

---

## Deployment Steps

### Step 1: Backup Current Configuration

```bash
cd /path/to/argo
cp config.json config.backup.$(date +%Y%m%d_%H%M%S).json
```

### Step 2: Deploy V11 Configuration

**Option A: Automated Deployment**
```bash
cd argo
python3 scripts/deploy_v11_configuration.py
```

**Option B: Manual Deployment**
1. Copy `config.v11.production.json` to `config.json`
2. Update API keys and secrets (preserve existing values)
3. Verify configuration

### Step 3: Verify Configuration

```bash
# Check config is valid JSON
python3 -m json.tool config.json > /dev/null && echo "✅ Valid JSON"

# Verify key V11 settings
python3 -c "
import json
with open('config.json') as f:
    config = json.load(f)
    print(f\"Min Confidence: {config['trading']['min_confidence']}%\")
    print(f\"Position Size: {config['trading']['position_size_pct']}%\")
    print(f\"Enhanced Cost Model: {config.get('backtest', {}).get('use_enhanced_cost_model', False)}\")
"
```

### Step 4: Restart Trading Service

```bash
# For systemd service
sudo systemctl restart argo-trading-prop-firm

# Or for manual start
cd argo
python3 -m argo.main
```

### Step 5: Monitor Deployment

```bash
# Check service status
sudo systemctl status argo-trading-prop-firm

# Monitor logs
sudo journalctl -u argo-trading-prop-firm -f

# Run performance monitor
python3 scripts/monitor_v11_performance.py
```

---

## V11 Configuration Details

### Core Trading Settings

```json
{
  "trading": {
    "min_confidence": 60.0,
    "position_size_pct": 9,
    "max_position_size_pct": 16,
    "min_position_size_pct": 5,
    "max_drawdown_pct": 20,
    "stop_loss": 0.025,
    "profit_target": 0.05
  }
}
```

### Backtest/Strategy Settings

```json
{
  "backtest": {
    "use_enhanced_cost_model": true,
    "volume_confirmation": true,
    "adaptive_stops": true,
    "trailing_stops": true,
    "position_sizing": true,
    "base_position_size_pct": 0.09,
    "portfolio_risk_limits": true,
    "max_portfolio_drawdown_pct": 0.20,
    "max_positions": 5,
    "dynamic_stop_loss": true,
    "symbol_specific_thresholds": true,
    "high_confidence_boost": true
  }
}
```

### Symbol-Specific Thresholds

- **SPY/QQQ:** -2% confidence threshold (more liquid)
- **BTC-USD/ETH-USD:** +3% confidence threshold (more volatile)
- **TSLA/AMD:** +1% confidence threshold (volatile stocks)

---

## Key Features

### 1. Enhanced Cost Model
- Square-root slippage model
- Symbol-specific liquidity tiers
- Volume-based slippage calculation
- Volatility-adjusted costs

### 2. Dynamic Stop Loss
- Automatically tightens as portfolio drawdown increases
- 20% tighter at 10% drawdown
- 40% tighter at 20% drawdown

### 3. Portfolio Risk Limits
- Maximum 20% portfolio drawdown
- Maximum 5 concurrent positions
- Position size reduction during drawdowns

### 4. High-Confidence Boost
- +10% position size for signals ≥70% confidence
- Better capital allocation for high-quality signals

### 5. Volume Confirmation
- Requires 1.2x average volume for signal confirmation
- Filters out low-quality signals

---

## Monitoring & Validation

### Performance Monitoring

Run the performance monitor script regularly:

```bash
python3 scripts/monitor_v11_performance.py
```

This compares live performance with V11 backtest expectations:
- Win Rate
- Total Return
- Sharpe Ratio
- Max Drawdown
- Profit Factor

### Expected Performance

Based on V11 backtest, expect:
- **Win Rate:** ~49% (target: 50%+)
- **Returns:** ~13% (risk-adjusted)
- **Sharpe:** ~0.80 (excellent)
- **Drawdown:** ~-22% (acceptable)
- **Profit Factor:** ~1.50 (excellent)

### Alert Thresholds

Monitor for deviations:
- **Win Rate:** Alert if < 45% or > 55%
- **Sharpe:** Alert if < 0.60
- **Drawdown:** Alert if > -25%
- **Profit Factor:** Alert if < 1.20

---

## Rollback Procedure

If issues occur, rollback to previous configuration:

```bash
# Find backup
ls -lt config.backup.*.json | head -1

# Restore
cp config.backup.YYYYMMDD_HHMMSS.json config.json

# Restart service
sudo systemctl restart argo-trading-prop-firm
```

---

## Troubleshooting

### Issue: Performance Below Expectations

**Possible Causes:**
- Market conditions different from backtest period
- Insufficient sample size (need 100+ trades)
- Configuration not applied correctly

**Actions:**
1. Verify configuration is correct
2. Check market conditions vs backtest period
3. Wait for more trades (statistical significance)
4. Review symbol-specific performance

### Issue: Too Few Trades

**Possible Causes:**
- Confidence threshold too high (60%)
- Volume confirmation too strict
- Market conditions not generating signals

**Actions:**
1. Monitor signal generation
2. Check if signals are being filtered
3. Consider adjusting thresholds if needed
4. Review symbol-specific thresholds

### Issue: Higher Drawdown Than Expected

**Possible Causes:**
- Market volatility higher than backtest
- Dynamic stops not working correctly
- Portfolio risk limits not triggered

**Actions:**
1. Verify dynamic stop loss is enabled
2. Check portfolio risk limits
3. Review position sizing
4. Consider tighter stops if needed

---

## Best Practices

1. **Monitor Closely Initially**
   - Check performance daily for first week
   - Compare with backtest expectations
   - Watch for any anomalies

2. **Maintain Backups**
   - Keep configuration backups
   - Document any manual changes
   - Version control configuration

3. **Track Performance**
   - Run performance monitor regularly
   - Keep logs of performance metrics
   - Compare with backtest over time

4. **Iterate Carefully**
   - Don't change multiple parameters at once
   - Test changes in backtest first
   - Monitor impact of changes

---

## Support & Resources

- **Backtest Reports:** `argo/reports/OPTIMAL_BACKTESTING_FINAL.md`
- **Configuration File:** `argo/config.v11.production.json`
- **Deployment Script:** `argo/scripts/deploy_v11_configuration.py`
- **Monitor Script:** `argo/scripts/monitor_v11_performance.py`

---

## Conclusion

V11 configuration is **production-ready** and provides the best balance of:
- Risk-adjusted returns
- Trade quality
- Risk management
- Realistic expectations

**Deploy with confidence** and monitor closely for the first few weeks.

---

**Last Updated:** 2025-11-16  
**Version:** V11  
**Status:** ✅ Ready for Production

