# Complete Backtesting Framework Guide v5.0

**Date:** January 15, 2025  
**Version:** 5.0  
**Status:** Complete Implementation Guide with v5.0 Enhancements

---

## Executive Summary

This document provides a comprehensive guide to the Argo-Alpine backtesting framework with v5.0 enhancements. It explains how the system is set up, how it's used, what affects what, and the correlations between different components. Most importantly, it details **realistic cost modeling, out-of-sample testing, and proper validation procedures**.

---

## v5.0 Enhancements

### Realistic Cost Modeling

**All backtests now include realistic trading costs:**
- **Slippage:** 0.05% (price movement between signal and execution)
- **Spread:** 0.02% (bid-ask spread)
- **Commission:** 0.1% (broker fee per trade)

**Total Round-Trip Cost:** ~0.17% per trade

**Impact:**
- More realistic accuracy reporting (10-15% reduction expected)
- Legally defensible results
- Accounts for real trading costs

### Out-of-Sample Testing

**Three-Set Data Split:**
- **Training (60%):** Used for optimization only
- **Validation (20%):** Used for validation only
- **Test (20%):** Used for measurement only (OUT-OF-SAMPLE)

**Rule:** ONLY report test set results to customers

### Confidence Calibration Integration

**File:** `argo/argo/backtest/calibrated_backtester.py`

**Features:**
- Trains calibrator on training set only
- Validates on validation set
- Tests on test set (out-of-sample)
- Compares calibrated vs uncalibrated results

### Market Regime Analysis

**File:** `argo/argo/backtest/market_regime_analyzer.py`

**Features:**
- Analyzes market characteristics by period
- Compares different market regimes
- Estimates expected accuracy ranges
- Documents regime-specific performance

---

## System Overview

### Purpose

The backtesting framework serves **two distinct purposes**:

1. **Strategy Backtester** (Alpine - Signal Quality)
   - Tests signal generation quality
   - Focus: Win rate, confidence accuracy
   - **v5.0:** Includes realistic costs
   - **v5.0:** Out-of-sample testing only

2. **Profit Backtester** (Argo - Trading Profitability)
   - Tests trading profitability
   - Focus: Returns, Sharpe ratio, drawdown
   - **v5.0:** Includes realistic costs
   - For: Internal trading optimization

### Key Principle

**Strategy quality ≠ Trading profitability**

- High win rate signals can still lose money (poor execution, slippage, fees)
- Low win rate signals can still be profitable (good risk/reward, position sizing)
- **Both must be optimized separately**

---

## Architecture & Components

### Component Structure (v5.0)

```
Backtesting Framework v5.0
├── BaseBacktester (Abstract Base Class)
│   ├── StrategyBacktester (Signal Quality - v5.0: Cost modeling)
│   ├── ProfitBacktester (Trading Profitability)
│   └── EnhancedBacktester (Cost modeling base)
├── CalibratedBacktester (v5.0: Calibration integration)
├── MarketRegimeAnalyzer (v5.0: Regime analysis)
├── DataManager (Historical Data)
├── ParameterOptimizer (Grid Search)
├── WalkForwardTester (Rolling Windows)
└── ResultsStorage (Metrics Storage)
```

### File Locations

- **Base Class**: `argo/argo/backtest/base_backtester.py`
- **Strategy Backtester**: `argo/argo/backtest/strategy_backtester.py` (v5.0: Enhanced)
- **Profit Backtester**: `argo/argo/backtest/profit_backtester.py`
- **Calibrated Backtester**: `argo/argo/backtest/calibrated_backtester.py` (v5.0: New)
- **Market Regime Analyzer**: `argo/argo/backtest/market_regime_analyzer.py` (v5.0: New)
- **Data Manager**: `argo/argo/backtest/data_manager.py`
- **Optimizer**: `argo/argo/backtest/optimizer.py`
- **Walk-Forward**: `argo/argo/backtest/walk_forward.py`

---

## How It Works

### 1. Strategy Backtester (v5.0 Enhanced)

**Purpose**: Test how good our signals are at predicting price movements

**v5.0 Enhancements:**
- Realistic cost modeling (slippage, spread, commission)
- Three-set data split (train/val/test)
- Out-of-sample testing only

**Process**:
1. Split data into train/val/test sets
2. Fetch historical data for a symbol
3. For each day in TEST SET (out-of-sample):
   - Generate signal using Weighted Consensus Engine
   - Check if signal meets confidence threshold (75%+)
   - Enter position if BUY signal (with costs applied)
   - Exit position if SELL signal or stop/target hit (with costs applied)
4. Calculate metrics: win rate, average return, Sharpe ratio

**Key Metrics**:
- **Win Rate**: % of profitable trades (with costs)
- **Average Return**: Average % return per signal (with costs)
- **Sharpe Ratio**: Risk-adjusted returns
- **Confidence Accuracy**: How well confidence predicts success

**v5.0 Cost Application:**
```python
# Entry (LONG)
Entry Price = Close Price + Slippage + Spread/2 + Commission

# Exit (LONG)
Exit Price = Target/Stop Price - Slippage - Spread/2 - Commission
```

### 2. Profit Backtester

**Purpose**: Test trading profitability with full execution simulation

**v5.0:** Already includes costs (maintained)

**Process**:
1. Use Strategy Backtester to generate signals
2. Apply execution costs (slippage, spread, commission)
3. Calculate profitability metrics

**Key Metrics**:
- **Total Return**: % return over period
- **Sharpe Ratio**: Risk-adjusted returns
- **Max Drawdown**: Largest peak-to-trough decline
- **Profit Factor**: Gross profit / Gross loss

### 3. Calibrated Backtester (v5.0 New)

**Purpose**: Test confidence calibration effectiveness

**Process**:
1. Train calibrator on training set only
2. Validate on validation set
3. Test on test set (out-of-sample)
4. Compare calibrated vs uncalibrated results

**Key Metrics**:
- **Calibration Improvement**: Win rate improvement from calibration
- **Accuracy Alignment**: How well calibrated confidence matches actual win rates

### 4. Market Regime Analyzer (v5.0 New)

**Purpose**: Analyze market characteristics and set realistic expectations

**Process**:
1. Analyze market characteristics for different periods
2. Compare regimes (e.g., 2023-2024 vs 2025-11-15)
3. Estimate expected accuracy ranges
4. Document regime-specific performance

**Key Metrics**:
- **Volatility**: Annualized volatility
- **Trend Strength**: Trend alignment percentage
- **Trading Difficulty**: Easy/Moderate/Difficult/Very Difficult
- **Expected Accuracy Range**: Min/Expected/Max accuracy

---

## Out-of-Sample Testing Procedure

### Three-Set Data Split

**Rule:** ALWAYS use three-set split for strategy validation

**Split:**
- **Training (60%):** 2023-2024 - Used for optimization only
- **Validation (20%):** 2025-01 to 2025-09 - Used for validation only
- **Test (20%):** 2025-10-01 onwards - Used for measurement only

**Implementation:**
```python
from argo.backtest import StrategyBacktester

backtester = StrategyBacktester()
train_df, val_df, test_df = backtester.split_data(df, train_pct=0.6, val_pct=0.2, test_pct=0.2)

# Run on test set only (out-of-sample)
metrics = await backtester.run_backtest(
    symbol="AAPL",
    start_date=test_df.index[0],
    end_date=test_df.index[-1]
)
```

### Data Leakage Prevention

**Rules:**
- ✅ Training data: Used for optimization only
- ✅ Validation data: Used for validation only
- ✅ Test data: Used for measurement only (never for optimization)
- ❌ Never optimize on test data
- ❌ Never use future data to predict past

---

## Cost Modeling

### Cost Parameters

| Cost Type | Value | Description |
|-----------|-------|-------------|
| **Slippage** | 0.05% | Price movement between signal and execution |
| **Spread** | 0.02% | Bid-ask spread (0.01% on entry, 0.01% on exit) |
| **Commission** | 0.1% | Broker commission per trade |

**Total Round-Trip Cost:** ~0.17% per trade

### Cost Application

**Entry (LONG):**
```
Entry Price = Close Price + Slippage + Spread/2 + Commission
```

**Exit (LONG):**
```
Exit Price = Target/Stop Price - Slippage - Spread/2 - Commission
```

**Impact on Accuracy:**
- Without costs: ~95% accuracy (unrealistic)
- With costs: ~80-85% accuracy (realistic)
- Difference: 10-15 percentage points (expected and documented)

---

## Market Regime Analysis

### Regime Characteristics

**2023-2024 (Training Period):**
- **Direction:** Bull market
- **Volatility:** Moderate to High
- **Trend Strength:** Strong
- **Difficulty:** Easy to Moderate
- **Expected Accuracy:** 85-95% (with costs: 75-85%)

**2025-11-15 (Current Period):**
- **Direction:** Sideways consolidation
- **Volatility:** Moderate
- **Trend Strength:** Weak
- **Difficulty:** Moderate to Difficult
- **Expected Accuracy:** 75-85% (with costs: 70-80%)

### Regime Impact on Accuracy

**Historical (2023-2024):** Higher accuracy due to strong trends  
**Current (2025-11-15):** Lower accuracy due to sideways market

**Adjustment:** We report regime-adjusted expectations

---

## Usage Guide

### Run Out-of-Sample Backtest

```bash
python argo/scripts/run_out_of_sample_backtest.py AAPL
```

### Use in Code

```python
from argo.backtest import StrategyBacktester, CalibratedBacktester, MarketRegimeAnalyzer

# Initialize with costs
backtester = StrategyBacktester(
    slippage_pct=0.0005,
    spread_pct=0.0002,
    commission_pct=0.001,
    use_cost_modeling=True
)

# Split data
train_df, val_df, test_df = backtester.split_data(df)

# Run on test set only
metrics = await backtester.run_backtest(
    symbol="AAPL",
    start_date=test_df.index[0],
    end_date=test_df.index[-1]
)

# Analyze regimes
analyzer = MarketRegimeAnalyzer()
characteristics = analyzer.analyze_period(df, "2025-11-15")
print(analyzer.generate_regime_report())
```

---

## Best Practices

### DO ✅

- ✅ Use three-set data split (train/val/test)
- ✅ Report only test set results
- ✅ Include realistic costs in all backtests
- ✅ Analyze market regimes
- ✅ Test calibration effectiveness
- ✅ Document methodology completely

### DON'T ❌

- ❌ Test on same data used for training
- ❌ Optimize on test data
- ❌ Ignore costs in backtests
- ❌ Report training set accuracy
- ❌ Ignore market regime changes
- ❌ Skip out-of-sample validation

---

## Related Documentation

- **Methodology:** See `docs/BACKTESTING_METHODOLOGY.md`
- **System Architecture:** See `01_COMPLETE_SYSTEM_ARCHITECTURE.md`
- **Signal Generation:** See `02_SIGNAL_GENERATION_COMPLETE_GUIDE.md`

---

**This guide reflects the complete v5.0 backtesting framework with all enhancements.**

