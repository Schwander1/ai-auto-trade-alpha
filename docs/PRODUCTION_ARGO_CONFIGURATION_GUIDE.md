# Production ARGO Configuration Guide

**Date:** January 2025  
**Status:** Complete Configuration Guide  
**Purpose:** Ensure prop trading and regular trading are properly configured with signal generation and backtesting strategies

---

## Executive Summary

This guide ensures that ARGO is properly configured for both prop trading and regular trading in production, with both using signal generation and having appropriate strategies from backtesting applied.

---

## Key Findings

### ✅ Signal Generation

**Both prop trading and regular trading use signal generation:**

1. **SignalGenerationService** (`argo/argo/core/signal_generation_service.py`)
   - Generates signals every 5 seconds
   - Uses Weighted Consensus v6.0 algorithm
   - Multi-source aggregation (6 data sources)
   - **Used by both prop and regular trading**

2. **Prop Trading Signal Generation:**
   - Uses same SignalGenerationService
   - Higher confidence threshold (82%+ vs 75%+)
   - Stricter risk limits applied via PropFirmRiskMonitor
   - Account switching to prop_firm_test account

3. **Regular Trading Signal Generation:**
   - Uses same SignalGenerationService
   - Standard confidence threshold (75%+)
   - Standard risk limits
   - Uses dev/production account

### ✅ Backtesting Strategies

**Two different strategies are applied from backtesting:**

1. **Prop Trading Strategy** (`PropFirmBacktester`):
   - **Min Confidence:** 80-82% (higher threshold)
   - **Max Drawdown:** 2.0% (conservative)
   - **Daily Loss Limit:** 4.5%
   - **Max Position Size:** 3.0% (conservative)
   - **Max Positions:** 3
   - **Max Stop Loss:** 1.5%

2. **Regular Trading Strategy** (`StrategyBacktester`):
   - **Min Confidence:** 75% (standard threshold)
   - **Max Drawdown:** 10% (standard)
   - **Daily Loss Limit:** 5.0%
   - **Max Position Size:** 15% (standard)
   - **Max Positions:** Varies
   - **Stop Loss:** 3.0%

---

## Configuration Structure

### Prop Trading Configuration

**Location:** `/root/argo-production-prop-firm/config.json` (or prop firm service config)

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
    }
  },
  "strategy": {
    "use_multi_source": true,
    "weight_massive": 0.4,
    "weight_alpha_vantage": 0.25,
    "weight_x_sentiment": 0.2,
    "weight_sonar": 0.15
  },
  "trading": {
    "auto_execute": true,
    "min_confidence": 82.0,
    "consensus_threshold": 82.0,
    "profit_target": 0.05,
    "stop_loss": 0.015,
    "position_size_pct": 3,
    "max_position_size_pct": 3,
    "max_correlated_positions": 3,
    "max_drawdown_pct": 2.0,
    "daily_loss_limit_pct": 4.5
  },
  "alpaca": {
    "prop_firm_test": {
      "api_key": "FROM_AWS_SECRETS",
      "secret_key": "FROM_AWS_SECRETS",
      "paper": true
    }
  }
}
```

### Regular Trading Configuration

**Location:** `/root/argo-production-green/config.json` (or regular trading service config)

```json
{
  "prop_firm": {
    "enabled": false
  },
  "strategy": {
    "use_multi_source": true,
    "weight_massive": 0.4,
    "weight_alpha_vantage": 0.25,
    "weight_x_sentiment": 0.2,
    "weight_sonar": 0.15
  },
  "trading": {
    "auto_execute": true,
    "min_confidence": 75.0,
    "consensus_threshold": 75.0,
    "profit_target": 0.05,
    "stop_loss": 0.03,
    "position_size_pct": 10,
    "max_position_size_pct": 15,
    "max_correlated_positions": 3,
    "max_drawdown_pct": 10,
    "daily_loss_limit_pct": 5.0
  },
  "alpaca": {
    "production": {
      "api_key": "FROM_AWS_SECRETS",
      "secret_key": "FROM_AWS_SECRETS",
      "paper": true
    }
  }
}
```

---

## Verification

### Automated Verification

Run the verification script to check configuration:

```bash
# Check configuration
python argo/scripts/verify_production_argo_config.py

# Check and auto-fix issues
python argo/scripts/verify_production_argo_config.py --fix

# Check specific config file
python argo/scripts/verify_production_argo_config.py --config-path /path/to/config.json
```

### Manual Verification Checklist

#### Prop Trading Verification

- [ ] `prop_firm.enabled = true`
- [ ] `prop_firm.risk_limits.min_confidence >= 82.0`
- [ ] `prop_firm.risk_limits.max_drawdown_pct <= 2.0`
- [ ] `prop_firm.risk_limits.max_position_size_pct <= 3.0`
- [ ] `prop_firm.account` exists in `alpaca` section
- [ ] `strategy.use_multi_source = true`
- [ ] Signal generation service is running
- [ ] PropFirmRiskMonitor is initialized

#### Regular Trading Verification

- [ ] `prop_firm.enabled = false` (or missing)
- [ ] `trading.min_confidence >= 75.0`
- [ ] `trading.max_drawdown_pct <= 10.0`
- [ ] `trading.max_position_size_pct <= 15.0`
- [ ] `strategy.use_multi_source = true`
- [ ] Signal generation service is running
- [ ] Standard risk monitoring is active

---

## How Signal Generation Works

### Signal Generation Flow

1. **SignalGenerationService** runs every 5 seconds
2. Generates signals for monitored symbols using:
   - Multi-source data aggregation
   - Weighted Consensus v6.0 algorithm
   - Market regime detection
   - Confidence threshold filtering

3. **Prop Trading:**
   - Signals filtered by higher confidence threshold (82%+)
   - Additional risk checks via PropFirmRiskMonitor
   - Stricter position sizing (3% max)
   - Executed on prop_firm_test account

4. **Regular Trading:**
   - Signals filtered by standard confidence threshold (75%+)
   - Standard risk checks
   - Standard position sizing (10-15%)
   - Executed on production account

### Signal Generation Components

- **SignalGenerationService** (`argo/argo/core/signal_generation_service.py`)
  - Main service that generates signals
  - Used by both prop and regular trading
  - Detects prop firm mode and applies appropriate thresholds

- **WeightedConsensusEngine** (`argo/argo/core/weighted_consensus_engine.py`)
  - Combines multiple data sources
  - Calculates weighted consensus
  - Applies market regime adjustments

- **PropFirmRiskMonitor** (`argo/argo/risk/prop_firm_risk_monitor.py`)
  - Additional risk checks for prop trading
  - Monitors drawdown and daily loss limits
  - Enforces prop firm constraints

---

## Backtesting Strategy Application

### Prop Trading Strategy (PropFirmBacktester)

**Applied Parameters:**
- Min Confidence: 80-82%
- Max Drawdown: 2.0%
- Daily Loss Limit: 4.5%
- Max Position Size: 3.0%
- Max Positions: 3
- Max Stop Loss: 1.5%

**Backtester:** `argo/argo/backtest/prop_firm_backtester.py`

**Usage:**
```python
from argo.backtest.prop_firm_backtester import PropFirmBacktester

backtester = PropFirmBacktester(
    initial_capital=25000.0,
    min_confidence=82.0,
    max_drawdown_pct=2.0,
    daily_loss_limit_pct=4.5,
    max_position_size_pct=3.0
)
```

### Regular Trading Strategy (StrategyBacktester)

**Applied Parameters:**
- Min Confidence: 75%
- Max Drawdown: 10%
- Daily Loss Limit: 5.0%
- Max Position Size: 15%
- Max Positions: Varies
- Stop Loss: 3.0%

**Backtester:** `argo/argo/backtest/strategy_backtester.py`

**Usage:**
```python
from argo.backtest.strategy_backtester import StrategyBacktester

backtester = StrategyBacktester(
    initial_capital=100000.0,
    min_confidence=75.0
)
```

---

## Production Deployment

### Dual Service Setup

**Regular Trading Service:**
- Port: 8000
- Config: `/root/argo-production-green/config.json`
- `prop_firm.enabled = false`
- Account: Production account

**Prop Trading Service:**
- Port: 8001
- Config: `/root/argo-production-prop-firm/config.json`
- `prop_firm.enabled = true`
- Account: prop_firm_test account

### Service Files

**Regular Trading:**
- `infrastructure/systemd/argo-trading.service`

**Prop Trading:**
- `infrastructure/systemd/argo-trading-prop-firm.service`

---

## Troubleshooting

### Issue: Prop Trading Not Using Signal Generation

**Symptoms:**
- No signals generated for prop trading
- Prop trading not executing trades

**Solution:**
1. Verify `prop_firm.enabled = true` in config
2. Check SignalGenerationService is running
3. Verify prop_firm_test account credentials
4. Check PropFirmRiskMonitor is initialized

### Issue: Regular Trading Not Using Signal Generation

**Symptoms:**
- No signals generated for regular trading
- Regular trading not executing trades

**Solution:**
1. Verify `prop_firm.enabled = false` in config
2. Check SignalGenerationService is running
3. Verify production account credentials
4. Check standard risk monitoring is active

### Issue: Wrong Strategy Applied

**Symptoms:**
- Prop trading using regular trading parameters
- Regular trading using prop trading parameters

**Solution:**
1. Verify correct config file is loaded
2. Check `prop_firm.enabled` flag
3. Verify account selection logic
4. Restart service to reload config

---

## Best Practices

### DO

- ✅ Always verify configuration before deployment
- ✅ Use separate config files for prop and regular trading
- ✅ Run verification script after configuration changes
- ✅ Test signal generation in both modes
- ✅ Monitor both services independently
- ✅ Use backtesting to validate strategy parameters

### DON'T

- ❌ Share accounts between prop and regular trading
- ❌ Use same risk limits for both modes
- ❌ Skip verification after config changes
- ❌ Deploy without testing signal generation
- ❌ Mix prop and regular trading configurations

---

## Related Documentation

- [PROP_FIRM_SETUP_GUIDE.md](PROP_FIRM_SETUP_GUIDE.md) - Prop firm setup
- [PROP_FIRM_DEPLOYMENT_GUIDE.md](PROP_FIRM_DEPLOYMENT_GUIDE.md) - Prop firm deployment
- [SIGNAL_GENERATION_AND_TRADING_FLOW.md](SIGNAL_GENERATION_AND_TRADING_FLOW.md) - Signal generation flow
- [BACKTESTING_COMPLETE_GUIDE.md](SystemDocs/BACKTESTING_COMPLETE_GUIDE.md) - Backtesting guide
- [Rules/13_TRADING_OPERATIONS.md](../../Rules/13_TRADING_OPERATIONS.md) - Trading operations rules

---

## Summary

✅ **Both prop trading and regular trading use signal generation** via SignalGenerationService

✅ **Two different strategies are applied from backtesting:**
- Prop Trading: Conservative (82% confidence, 2% drawdown, 3% position size)
- Regular Trading: Standard (75% confidence, 10% drawdown, 15% position size)

✅ **Configuration is properly separated:**
- Prop trading: `prop_firm.enabled = true` with strict limits
- Regular trading: `prop_firm.enabled = false` with standard limits

✅ **Both services run independently:**
- Regular trading: Port 8000, production account
- Prop trading: Port 8001, prop_firm_test account

