# Complete Trading Execution Guide

**Date:** January 15, 2025  
**Version:** 2.0  
**Status:** Complete Implementation Guide

---

## Executive Summary

This document provides a comprehensive guide to the Argo-Alpine trading execution system. It explains how trades are executed, how position sizing works, how orders are managed, and how to optimize execution for maximum profitability while minimizing costs.

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

The trading execution system executes trades on Alpaca paper trading, managing:
- Order submission (market/limit orders)
- Position sizing (confidence and volatility-based)
- Stop loss and take profit orders
- Order tracking and status monitoring
- Retry logic with exponential backoff

### Key Features

- **Environment-Aware**: Automatically selects dev/prod Alpaca accounts
- **Position Sizing**: Dynamic sizing based on confidence and volatility
- **Order Types**: Market and limit orders
- **Bracket Orders**: Automatic stop-loss and take-profit
- **Retry Logic**: Exponential backoff for failed orders
- **Order Tracking**: Complete order lifecycle tracking

---

## Architecture & Components

### Component Structure

```
Trading Execution System
├── PaperTradingEngine (Main Engine)
│   ├── execute_signal() - Execute trade from signal
│   ├── _execute_live() - Live Alpaca execution
│   ├── _execute_sim() - Simulation mode
│   ├── get_positions() - Fetch positions
│   └── get_order_status() - Track orders
├── Signal Generation Service (Integration)
│   └── Auto-execution integration
├── Position Monitoring (Background Task)
│   └── Monitor stop-loss/take-profit
└── Configuration (config.json)
    ├── Trading parameters
    ├── Order settings
    └── Retry logic
```

### File Locations

- **Main Engine**: `argo/argo/core/paper_trading_engine.py`
- **Integration**: `argo/argo/core/signal_generation_service.py`
- **Environment Detection**: `argo/argo/core/environment.py`

---

## How It Works

### Step 1: Signal to Trade Conversion

**Process**:
1. Signal generated with:
   - Symbol
   - Action (BUY/SELL)
   - Entry price
   - Confidence
   - Stop loss
   - Take profit
2. Signal passed to `execute_signal()`
3. Validated against risk management rules
4. Converted to trade order

**Validation**:
- Account status check
- Buying power check
- Risk limits check
- Market hours check (for stocks)

---

### Step 2: Position Sizing Calculation

**Process**:
1. Base position size: `position_size_pct` (default: 10%)
2. Confidence multiplier:
   - 75% confidence = 1.0x (base)
   - 100% confidence = 1.5x (max)
   - Formula: `1.0 + ((confidence - 75) / 25) * 0.5`
3. Volatility adjustment:
   - High volatility = Smaller position
   - Low volatility = Larger position
   - Formula: `min(avg_volatility / asset_volatility, 1.5)`
4. Final size: `base × confidence_mult × volatility_mult`
5. Capped at `max_position_size_pct` (default: 15%)

**Calculation Example**:
```
Buying Power: $100,000
Base Position Size: 10%
Confidence: 85% → Multiplier: 1.2x
Volatility: 1.5% (low) → Multiplier: 1.33x
Position Size: 10% × 1.2 × 1.33 = 16% (capped at 15%)
Position Value: $100,000 × 15% = $15,000
Entry Price: $150
Quantity: $15,000 / $150 = 100 shares
```

---

### Step 3: Order Type Selection

**Process**:
1. Check `use_limit_orders` config (default: false)
2. If limit orders enabled:
   - Calculate limit price with offset
   - BUY: `entry_price × (1 + offset_pct)`
   - SELL: `entry_price × (1 - offset_pct)`
   - Default offset: 0.1%
3. If market orders (default):
   - Execute immediately at market price
   - Faster execution, potential slippage

**Trade-off**:
- **Market Orders**: Faster, guaranteed execution, potential slippage
- **Limit Orders**: Better price, may not fill, slower

**Configuration**: `config.json` → `trading.use_limit_orders`

---

### Step 4: Order Submission

**Process**:
1. Create order request (MarketOrderRequest or LimitOrderRequest)
2. Submit to Alpaca API
3. Track order ID
4. Store order details in `_order_tracker`
5. Return order ID

**Order Details Tracked**:
- Order ID
- Symbol
- Side (BUY/SELL)
- Quantity
- Entry price
- Signal details
- Timestamp

---

### Step 5: Bracket Orders (Stop Loss / Take Profit)

**Process**:
1. After primary order fills, place bracket orders:
   - Stop loss order (if `stop_price` provided)
   - Take profit order (if `target_price` provided)
2. Stop loss: Closes position if price hits stop
3. Take profit: Closes position if price hits target

**Order Types**:
- **Stop Loss**: StopLossRequest (trailing or fixed)
- **Take Profit**: TakeProfitRequest (limit order)

**Configuration**: Automatic if signal includes stop/target prices

---

### Step 6: Order Tracking & Monitoring

**Process**:
1. Order status checked via `get_order_status()`
2. Position monitoring background task:
   - Checks positions every 30 seconds
   - Monitors stop-loss/take-profit levels
   - Auto-closes if targets hit
3. Order history tracked in `_order_tracker`

**Monitoring**:
- Order status (pending, filled, cancelled, rejected)
- Filled quantity
- Average fill price
- Position status

---

### Step 7: Retry Logic

**Process**:
1. If order fails, retry with exponential backoff
2. Retry attempts: `max_retry_attempts` (default: 3)
3. Delay: `retry_delay_seconds × (attempt_number)` (exponential)
4. After max retries, log error and return None

**Configuration**:
- `config.json` → `trading.max_retry_attempts` (default: 3)
- `config.json` → `trading.retry_delay_seconds` (default: 1)

---

## What Affects What

### Position Sizing → Risk & Returns

**Correlation**: Larger positions = Higher risk AND higher returns

**Factors**:
1. **Base Size** (`position_size_pct`): Base percentage
2. **Confidence**: Higher confidence = Larger size
3. **Volatility**: Higher volatility = Smaller size

**Optimization**: Test different base sizes, select based on Sharpe ratio

---

### Order Type → Execution Quality

**Correlation**: Limit orders = Better price, Market orders = Faster execution

**Trade-off**:
- **Market Orders**: Guaranteed fill, potential slippage (0.1% default)
- **Limit Orders**: Better price, may not fill, slower

**Optimization**: Test both, select based on fill rate and slippage

---

### Stop Loss / Take Profit → Win Rate vs. Profitability

**Correlation**: Tighter stops = Lower win rate BUT potentially higher profitability

**Trade-off**:
- **Tight Stop (2%)**: More exits, lower win rate, smaller losses
- **Wide Stop (5%)**: Fewer exits, higher win rate, larger losses
- **Optimal**: Balance win rate and profit factor

**Optimization**: Test different stop/target combinations, optimize for profit factor

---

### Retry Logic → Order Fill Rate

**Correlation**: More retries = Higher fill rate, but slower execution

**Trade-off**:
- **Few Retries (1-2)**: Faster, may miss fills
- **Many Retries (3-5)**: Slower, higher fill rate

**Optimization**: Balance fill rate and execution speed

---

## Configuration Guide

### Key Parameters in `config.json`

```json
{
  "trading": {
    "position_size_pct": 10,              // % - Base position size
    "max_position_size_pct": 15,          // % - Maximum position size
    "stop_loss": 0.03,                    // 3% - Stop loss per trade
    "profit_target": 0.05,                // 5% - Take profit per trade
    "use_limit_orders": false,            // Use limit vs. market orders
    "limit_order_offset_pct": 0.001,      // 0.1% - Limit order offset
    "max_retry_attempts": 3,              // Retry attempts
    "retry_delay_seconds": 1,             // Retry delay (seconds)
    "auto_execute": true                  // Auto-execute signals
  }
}
```

### How to Optimize Position Sizing

**Step 1: Test Different Base Sizes**
```python
# Test position sizes: 5%, 10%, 15%, 20%
# Run profit backtester for each
# Compare Sharpe ratio
```

**Step 2: Optimize Confidence Multiplier**
```python
# Current: 75% = 1.0x, 100% = 1.5x
# Test: 70% = 1.0x, 100% = 2.0x (more aggressive)
# Compare profitability
```

**Step 3: Optimize Volatility Adjustment**
```python
# Current: avg_volatility / asset_volatility
# Test: Different volatility windows (20-day, 30-day, 60-day)
# Compare risk-adjusted returns
```

---

### How to Optimize Order Types

**Step 1: Test Market vs. Limit Orders**
```python
# Test market orders (current)
# Test limit orders with 0.1% offset
# Compare: Fill rate, slippage, execution time
```

**Step 2: Optimize Limit Order Offset**
```python
# Test offsets: 0.05%, 0.1%, 0.2%, 0.5%
# Compare: Fill rate vs. price improvement
# Select optimal balance
```

---

### How to Optimize Stop Loss / Take Profit

**Step 1: Test Different Combinations**
```python
# Test combinations:
# Stop: 2%, 3%, 4%, 5%
# Target: 3%, 5%, 7%, 10%
# Compare: Win rate, profit factor, Sharpe ratio
```

**Step 2: Optimize for Profit Factor**
```python
# Focus on profit factor (gross profit / gross loss)
# Target: >2.0
# Not just win rate!
```

---

## Troubleshooting

### Issue: Orders not executing

**Possible Causes**:
1. Market closed (for stocks)
2. Insufficient buying power
3. Risk limits triggered
4. API connection issues

**Solution**:
1. Check market hours (stocks: 9:30 AM - 4:00 PM ET)
2. Check buying power
3. Check risk limit logs
4. Verify Alpaca API connection

**Prevention**: Monitor order execution rate, set up alerts

---

### Issue: Orders filling at bad prices (slippage)

**Possible Causes**:
1. Market orders during high volatility
2. Large position sizes
3. Low liquidity assets

**Solution**:
1. Use limit orders instead
2. Reduce position sizes
3. Avoid low liquidity assets
4. Optimize limit order offset

**Prevention**: Monitor slippage, adjust order type

---

### Issue: Orders not filling (limit orders)

**Possible Causes**:
1. Limit price too far from market
2. Market moved away
3. Insufficient liquidity

**Solution**:
1. Reduce limit order offset
2. Use market orders for fast-moving markets
3. Check asset liquidity

**Prevention**: Monitor fill rate, adjust offset

---

### Issue: Stop loss / take profit not triggering

**Possible Causes**:
1. Orders not placed correctly
2. Price gaps (stop loss)
3. Market closed

**Solution**:
1. Verify bracket orders placed
2. Check order status
3. Monitor position manually if needed

**Prevention**: Monitor position monitoring task, verify orders

---

### Issue: Position sizing too small/large

**Possible Causes**:
1. Base size too conservative/aggressive
2. Confidence multiplier too low/high
3. Volatility adjustment too aggressive

**Solution**:
1. Adjust `position_size_pct`
2. Adjust confidence multiplier formula
3. Adjust volatility calculation

**Prevention**: Monitor position sizes, optimize regularly

---

## Best Practices

### 1. Start with Market Orders

**Why**: Guaranteed execution, simpler

**How**: Use market orders initially, optimize later

**Benefit**: Faster execution, fewer issues

---

### 2. Optimize Position Sizing

**Why**: Critical for risk/return balance

**How**: Test different sizes, optimize for Sharpe ratio

**Benefit**: Optimal risk-adjusted returns

---

### 3. Monitor Execution Quality

**Why**: Need to detect slippage and fill issues

**How**: Track fill rate, slippage, execution time

**Benefit**: Early detection of issues

---

### 4. Test Order Types

**Why**: Different markets require different order types

**How**: Test market vs. limit orders, optimize offset

**Benefit**: Better execution quality

---

### 5. Optimize Stop/Target

**Why**: Critical for profitability

**How**: Test combinations, optimize for profit factor

**Benefit**: Better risk/reward balance

---

### 6. Monitor Order Status

**Why**: Need to track order lifecycle

**How**: Regular status checks, position monitoring

**Benefit**: Early detection of issues

---

### 7. Document Changes

**Why**: Need to track what changed and why

**How**: Document all execution parameter changes

**Benefit**: Easier troubleshooting and optimization

---

## Quick Reference: Trading Execution

### Default Settings

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `position_size_pct` | 10% | Base position size |
| `max_position_size_pct` | 15% | Maximum position size |
| `stop_loss` | 3% | Per-trade stop loss |
| `profit_target` | 5% | Per-trade take profit |
| `use_limit_orders` | false | Order type |
| `limit_order_offset_pct` | 0.1% | Limit order offset |
| `max_retry_attempts` | 3 | Retry attempts |
| `retry_delay_seconds` | 1 | Retry delay |

### Optimization Workflow

1. **Measure**: Track execution quality (fill rate, slippage)
2. **Test**: Test different parameters
3. **Optimize**: Select best parameters
4. **Deploy**: Update config.json
5. **Monitor**: Track improvement
6. **Iterate**: Repeat monthly

---

## Conclusion

Trading execution is **critical for profitability**. Proper configuration and optimization of execution parameters can significantly impact returns.

**Key Takeaways**:
1. Optimize position sizing for risk/return balance
2. Test order types (market vs. limit)
3. Optimize stop/target for profit factor
4. Monitor execution quality continuously
5. Test changes before deploying

**Remember**: Execution quality directly impacts profitability.

---

**For Questions**:  
Trading Execution: trading@alpineanalytics.com  
**Technical Support**: tech@alpineanalytics.com

