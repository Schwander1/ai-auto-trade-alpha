# Prop Firm Quick Start Guide

## ✅ Implementation Complete

All prop firm setup enhancements have been implemented and validated.

## Quick Start

### 1. Enable Prop Firm Mode

Edit `argo/config.json`:
```json
{
  "prop_firm": {
    "enabled": true
  }
}
```

**Important**: When prop firm mode is enabled, the system **automatically switches to the separate prop firm Alpaca account**. This ensures complete isolation from your regular trading accounts.

### 2. Validate Setup

```bash
cd argo
python scripts/validate_prop_firm_setup.py
```

Expected output:
```
✅ PROP FIRM SETUP VALIDATION PASSED
```

### 3. Start Trading

The system will automatically:
- ✅ Initialize risk monitor
- ✅ Enforce prop firm limits
- ✅ Monitor risk in real-time
- ✅ Block non-compliant trades
- ✅ Trigger emergency shutdown on breach

## What Was Implemented

### ✅ Core Components

1. **PropFirmRiskMonitor** (`argo/argo/risk/prop_firm_risk_monitor.py`)
   - Real-time risk monitoring
   - Portfolio correlation calculation
   - Emergency shutdown capabilities
   - Trading halt checks

2. **SignalGenerationService Integration** (`argo/argo/core/signal_generation_service.py`)
   - Pre-trade validation
   - Real-time equity updates
   - Position tracking
   - Risk monitor integration

3. **PaperTradingEngine Integration** (`argo/argo/core/paper_trading_engine.py`)
   - Prop firm position sizing
   - Stop loss enforcement
   - Confidence threshold enforcement
   - Symbol restrictions

4. **Configuration** (`argo/config.json`)
   - Complete prop firm section
   - Risk limits
   - Monitoring settings
   - Symbol restrictions

5. **Validation Script** (`argo/scripts/validate_prop_firm_setup.py`)
   - Config validation
   - Component testing
   - Comprehensive reporting

6. **Documentation**
   - Setup guide (`docs/PROP_FIRM_SETUP_GUIDE.md`)
   - Implementation details (`docs/PROP_FIRM_IMPLEMENTATION_COMPLETE.md`)

## Key Features

### Risk Limits (Conservative)
- **Max Drawdown**: 2.0% (vs 2.5% prop firm limit)
- **Daily Loss Limit**: 4.5% (vs 5.0% prop firm limit)
- **Max Position Size**: 3.0%
- **Min Confidence**: 82.0%
- **Max Positions**: 3
- **Max Stop Loss**: 1.5%

### Real-Time Monitoring
- Continuous monitoring every 5 seconds
- Drawdown tracking
- Daily P&L tracking
- Portfolio correlation analysis
- Risk level assessment

### Pre-Trade Validation
- Risk monitor status check
- Position count limits
- Confidence threshold
- Symbol restrictions
- Position size limits
- Stop loss limits

### Emergency Shutdown
- Automatic halt on breach
- Position closure
- Critical alerts
- Detailed logging

## Usage Examples

### Check Risk Monitor Status

```python
from argo.risk.prop_firm_risk_monitor import PropFirmRiskMonitor

config = {
    'max_drawdown_pct': 2.0,
    'daily_loss_limit_pct': 4.5,
    'initial_capital': 25000.0
}

monitor = PropFirmRiskMonitor(config)
monitor.update_equity(25000.0)

# Check if trading is allowed
can_trade, reason = monitor.can_trade()
print(f"Can trade: {can_trade}, Reason: {reason}")

# Get monitoring stats
stats = monitor.get_monitoring_stats()
print(f"Risk Level: {stats['current_risk_level']}")
print(f"Drawdown: {stats['current_drawdown']:.2f}%")
print(f"Daily P&L: {stats['daily_pnl_pct']:.2f}%")
```

### Start Monitoring

```python
import asyncio

async def main():
    monitor = PropFirmRiskMonitor(config)
    await monitor.start_monitoring()
    
    # Update equity as trades execute
    monitor.update_equity(25000.0)
    
    # Monitor will automatically check every 5 seconds
    await asyncio.sleep(60)  # Monitor for 60 seconds
    
    await monitor.stop_monitoring()

asyncio.run(main())
```

## Configuration

### Required Settings

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

## Validation

Run validation to ensure everything is working:

```bash
cd argo
python scripts/validate_prop_firm_setup.py
```

## Next Steps

1. ✅ **Enable prop firm mode** in config.json
2. ✅ **Run validation** to verify setup
3. ✅ **Paper trade** to test the system
4. ✅ **Monitor closely** during initial trades
5. ✅ **Review results** and adjust if needed

## Documentation

- **Setup Guide**: `docs/PROP_FIRM_SETUP_GUIDE.md`
- **Implementation Details**: `docs/PROP_FIRM_IMPLEMENTATION_COMPLETE.md`
- **Quick Start**: This document

## Support

For issues:
1. Run validation script
2. Check risk monitor logs
3. Review configuration
4. Consult documentation

---

**Status**: ✅ Ready for Use
**Last Updated**: 2025-01-XX
