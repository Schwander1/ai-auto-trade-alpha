# Prop Firm Setup Guide

Complete guide for setting up and using the prop firm trading system.

## Overview

The prop firm trading system provides:
- **Real-time risk monitoring** with automatic shutdown on breach
- **Pre-trade validation** enforcing prop firm limits
- **Position tracking** with correlation analysis
- **Emergency shutdown** capabilities
- **Comprehensive compliance** with prop firm rules

## Configuration

### 1. Enable Prop Firm Mode

Edit `config.json` and set:

```json
{
  "prop_firm": {
    "enabled": true,
    "account": "prop_firm_test",
    "risk_limits": {
      "max_drawdown_pct": 2.0,
      "daily_loss_limit_pct": 4.5,
      "max_position_size_pct": 3.0,
      "min_confidence": 82.0,
      "max_positions": 3,
      "max_stop_loss_pct": 1.5
    },
    "monitoring": {
      "enabled": true,
      "check_interval_seconds": 5,
      "alert_on_warning": true,
      "auto_shutdown": true
    },
    "symbols": {
      "allowed": ["SPY", "QQQ"],
      "restricted": ["AAPL", "NVDA", "TSLA"]
    }
  }
}
```

### 2. Configure Account

The prop firm account is already configured in `config.json`. When prop firm mode is enabled, the system **automatically uses the separate prop firm account** instead of the dev/production accounts.

**Important**: Prop firm trading uses a **separate Alpaca account** (`prop_firm_test`) that is isolated from your regular trading accounts. This ensures:
- ✅ Complete separation of prop firm trades from regular trades
- ✅ Independent risk monitoring and compliance tracking
- ✅ No interference between different trading strategies

The account configuration:
```json
{
  "alpaca": {
    "prop_firm_test": {
      "api_key": "PKM64P6DVTL6EGSGUD4567MKHN",
      "secret_key": "3qFDKEJQKtB8SBQ4XGkNi5UZj58siqSofQMh53uE5MHs",
      "paper": true,
      "account_name": "Prop Firm Test Account",
      "risk_limits": {
        "max_drawdown_pct": 2.0,
        "daily_loss_limit_pct": 4.5,
        "max_position_size_pct": 3.0,
        "min_confidence": 82.0,
        "max_positions": 3,
        "max_stop_loss_pct": 1.5
      }
    }
  }
}
```

**Account Selection Logic**:
- When `prop_firm.enabled = true` → Uses `prop_firm_test` account
- When `prop_firm.enabled = false` → Uses `dev` or `production` account (based on environment)

## Risk Limits

### Conservative Limits (Recommended)

- **Max Drawdown**: 2.0% (vs 2.5% prop firm limit)
- **Daily Loss Limit**: 4.5% (vs 5.0% prop firm limit)
- **Max Position Size**: 3.0% (conservative)
- **Min Confidence**: 82.0% (high quality signals only)
- **Max Positions**: 3 (diversification)
- **Max Stop Loss**: 1.5% (tight risk control)

### Why Conservative?

Prop firms have strict rules. Using conservative limits provides:
- **Safety buffer** before hitting actual limits
- **Reduced risk** of account termination
- **Better compliance** tracking
- **Peace of mind** during trading

## Components

### 1. PropFirmRiskMonitor

Real-time monitoring system that:
- Tracks drawdown continuously
- Monitors daily P&L
- Calculates portfolio correlation
- Provides risk level assessment
- Triggers emergency shutdown on breach

**Usage:**
```python
from argo.risk.prop_firm_risk_monitor import PropFirmRiskMonitor

config = {
    'max_drawdown_pct': 2.0,
    'daily_loss_limit_pct': 4.5,
    'initial_capital': 25000.0
}

monitor = PropFirmRiskMonitor(config)
await monitor.start_monitoring()

# Update equity as trades execute
monitor.update_equity(25000.0)

# Check if trading is allowed
can_trade, reason = monitor.can_trade()
```

### 2. SignalGenerationService Integration

The signal generation service automatically:
- Checks risk monitor before each trade
- Validates confidence thresholds
- Enforces position limits
- Validates symbol restrictions
- Updates risk monitor with positions

**No additional code needed** - works automatically when prop firm mode is enabled.

### 3. PaperTradingEngine Integration

The trading engine automatically:
- Uses prop firm position sizing
- Enforces confidence thresholds
- Applies prop firm stop loss limits
- Tracks positions for risk monitor

**No additional code needed** - works automatically when prop firm mode is enabled.

## Validation

### Run Validation Script

```bash
python argo/scripts/validate_prop_firm_setup.py
```

This validates:
- Configuration completeness
- Risk limit values
- Component integration
- Account setup

### Manual Checks

1. **Config Validation**
   ```bash
   python -c "import json; config = json.load(open('argo/config.json')); print('Prop firm enabled:', config.get('prop_firm', {}).get('enabled', False))"
   ```

2. **Risk Monitor Test**
   ```python
   from argo.risk.prop_firm_risk_monitor import PropFirmRiskMonitor
   monitor = PropFirmRiskMonitor({'max_drawdown_pct': 2.0, 'daily_loss_limit_pct': 4.5, 'initial_capital': 25000.0})
   monitor.update_equity(25000.0)
   can_trade, reason = monitor.can_trade()
   print(f"Can trade: {can_trade}, Reason: {reason}")
   ```

## Usage

### Starting Trading with Prop Firm Mode

1. **Enable prop firm mode** in `config.json`
2. **Run validation** to ensure setup is correct
3. **Start signal generation** service
4. **Monitor risk metrics** in real-time

### Monitoring Risk

The risk monitor provides real-time metrics:

```python
stats = monitor.get_monitoring_stats()
print(f"Risk Level: {stats['current_risk_level']}")
print(f"Drawdown: {stats['current_drawdown']:.2f}%")
print(f"Daily P&L: {stats['daily_pnl_pct']:.2f}%")
print(f"Open Positions: {stats['open_positions']}")
print(f"Trading Halted: {stats['trading_halted']}")
```

### Risk Levels

- **NORMAL**: All metrics within safe limits
- **WARNING**: Approaching limits (70% of max)
- **CRITICAL**: Near limits (90% of max) - risk reduction triggered
- **BREACH**: Limits exceeded - emergency shutdown

## Emergency Shutdown

When a breach is detected:

1. **Trading halted** immediately
2. **All positions closed** at market
3. **Critical alerts** sent
4. **Detailed state logged** for analysis
5. **Monitoring stopped**

The system will **not** resume trading until manually restarted after review.

## Best Practices

### 1. Start Conservative

- Use 2.0% max drawdown (vs 2.5% limit)
- Use 4.5% daily loss limit (vs 5.0% limit)
- Use 3% position size (vs 10% max)
- Use 82%+ confidence threshold

### 2. Monitor Continuously

- Check risk metrics every 5 seconds
- Review daily P&L regularly
- Watch for correlation buildup
- Monitor position count

### 3. Test Thoroughly

- Run backtests with prop firm constraints
- Paper trade before live trading
- Validate all components
- Test emergency shutdown

### 4. Stay Compliant

- Never exceed position limits
- Always use stop losses
- Monitor correlation
- Track all trades

## Troubleshooting

### Issue: Trading Blocked

**Cause**: Risk monitor detected breach or critical risk level

**Solution**:
1. Check risk monitor stats
2. Review drawdown and daily P&L
3. Close positions if needed
4. Wait for risk level to normalize

### Issue: Signals Rejected

**Cause**: Confidence too low or position limit reached

**Solution**:
1. Check signal confidence vs minimum (82%)
2. Verify position count vs maximum (3)
3. Review symbol restrictions
4. Check risk monitor status

### Issue: Position Size Too Small

**Cause**: Prop firm position size limit (3%) is conservative

**Solution**:
- This is intentional for prop firm compliance
- Consider increasing if backtests show it's safe
- Never exceed 10% per position

## Next Steps

1. **Validate Setup**: Run `validate_prop_firm_setup.py`
2. **Paper Trade**: Test with paper account first
3. **Monitor Closely**: Watch risk metrics during initial trades
4. **Review Results**: Analyze performance and compliance
5. **Adjust if Needed**: Fine-tune limits based on results

## Support

For issues or questions:
- Check validation script output
- Review risk monitor logs
- Consult backtesting results
- Review prop firm documentation

---

**Status**: ✅ Ready for paper trading

**Last Updated**: 2025-01-XX

