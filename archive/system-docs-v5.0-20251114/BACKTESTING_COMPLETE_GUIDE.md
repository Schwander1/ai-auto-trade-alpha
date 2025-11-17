# Complete Backtesting Framework Guide

**Date:** January 15, 2025  
**Version:** 2.0  
**Status:** Complete Implementation Guide

---

## Executive Summary

This document provides a comprehensive guide to the Argo-Alpine backtesting framework. It explains how the system is set up, how it's used, what affects what, and the correlations between different components. Most importantly, it details **how to focus on specific areas to improve profitability** and signal quality.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture & Components](#architecture--components)
3. [How It Works](#how-it-works)
4. [What Affects What](#what-affects-what)
5. [Improving Profitability](#improving-profitability)
6. [Improving Signal Quality](#improving-signal-quality)
7. [Correlations & Dependencies](#correlations--dependencies)
8. [Usage Guide](#usage-guide)
9. [Best Practices](#best-practices)

---

## System Overview

### Purpose

The backtesting framework serves **two distinct purposes**:

1. **Strategy Backtester** (Alpine - Signal Quality)
   - Tests signal generation quality
   - Focus: Win rate, confidence accuracy
   - For: Customer-facing signal quality

2. **Profit Backtester** (Argo - Trading Profitability)
   - Tests trading profitability
   - Focus: Returns, Sharpe ratio, drawdown
   - For: Internal trading optimization

### Key Principle

**Strategy quality ≠ Trading profitability**

- High win rate signals can still lose money (poor execution, slippage, fees)
- Low win rate signals can still be profitable (good risk/reward, position sizing)
- **Both must be optimized separately**

---

## Architecture & Components

### Component Structure

```
Backtesting Framework
├── BaseBacktester (Abstract Base Class)
│   ├── StrategyBacktester (Signal Quality)
│   └── ProfitBacktester (Trading Profitability)
├── DataManager (Historical Data)
├── ParameterOptimizer (Grid Search)
├── WalkForwardTester (Rolling Windows)
└── ResultsStorage (Metrics Storage)
```

### File Locations

- **Base Class**: `argo/argo/backtest/base_backtester.py`
- **Strategy Backtester**: `argo/argo/backtest/strategy_backtester.py`
- **Profit Backtester**: `argo/argo/backtest/profit_backtester.py`
- **Data Manager**: `argo/argo/backtest/data_manager.py`
- **Optimizer**: `argo/argo/backtest/optimizer.py`
- **Walk-Forward**: `argo/argo/backtest/walk_forward.py`
- **Results Storage**: `argo/argo/backtest/results_storage.py`

---

## How It Works

### 1. Strategy Backtester (Signal Quality)

**Purpose**: Test how good our signals are at predicting price movements

**Process**:
1. Fetch historical data for a symbol
2. For each day in history:
   - Generate signal using Weighted Consensus Engine
   - Check if signal meets confidence threshold (75%+)
   - Enter position if BUY signal
   - Exit position if SELL signal or stop/target hit
3. Calculate metrics: win rate, average return, Sharpe ratio

**Key Metrics**:
- **Win Rate**: % of profitable trades
- **Average Return**: Average % return per signal
- **Sharpe Ratio**: Risk-adjusted returns
- **Confidence Accuracy**: How well confidence predicts success

**What It Tests**:
- Signal generation quality
- Confidence calibration
- Strategy effectiveness
- Data source weights

**For**: Alpine customers (signal quality)

---

### 2. Profit Backtester (Trading Profitability)

**Purpose**: Test how profitable our trading is after execution costs

**Process**:
1. Use Strategy Backtester to generate trades
2. Copy all trades to Profit Backtester
3. Apply execution costs:
   - Slippage (0.1% default)
   - Commission (0.1% default)
4. Apply risk management:
   - Position sizing (10% base, 15% max)
   - Stop loss (3%)
   - Take profit (5%)
5. Recalculate metrics with costs applied

**Key Metrics**:
- **Total Return**: % return after costs
- **Sharpe Ratio**: Risk-adjusted returns
- **Max Drawdown**: Largest peak-to-trough decline
- **Profit Factor**: Gross profit / Gross loss

**What It Tests**:
- Trading profitability
- Execution quality
- Risk management effectiveness
- Position sizing optimization

**For**: Argo internal trading (profitability)

---

### 3. Data Manager

**Purpose**: Fetch, validate, and cache historical data

**Process**:
1. Check cache for existing data
2. If not cached, fetch from yfinance
3. Clean and validate data
4. Cache for future use

**Data Sources**:
- **Primary**: yfinance (free, reliable)
- **Cached**: Local CSV files
- **Period**: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max

**Data Quality**:
- Removes duplicates
- Validates prices (no negative/zero)
- Ensures High >= Low
- Checks for missing data

---

### 4. Parameter Optimizer

**Purpose**: Find optimal parameters using grid search

**Process**:
1. Define parameter grid (e.g., min_confidence: [70, 75, 80, 85])
2. Test all combinations
3. Run backtest for each combination
4. Select best based on objective (Sharpe ratio, win rate, etc.)

**Objectives**:
- **sharpe_ratio**: Risk-adjusted returns
- **win_rate**: % of profitable trades
- **total_return**: Total % return
- **sortino_ratio**: Downside risk-adjusted returns
- **profit_factor**: Gross profit / Gross loss

---

### 5. Walk-Forward Tester

**Purpose**: Validate strategy robustness across time periods

**Process**:
1. Define training window (e.g., 252 days = 1 year)
2. Define test window (e.g., 63 days = 1 quarter)
3. Define step size (e.g., 21 days = 1 month)
4. For each window:
   - Train on training period
   - Test on test period
   - Record metrics
5. Analyze consistency across windows

**Benefits**:
- Tests strategy robustness
- Prevents overfitting
- Validates across different market conditions

---

## What Affects What

### Signal Quality (Strategy Backtester)

**What Affects Win Rate**:
1. **Data Source Weights** (`config.json` → `strategy` section)
   - Massive: 40% weight
   - Alpha Vantage: 25% weight
   - X Sentiment: 20% weight
   - Sonar AI: 15% weight
   - **Action**: Adjust weights based on performance

2. **Consensus Threshold** (`config.json` → `trading.consensus_threshold`)
   - Default: 75%
   - Higher = fewer signals, higher quality
   - Lower = more signals, lower quality
   - **Action**: Optimize threshold for best win rate

3. **Min Confidence** (`config.json` → `trading.min_confidence`)
   - Default: 75%
   - Filters out low-confidence signals
   - **Action**: Adjust to balance quantity vs. quality

4. **Regime Detection** (Automatic)
   - Detects market regime (BULL, BEAR, CHOP, CRISIS)
   - Adjusts strategy weights automatically
   - **Action**: Monitor regime detection accuracy

**What Affects Confidence Accuracy**:
1. **Data Source Quality**: Better data = better confidence
2. **Historical Performance**: Past accuracy affects confidence
3. **Regime Alignment**: Confidence higher when regime matches strategy

---

### Trading Profitability (Profit Backtester)

**What Affects Total Return**:
1. **Position Sizing** (`config.json` → `trading.position_size_pct`)
   - Default: 10% base, 15% max
   - Larger positions = higher returns (and risk)
   - **Action**: Optimize for best risk-adjusted returns

2. **Stop Loss** (`config.json` → `trading.stop_loss`)
   - Default: 3%
   - Tighter = less risk, more exits
   - Wider = more risk, fewer exits
   - **Action**: Balance risk vs. opportunity

3. **Take Profit** (`config.json` → `trading.profit_target`)
   - Default: 5%
   - Higher = fewer exits, larger wins
   - Lower = more exits, smaller wins
   - **Action**: Optimize for best risk/reward

4. **Execution Costs** (`config.json` → `backtest.execution`)
   - Slippage: 0.1% default
   - Commission: 0.1% default
   - **Action**: Minimize costs (better execution, lower fees)

5. **Volatility Adjustment** (Automatic)
   - Adjusts position size based on asset volatility
   - Higher volatility = smaller positions
   - **Action**: Monitor volatility calculations

---

## Improving Profitability

### Focus Areas for Profitability

#### 1. Position Sizing Optimization

**What to Change**: `config.json` → `trading.position_size_pct` and `max_position_size_pct`

**How to Test**:
```python
# Run profit backtester with different position sizes
position_sizes = [5, 10, 15, 20, 25]  # %
for size in position_sizes:
    # Update config
    # Run profit backtest
    # Compare Sharpe ratio
```

**What to Look For**:
- **Sharpe Ratio**: Higher is better (risk-adjusted returns)
- **Max Drawdown**: Lower is better (risk control)
- **Total Return**: Higher is better (but consider risk)

**Correlation**:
- Larger positions → Higher returns AND higher drawdown
- Optimal = Best Sharpe ratio (not highest return)

**Action Items**:
1. Run grid search on position sizes (5% to 25%)
2. Test on multiple symbols
3. Select size with best Sharpe ratio
4. Update `config.json`

---

#### 2. Stop Loss / Take Profit Optimization

**What to Change**: `config.json` → `trading.stop_loss` and `trading.profit_target`

**How to Test**:
```python
# Test different stop/target combinations
stop_losses = [0.02, 0.03, 0.04, 0.05]  # 2-5%
take_profits = [0.03, 0.05, 0.07, 0.10]  # 3-10%

for stop in stop_losses:
    for target in take_profits:
        # Run profit backtest
        # Compare profit factor
```

**What to Look For**:
- **Profit Factor**: Gross profit / Gross loss (target: >2.0)
- **Win Rate**: % of profitable trades
- **Average Win/Loss Ratio**: Should be >1.0

**Correlation**:
- Tighter stop = More exits, lower win rate, but smaller losses
- Wider target = Fewer exits, higher average win
- Optimal = Best profit factor (not highest win rate)

**Action Items**:
1. Run grid search on stop/target combinations
2. Focus on profit factor (not just win rate)
3. Test on multiple symbols
4. Update `config.json`

---

#### 3. Execution Cost Reduction

**What to Change**: Execution method, order types, timing

**Current Costs**:
- Slippage: 0.1% (default in backtest)
- Commission: 0.1% (default in backtest)

**How to Reduce**:
1. **Use Limit Orders**: `config.json` → `trading.use_limit_orders = true`
   - Reduces slippage
   - May miss some trades (limit not hit)

2. **Optimize Entry Timing**: Enter at better prices
   - Use limit orders with small offset
   - Wait for pullbacks

3. **Reduce Commission**: Negotiate lower fees
   - Use commission-free brokers where possible
   - Negotiate volume discounts

**Action Items**:
1. Test limit orders vs. market orders
2. Optimize limit order offset (`limit_order_offset_pct`)
3. Monitor actual execution costs
4. Update backtest costs to match reality

---

#### 4. Volatility-Based Position Sizing

**What It Does**: Automatically adjusts position size based on asset volatility

**How It Works**:
- Calculate asset volatility (rolling standard deviation)
- Compare to average volatility (2% default)
- Reduce position size for high volatility assets
- Increase position size for low volatility assets

**What to Change**: Volatility calculation method, average volatility assumption

**Action Items**:
1. Monitor volatility calculations
2. Adjust average volatility assumption if needed
3. Test different volatility windows (20-day, 30-day, 60-day)

---

#### 5. Risk Management Optimization

**What to Change**: Risk limits in `config.json`

**Key Parameters**:
- `max_drawdown_pct`: 10% (stop trading if drawdown exceeds)
- `daily_loss_limit_pct`: 5% (stop trading for the day)
- `max_correlated_positions`: 3 (limit correlated exposure)

**How to Test**:
1. Run backtest with different risk limits
2. Compare total return vs. max drawdown
3. Find optimal balance

**Action Items**:
1. Test different drawdown limits (5%, 10%, 15%)
2. Test different daily loss limits (3%, 5%, 7%)
3. Monitor actual risk in live trading
4. Adjust limits based on results

---

## Improving Signal Quality

### Focus Areas for Signal Quality

#### 1. Data Source Weight Optimization

**What to Change**: `config.json` → `strategy` section weights

**Current Weights**:
- Massive: 40%
- Alpha Vantage: 25%
- X Sentiment: 20%
- Sonar AI: 15%

**How to Optimize**:
1. Run strategy backtests with different weight combinations
2. Measure win rate for each combination
3. Select weights with highest win rate

**Example Grid Search**:
```python
weights = {
    'massive': [0.30, 0.35, 0.40, 0.45, 0.50],
    'alpha_vantage': [0.20, 0.25, 0.30],
    'x_sentiment': [0.15, 0.20, 0.25],
    'sonar': [0.10, 0.15, 0.20]
}
# Test all combinations
# Select best win rate
```

**Correlation**:
- Higher weight on better-performing source → Higher win rate
- But: Need to test on multiple symbols and time periods
- Avoid overfitting to one symbol/period

**Action Items**:
1. Run grid search on data source weights
2. Test on multiple symbols
3. Use walk-forward testing to validate
4. Update `config.json` with optimal weights

---

#### 2. Consensus Threshold Optimization

**What to Change**: `config.json` → `trading.consensus_threshold`

**Current**: 75%

**How to Test**:
```python
thresholds = [70, 75, 80, 85, 90]  # %
for threshold in thresholds:
    # Run strategy backtest
    # Compare win rate vs. signal count
```

**Correlation**:
- Higher threshold → Fewer signals, higher win rate
- Lower threshold → More signals, lower win rate
- Optimal = Best balance (win rate × signal count)

**Action Items**:
1. Test different thresholds (70% to 90%)
2. Plot win rate vs. signal count
3. Select threshold with best balance
4. Update `config.json`

---

#### 3. Min Confidence Optimization

**What to Change**: `config.json` → `trading.min_confidence`

**Current**: 75%

**How to Test**:
```python
confidences = [70, 75, 80, 85, 90]  # %
for confidence in confidences:
    # Run strategy backtest
    # Compare win rate
```

**Correlation**:
- Higher min confidence → Higher win rate, fewer signals
- Lower min confidence → Lower win rate, more signals
- Optimal = Best win rate while maintaining signal volume

**Action Items**:
1. Test different min confidence levels
2. Focus on win rate improvement
3. Ensure sufficient signal volume
4. Update `config.json`

---

#### 4. Regime Detection Accuracy

**What It Does**: Automatically detects market regime and adjusts strategy

**Regimes**:
- **BULL**: Rising market, buy signals favored
- **BEAR**: Falling market, sell signals favored
- **CHOP**: Sideways market, mean reversion favored
- **CRISIS**: High volatility, risk-off mode

**How to Improve**:
1. Monitor regime detection accuracy
2. Adjust regime detection parameters
3. Test regime-specific strategies
4. Optimize regime transition detection

**Action Items**:
1. Review regime detection logs
2. Validate regime classifications
3. Test regime-specific optimizations
4. Improve transition detection

---

## Correlations & Dependencies

### Signal Quality → Trading Profitability

**Correlation**: High signal quality (win rate) generally leads to higher profitability, BUT:

**Important**: High win rate ≠ High profitability

**Why**:
- Execution costs reduce profitability
- Poor risk management can turn winning signals into losses
- Position sizing affects returns more than win rate

**Example**:
- 80% win rate, 2% avg win, 3% avg loss = Negative expectancy
- 60% win rate, 5% avg win, 2% avg loss = Positive expectancy

**Action**: Optimize BOTH signal quality AND execution/risk management

---

### Position Sizing → Profitability

**Correlation**: Larger positions = Higher returns AND higher risk

**Trade-off**:
- 5% positions: Lower returns, lower drawdown
- 10% positions: Moderate returns, moderate drawdown
- 20% positions: Higher returns, higher drawdown

**Optimal**: Best Sharpe ratio (risk-adjusted returns)

**Action**: Test different position sizes, select based on Sharpe ratio

---

### Stop Loss → Win Rate vs. Profitability

**Correlation**: Tighter stops = Lower win rate BUT potentially higher profitability

**Why**:
- Tighter stops = More exits (lower win rate)
- But: Smaller losses = Better risk/reward
- Result: Higher profit factor despite lower win rate

**Action**: Focus on profit factor, not just win rate

---

### Data Source Weights → Signal Quality

**Correlation**: Better-performing sources with higher weights = Higher win rate

**Dependency**:
- Source performance varies by market regime
- Need to test across multiple regimes
- Avoid overfitting to one period

**Action**: Use walk-forward testing to validate weight optimization

---

## Usage Guide

### Running a Strategy Backtest

```python
from argo.backtest.strategy_backtester import StrategyBacktester
from datetime import datetime

backtester = StrategyBacktester(initial_capital=100000)

# Run backtest
metrics = await backtester.run_backtest(
    symbol="AAPL",
    start_date=datetime(2020, 1, 1),
    end_date=datetime(2024, 1, 1),
    min_confidence=75.0
)

print(f"Win Rate: {metrics.win_rate_pct}%")
print(f"Sharpe Ratio: {metrics.sharpe_ratio}")
```

### Running a Profit Backtest

```python
from argo.backtest.profit_backtester import ProfitBacktester

backtester = ProfitBacktester(
    initial_capital=100000,
    slippage_pct=0.001,
    commission_pct=0.001
)

# Run backtest
metrics = await backtester.run_backtest(
    symbol="AAPL",
    start_date=datetime(2020, 1, 1),
    end_date=datetime(2024, 1, 1),
    min_confidence=75.0
)

print(f"Total Return: {metrics.total_return_pct}%")
print(f"Max Drawdown: {metrics.max_drawdown_pct}%")
print(f"Profit Factor: {metrics.profit_factor}")
```

### Running Parameter Optimization

```python
from argo.backtest.optimizer import ParameterOptimizer
from argo.backtest.strategy_backtester import StrategyBacktester

backtester = StrategyBacktester()
optimizer = ParameterOptimizer(backtester)

# Define parameter grid
param_grid = {
    'min_confidence': [70, 75, 80, 85],
    'position_size_pct': [5, 10, 15, 20]
}

# Run optimization
results = await optimizer.grid_search(
    symbol="AAPL",
    param_grid=param_grid,
    objective="sharpe_ratio"
)

print(f"Best Parameters: {results['best_params']}")
print(f"Best Score: {results['best_score']}")
```

### Running Walk-Forward Test

```python
from argo.backtest.walk_forward import WalkForwardTester
from argo.backtest.strategy_backtester import StrategyBacktester

backtester = StrategyBacktester()
wf_tester = WalkForwardTester(
    backtester=backtester,
    train_days=252,  # 1 year
    test_days=63,    # 1 quarter
    step_days=21     # 1 month
)

# Run walk-forward
results = await wf_tester.run_walk_forward(
    symbol="AAPL",
    start_date=datetime(2020, 1, 1),
    end_date=datetime(2024, 1, 1)
)

# Get summary
summary = wf_tester.get_summary()
print(f"Average Return: {summary['avg_return']}%")
print(f"Consistency: {summary['consistency']}")
```

---

## Best Practices

### 1. Always Use Walk-Forward Testing

**Why**: Prevents overfitting to one time period

**How**: Test strategy across multiple time windows

**Benefit**: Validates strategy robustness

---

### 2. Test on Multiple Symbols

**Why**: Strategy may work on one symbol but fail on others

**How**: Run backtests on 10+ different symbols

**Benefit**: Ensures strategy is generalizable

---

### 3. Focus on Risk-Adjusted Metrics

**Why**: High returns with high risk may not be sustainable

**Metrics to Focus On**:
- **Sharpe Ratio**: Risk-adjusted returns (target: >2.0)
- **Sortino Ratio**: Downside risk-adjusted returns
- **Max Drawdown**: Largest loss (target: <10%)

**Avoid**: Focusing only on total return

---

### 4. Consider Execution Costs

**Why**: Real trading has costs that affect profitability

**Costs to Include**:
- Slippage: 0.1% (default)
- Commission: 0.1% (default)
- Market impact: Varies by position size

**Action**: Always run profit backtests (not just strategy backtests)

---

### 5. Validate with Out-of-Sample Data

**Why**: In-sample optimization can overfit

**How**:
1. Optimize on training period (e.g., 2020-2022)
2. Validate on test period (e.g., 2023-2024)
3. Only use if test period performs well

**Benefit**: Ensures strategy works on unseen data

---

## Quick Reference: What to Change for Specific Goals

### Goal: Increase Profitability

**Focus On**:
1. **Position Sizing**: Optimize `position_size_pct` (5-25%)
2. **Stop Loss/Take Profit**: Optimize `stop_loss` and `profit_target`
3. **Execution Costs**: Use limit orders, reduce slippage
4. **Risk Management**: Optimize `max_drawdown_pct` and `daily_loss_limit_pct`

**Test With**: Profit Backtester
**Optimize For**: Sharpe Ratio, Profit Factor

---

### Goal: Increase Signal Quality (Win Rate)

**Focus On**:
1. **Data Source Weights**: Optimize weights in `strategy` section
2. **Consensus Threshold**: Optimize `consensus_threshold` (70-90%)
3. **Min Confidence**: Optimize `min_confidence` (70-90%)
4. **Regime Detection**: Improve regime detection accuracy

**Test With**: Strategy Backtester
**Optimize For**: Win Rate, Confidence Accuracy

---

### Goal: Balance Quality and Quantity

**Focus On**:
1. **Consensus Threshold**: Lower = more signals, higher = better quality
2. **Min Confidence**: Balance signal volume vs. quality
3. **Data Source Weights**: Optimize for best win rate × signal count

**Test With**: Strategy Backtester
**Optimize For**: Win Rate × Signal Count

---

## Configuration Reference

### Key Parameters in `config.json`

```json
{
  "strategy": {
    "weight_massive": 0.4,           // 0-1, affects signal quality
    "weight_alpha_vantage": 0.25,    // 0-1, affects signal quality
    "weight_x_sentiment": 0.2,       // 0-1, affects signal quality
    "weight_sonar": 0.15             // 0-1, affects signal quality
  },
  "trading": {
    "min_confidence": 75.0,          // %, affects signal quality
    "consensus_threshold": 75.0,     // %, affects signal quality
    "position_size_pct": 10,         // %, affects profitability
    "max_position_size_pct": 15,     // %, affects profitability
    "stop_loss": 0.03,               // 3%, affects profitability
    "profit_target": 0.05,           // 5%, affects profitability
    "max_drawdown_pct": 10,          // %, affects risk
    "daily_loss_limit_pct": 5.0      // %, affects risk
  },
  "backtest": {
    "execution": {
      "slippage_pct": 0.001,         // 0.1%, affects profitability
      "commission_pct": 0.001        // 0.1%, affects profitability
    }
  }
}
```

---

## Conclusion

The backtesting framework is a powerful tool for optimizing both signal quality and trading profitability. By understanding what affects what, you can:

1. **Improve Signal Quality**: Optimize data source weights, consensus threshold, min confidence
2. **Improve Profitability**: Optimize position sizing, stop loss/take profit, execution costs
3. **Balance Both**: Use walk-forward testing and multiple symbols to find optimal parameters

**Remember**: Signal quality and trading profitability are related but distinct. Optimize both separately for best results.

---

**For Questions**:  
Technical: tech@alpineanalytics.com  
**Backtesting**: backtesting@alpineanalytics.com

