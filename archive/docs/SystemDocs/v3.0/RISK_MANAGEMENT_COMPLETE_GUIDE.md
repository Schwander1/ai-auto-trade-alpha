# Complete Risk Management Guide

**Date:** January 15, 2025  
**Version:** 2.0  
**Status:** Complete Implementation Guide

---

## Executive Summary

This document provides a comprehensive guide to the Argo-Alpine risk management system. It explains how the 7-layer risk protection system works, what affects what, and how to configure it to prevent losses while maximizing profitability. **Understanding and properly configuring risk management is critical for preventing catastrophic losses.**

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture & Components](#architecture--components)
3. [How It Works](#how-it-works)
4. [What Affects What](#what-affects-what)
5. [Configuration Guide](#configuration-guide)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## System Overview

### Purpose

The risk management system provides **7 layers of protection** to prevent catastrophic losses while allowing profitable trading:

1. **Account Status Checks** - Prevents trading on blocked accounts
2. **Confidence Thresholds** - Filters low-quality signals
3. **Position Size Limits** - Prevents over-concentration
4. **Correlation Limits** - Prevents correlated exposure
5. **Daily Loss Limits** - Circuit breaker for bad days
6. **Drawdown Protection** - Prevents excessive portfolio decline
7. **Buying Power Checks** - Ensures sufficient capital

### Key Principle

**Risk management is not about avoiding losses - it's about controlling losses while allowing profits.**

- No risk = No returns
- Too much risk = Catastrophic losses
- **Optimal risk = Controlled losses with maximum returns**

---

## Architecture & Components

### Component Structure

```
Risk Management System
├── Signal Generation Service (Risk Validation)
│   ├── _validate_trade() - Main validation function
│   ├── _check_daily_loss_limit() - Daily circuit breaker
│   ├── _check_correlation_groups() - Correlation limits
│   └── _update_peak_equity() - Drawdown tracking
├── Paper Trading Engine (Position Sizing)
│   ├── Position size calculation
│   ├── Volatility adjustment
│   └── Confidence-based sizing
└── Configuration (config.json)
    ├── Trading parameters
    ├── Risk limits
    └── Position sizing rules
```

### File Locations

- **Main Risk Logic**: `argo/argo/core/signal_generation_service.py`
  - `_validate_trade()` method (line ~478)
  - `_check_daily_loss_limit()` method (line ~460)
  - `_check_correlation_groups()` method (line ~430)
- **Position Sizing**: `argo/argo/core/paper_trading_engine.py`
  - `_execute_live()` method (line ~212)
- **Risk Manager**: `argo/argo/risk/risk_manager.py` (legacy, being phased out)

---

## How It Works

### Layer 1: Account Status Checks

**Purpose**: Prevents trading on blocked or restricted accounts

**How It Works**:
1. Fetches account details from Alpaca API
2. Checks `trading_blocked` flag
3. Checks `account_blocked` flag
4. Rejects trade if either is true

**Configuration**: None (automatic)

**What Happens If Failed**:
- Trade is rejected
- Logged: "Trading is blocked on account" or "Account is blocked"
- No position opened

---

### Layer 2: Confidence Thresholds

**Purpose**: Filters out low-quality signals

**How It Works**:
1. Signal generated with confidence score (0-100%)
2. Compares to `min_confidence` threshold (default: 75%)
3. Rejects if confidence < threshold

**Configuration**: `config.json` → `trading.min_confidence`

**What Happens If Failed**:
- Signal is not executed
- Logged: Signal generated but not traded
- No position opened

**Trade-off**:
- Higher threshold = Fewer trades, higher quality
- Lower threshold = More trades, lower quality

---

### Layer 3: Position Size Limits

**Purpose**: Prevents over-concentration in single positions

**How It Works**:
1. Calculates position size based on:
   - Base position size (`position_size_pct`, default: 10%)
   - Confidence multiplier (75% = 1.0x, 100% = 1.5x)
   - Volatility adjustment (high vol = smaller size)
2. Caps at `max_position_size_pct` (default: 15%)
3. Ensures sufficient buying power (leaves 5% buffer)

**Configuration**:
- `config.json` → `trading.position_size_pct` (default: 10%)
- `config.json` → `trading.max_position_size_pct` (default: 15%)

**What Happens If Failed**:
- Trade is rejected
- Logged: "Insufficient buying power"
- No position opened

**Calculation Example**:
```
Buying Power: $100,000
Base Position Size: 10%
Confidence: 85% → Multiplier: 1.2x
Volatility: Low → Multiplier: 1.0x
Position Size: 10% × 1.2 × 1.0 = 12%
Position Value: $100,000 × 12% = $12,000
```

---

### Layer 4: Correlation Limits

**Purpose**: Prevents over-exposure to correlated assets

**How It Works**:
1. Defines correlation groups (e.g., tech stocks, crypto)
2. Counts existing positions in same group
3. Rejects if count >= `max_correlated_positions` (default: 3)

**Configuration**: `config.json` → `trading.max_correlated_positions` (default: 3)

**Correlation Groups** (defined in code):
- **Tech Stocks**: AAPL, MSFT, GOOGL, META, NVDA, AMD, INTC
- **Crypto**: BTC-USD, ETH-USD, SOL-USD, AVAX-USD
- **Finance**: JPM, BAC
- **Energy**: XOM, CVX
- **ETFs**: SPY, QQQ, DIA, IWM, TLT

**What Happens If Failed**:
- Trade is rejected
- Logged: "Max correlated positions exceeded"
- No position opened

**Example**:
- Already have positions in: AAPL, MSFT, GOOGL (3 tech stocks)
- Signal for NVDA (tech stock) → Rejected (max 3 correlated)

---

### Layer 5: Daily Loss Limits

**Purpose**: Circuit breaker for bad trading days

**How It Works**:
1. Tracks daily starting equity
2. Calculates daily P&L percentage
3. Pauses trading if daily loss >= `daily_loss_limit_pct` (default: 5%)
4. Resets at start of new trading day

**Configuration**: `config.json` → `trading.daily_loss_limit_pct` (default: 5.0)

**What Happens If Triggered**:
- Trading is paused for the day
- All new trades rejected
- Logged: "Daily loss limit exceeded: X%"
- Resets automatically next day

**Calculation**:
```
Daily Start Equity: $100,000
Current Equity: $94,000
Daily Loss: ($94,000 - $100,000) / $100,000 = -6%
Daily Loss Limit: 5%
Result: Trading paused (6% > 5%)
```

---

### Layer 6: Drawdown Protection

**Purpose**: Prevents excessive portfolio decline from peak

**How It Works**:
1. Tracks peak equity (highest equity ever reached)
2. Calculates current drawdown: `(peak - current) / peak × 100`
3. Rejects trades if drawdown > `max_drawdown_pct` (default: 10%)

**Configuration**: `config.json` → `trading.max_drawdown_pct` (default: 10)

**What Happens If Triggered**:
- All new trades rejected
- Logged: "Max drawdown exceeded: X%"
- Trading resumes when drawdown < limit

**Calculation**:
```
Peak Equity: $110,000
Current Equity: $98,000
Drawdown: ($110,000 - $98,000) / $110,000 = 10.9%
Max Drawdown: 10%
Result: Trading paused (10.9% > 10%)
```

**Important**: Peak equity only increases, never decreases. This ensures drawdown is measured from the highest point.

---

### Layer 7: Buying Power Checks

**Purpose**: Ensures sufficient capital for trades

**How It Works**:
1. Calculates required capital for position
2. Checks available buying power
3. Ensures 5% buffer remains
4. Rejects if insufficient

**Configuration**: None (automatic, 5% buffer hardcoded)

**What Happens If Failed**:
- Trade is rejected
- Logged: "Insufficient buying power: need $X, have $Y"
- No position opened

---

## What Affects What

### Position Size → Risk & Returns

**Correlation**: Larger positions = Higher risk AND higher returns

**Trade-off**:
- 5% positions: Lower risk, lower returns
- 10% positions: Moderate risk, moderate returns
- 15% positions: Higher risk, higher returns

**Optimal**: Balance risk-adjusted returns (Sharpe ratio)

**Action**: Test different position sizes, select based on Sharpe ratio

---

### Daily Loss Limit → Trading Frequency

**Correlation**: Tighter limit = More frequent pauses, fewer trades

**Trade-off**:
- 3% limit: Very conservative, frequent pauses
- 5% limit: Balanced (default)
- 10% limit: Aggressive, fewer pauses

**Optimal**: 5% is standard for day trading

**Action**: Adjust based on risk tolerance and trading style

---

### Max Drawdown → Recovery Time

**Correlation**: Tighter limit = Faster recovery, more conservative

**Trade-off**:
- 5% limit: Very conservative, frequent pauses
- 10% limit: Balanced (default)
- 15% limit: Aggressive, allows larger declines

**Optimal**: 10% is standard for active trading

**Action**: Adjust based on risk tolerance

---

### Correlation Limits → Diversification

**Correlation**: Tighter limits = Better diversification, fewer trades

**Trade-off**:
- 2 positions: Very diversified, fewer opportunities
- 3 positions: Balanced (default)
- 5 positions: Less diversified, more opportunities

**Optimal**: 3 is standard for balanced diversification

**Action**: Adjust based on portfolio size and strategy

---

## Configuration Guide

### Key Parameters in `config.json`

```json
{
  "trading": {
    "min_confidence": 75.0,           // % - Minimum signal confidence
    "position_size_pct": 10,          // % - Base position size
    "max_position_size_pct": 15,      // % - Maximum position size
    "max_correlated_positions": 3,    // Count - Max correlated positions
    "max_drawdown_pct": 10,           // % - Maximum drawdown
    "daily_loss_limit_pct": 5.0,      // % - Daily loss limit
    "stop_loss": 0.03,                // 3% - Stop loss per trade
    "profit_target": 0.05             // 5% - Take profit per trade
  }
}
```

### How to Adjust for Different Risk Profiles

#### Conservative (Low Risk)
```json
{
  "min_confidence": 85.0,
  "position_size_pct": 5,
  "max_position_size_pct": 10,
  "max_correlated_positions": 2,
  "max_drawdown_pct": 5,
  "daily_loss_limit_pct": 3.0
}
```

#### Balanced (Default)
```json
{
  "min_confidence": 75.0,
  "position_size_pct": 10,
  "max_position_size_pct": 15,
  "max_correlated_positions": 3,
  "max_drawdown_pct": 10,
  "daily_loss_limit_pct": 5.0
}
```

#### Aggressive (High Risk)
```json
{
  "min_confidence": 70.0,
  "position_size_pct": 15,
  "max_position_size_pct": 20,
  "max_correlated_positions": 5,
  "max_drawdown_pct": 15,
  "daily_loss_limit_pct": 7.0
}
```

---

## Troubleshooting

### Issue: "Trading paused due to daily loss limit"

**Cause**: Daily loss exceeded the limit

**Solution**:
1. Wait until next trading day (resets automatically)
2. Or reduce `daily_loss_limit_pct` if too tight
3. Or improve signal quality to reduce losses

**Prevention**: Monitor daily P&L, adjust limit if needed

---

### Issue: "Max drawdown exceeded"

**Cause**: Portfolio declined too much from peak

**Solution**:
1. Wait for portfolio to recover (drawdown < limit)
2. Or increase `max_drawdown_pct` if too tight
3. Or improve strategy to reduce drawdowns

**Prevention**: Monitor drawdown, adjust limit if needed

---

### Issue: "Insufficient buying power"

**Cause**: Not enough capital for position

**Solution**:
1. Reduce `position_size_pct`
2. Close existing positions
3. Add more capital to account

**Prevention**: Monitor buying power, adjust position size

---

### Issue: "Max correlated positions exceeded"

**Cause**: Too many positions in same correlation group

**Solution**:
1. Close existing positions in same group
2. Or increase `max_correlated_positions`
3. Or wait for positions to close

**Prevention**: Monitor correlation groups, adjust limit if needed

---

### Issue: Trading paused but no clear reason

**Cause**: Multiple risk checks may have failed

**Solution**:
1. Check logs for specific error messages
2. Verify account status
3. Check all risk limits
4. Review recent trades for patterns

**Prevention**: Monitor logs regularly, set up alerts

---

## Best Practices

### 1. Start Conservative

**Why**: Better to be too conservative than too aggressive

**How**: Use conservative settings initially, gradually increase

**Benefit**: Prevents catastrophic losses while learning

---

### 2. Monitor Daily

**Why**: Risk limits can trigger unexpectedly

**How**: Check daily P&L, drawdown, and risk status

**Benefit**: Early detection of issues

---

### 3. Adjust Based on Performance

**Why**: Optimal settings vary by market conditions

**How**: Review performance monthly, adjust limits if needed

**Benefit**: Optimizes risk/return balance

---

### 4. Test Changes

**Why**: Risk changes can have unexpected effects

**How**: Test new settings on paper trading first

**Benefit**: Prevents costly mistakes

---

### 5. Document Changes

**Why**: Need to track what changed and why

**How**: Document all risk parameter changes

**Benefit**: Easier troubleshooting and optimization

---

### 6. Set Alerts

**Why**: Need to know when limits are triggered

**How**: Set up alerts for:
- Daily loss limit triggered
- Max drawdown exceeded
- Trading paused

**Benefit**: Immediate notification of issues

---

### 7. Review Regularly

**Why**: Risk parameters may need adjustment over time

**How**: Monthly review of:
- Risk limit effectiveness
- Trading frequency
- Performance impact

**Benefit**: Continuous optimization

---

## Quick Reference: Risk Limits

### Default Settings (Balanced)

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `min_confidence` | 75% | Filter low-quality signals |
| `position_size_pct` | 10% | Base position size |
| `max_position_size_pct` | 15% | Maximum position size |
| `max_correlated_positions` | 3 | Correlation limit |
| `max_drawdown_pct` | 10% | Drawdown protection |
| `daily_loss_limit_pct` | 5% | Daily circuit breaker |
| `stop_loss` | 3% | Per-trade stop loss |
| `profit_target` | 5% | Per-trade take profit |

### When to Adjust

**Increase Limits** (More Aggressive):
- Strategy performing well
- Want more trading opportunities
- Higher risk tolerance

**Decrease Limits** (More Conservative):
- Strategy underperforming
- Want fewer trades
- Lower risk tolerance
- Market volatility high

---

## Conclusion

Risk management is **critical for preventing catastrophic losses** while allowing profitable trading. The 7-layer protection system provides comprehensive coverage, but **proper configuration is essential**.

**Key Takeaways**:
1. Start conservative, gradually increase
2. Monitor daily, adjust as needed
3. Test changes before deploying
4. Document all changes
5. Review regularly

**Remember**: Risk management is not about avoiding losses - it's about controlling losses while allowing profits.

---

**For Questions**:  
Risk Management: risk@alpineanalytics.com  
**Technical Support**: tech@alpineanalytics.com

