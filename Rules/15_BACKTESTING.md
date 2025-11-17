# Backtesting Rules

**Last Updated:** November 17, 2025
**Version:** 3.0
**Applies To:** Argo Trading Engine

---

## Overview

Backtesting rules and best practices for testing trading strategies, optimizing parameters, and validating signal quality.

---

## Backtesting Framework

### Components

**Location:** `argo/argo/backtest/`

**Components:**
- `base_backtester.py` - Base class for all backtesters
- `strategy_backtester.py` - Tests signal generation quality
- `profit_backtester.py` - Tests trading profitability
- `walk_forward.py` - Walk-forward optimization
- `optimizer.py` - Parameter optimization
- `data_manager.py` - Historical data management
- `results_storage.py` - Results storage and retrieval

---

## Backtesting Types

### Strategy Backtester

**Purpose:** Test signal generation quality

**Focus:**
- Win rate
- Confidence accuracy
- Signal quality metrics

**Use For:** Alpine customer signal quality

**Component:** `strategy_backtester.py`

**Key Metrics:**
- Win rate (percentage of correct signals)
- Confidence calibration (how well confidence predicts success)
- Signal distribution
- False positive/negative rates

### Profit Backtester

**Purpose:** Test trading profitability

**Focus:**
- Total returns
- Sharpe ratio
- Maximum drawdown
- Profit factor

**Use For:** Argo trading optimization

**Component:** `profit_backtester.py`

**Key Metrics:**
- Total return (%)
- Sharpe ratio
- Maximum drawdown (%)
- Win rate
- Profit factor
- Average win/loss ratio

**Includes:**
- Slippage simulation
- Commission costs
- Execution delays
- Real trading constraints

---

## Out-of-Sample Testing (v6.0 Enhancement)

### Purpose

**Rule:** ALWAYS use three-set data split (train/val/test) for strategy validation

**Why:** Prevents data leakage and overfitting, ensures defensible results

### Three-Set Split

**Rule:** Split data into three sets:
- **Training (60%):** Used for optimization only
- **Validation (20%):** Used for validation only
- **Test (20%):** Used for measurement only (OUT-OF-SAMPLE)

**Rule:** ONLY report test set results to customers

**Implementation:**
```python
train_df, val_df, test_df = backtester.split_data(df, train_pct=0.6, val_pct=0.2, test_pct=0.2)
```

### Data Leakage Prevention

**Rules:**
- ✅ Training data: Used for optimization only
- ✅ Validation data: Used for validation only
- ✅ Test data: Used for measurement only (never for optimization)
- ❌ Never optimize on test data
- ❌ Never use future data to predict past

## Walk-Forward Testing

### Purpose

**Rule:** Use walk-forward testing for additional validation

**Why:** Tests strategy robustness across different time periods

### Process

1. **Split Data:** Training period + Test period
2. **Train:** Optimize parameters on training data
3. **Test:** Validate on test data (out-of-sample)
4. **Roll Forward:** Move window forward
5. **Repeat:** Continue for entire dataset

### Configuration

**From `config.json` → `backtest.walk_forward`:**
- `train_days`: 252 (1 year)
- `test_days`: 63 (1 quarter)
- `step_days`: 21 (1 month)

**Rule:** Test period should be at least 20% of training period

**v6.0 Update:** Walk-forward testing should use three-set split within each window

---

## Parameter Optimization

### Grid Search

**Component:** `optimizer.py`

**Process:**
1. Define parameter ranges
2. Generate all combinations
3. Run backtest for each combination
4. Select best parameters based on objective

### Objectives

**Available Objectives:**
- Sharpe ratio (default)
- Win rate
- Total return
- Sortino ratio
- Profit factor

**Rule:** Use Sharpe ratio for risk-adjusted returns

### Constraints

**Rule:** Limit grid search iterations
- **Default:** 1000 iterations
- **Configurable:** `backtest.optimization.max_iterations`

**Rule:** Use walk-forward validation with optimization

---

## Historical Data Management

### Data Manager

**Component:** `data_manager.py`

### Data Sources

**Primary:** yfinance (default)
- **Stocks:** Standard ticker symbols
- **Crypto:** Symbol-USD format (e.g., BTC-USD)

**Configuration:** `backtest.data_source`

### Data Requirements

**Minimum Data:**
- **Training:** At least 1 year of data
- **Testing:** At least 3 months of data
- **Total:** At least 1.5 years for walk-forward

**Data Quality:**
- **Rule:** Validate data before backtesting
- **Checks:**
  - No missing values
  - No duplicate timestamps
  - Valid price ranges (High >= Low)
  - Consistent time intervals

### Caching

**Rule:** Cache historical data
- **Enabled:** `backtest.cache_enabled: true`
- **Location:** `backtest.data_path`
- **Benefit:** Faster subsequent backtests

---

## Execution Simulation

### Slippage

**Rule:** Include slippage in ALL backtests (strategy and profit)

**Configuration:** `backtest.execution.slippage_pct: 0.0005` (0.05%)

**Impact:** Reduces returns, more realistic

**v6.0 Update:** Strategy backtester now includes slippage by default

### Spread

**Rule:** Include bid-ask spread in ALL backtests

**Configuration:** `backtest.execution.spread_pct: 0.0002` (0.02%)

**Impact:** Reduces returns, accounts for bid-ask spread

**v6.0 Update:** Strategy backtester now includes spread by default

### Commission

**Rule:** Include commission costs in ALL backtests

**Configuration:** `backtest.execution.commission_pct: 0.001` (0.1%)

**Impact:** Reduces returns, more realistic

**v6.0 Update:** Strategy backtester now includes commission by default

### Total Round-Trip Cost

**Total Cost per Trade:** ~0.17% (slippage + spread + commission)

**Impact on Accuracy:** 10-15 percentage points reduction (expected and documented)

### Execution Delays

**Rule:** Simulate execution delays
- **Signal to Order:** 1-2 seconds
- **Order to Fill:** Market dependent

---

## Best Practices

### Strategy Testing

**DO:**
- ✅ Test on multiple time periods
- ✅ Use walk-forward validation
- ✅ Test on different market regimes
- ✅ Validate signal quality metrics
- ✅ Check confidence calibration

**DON'T:**
- ❌ Test on same data used for training
- ❌ Optimize on test data
- ❌ Ignore overfitting
- ❌ Use insufficient data
- ❌ Skip validation

### Profit Testing

**DO:**
- ✅ Include slippage and commissions
- ✅ Test with realistic constraints
- ✅ Validate risk management
- ✅ Check drawdown limits
- ✅ Test position sizing

**DON'T:**
- ❌ Ignore execution costs
- ❌ Assume perfect execution
- ❌ Skip risk management
- ❌ Ignore drawdown
- ❌ Over-optimize parameters

### Parameter Optimization

**DO:**
- ✅ Use walk-forward with optimization
- ✅ Limit parameter ranges
- ✅ Use multiple objectives
- ✅ Validate on out-of-sample data
- ✅ Check parameter stability

**DON'T:**
- ❌ Optimize on test data
- ❌ Use too many parameters
- ❌ Ignore overfitting
- ❌ Skip validation
- ❌ Use unstable parameters

---

## Running Backtests

### Local Backtests

**Script:** `argo/scripts/run_local_backtests.py`

**Usage:**
```bash
cd argo
python scripts/run_local_backtests.py
```

**Options:**
- Strategy backtest only
- Profit backtest only
- Both backtests
- Walk-forward testing
- Parameter optimization

### Manual Backtesting

**Example:**
```python
from argo.backtest.strategy_backtester import StrategyBacktester
from argo.backtest.data_manager import DataManager

# Initialize
data_manager = DataManager()
backtester = StrategyBacktester(data_manager)

# Run backtest
results = await backtester.run_backtest(
    symbol="AAPL",
    start_date="2023-01-01",
    end_date="2024-01-01"
)

# Analyze results
print(f"Win Rate: {results.win_rate:.2%}")
print(f"Sharpe Ratio: {results.sharpe_ratio:.2f}")
```

---

## Results Analysis

### Key Metrics

**Strategy Quality:**
- Win rate (target: >55%)
- Confidence calibration
- Signal distribution

**Trading Profitability:**
- Total return (target: >10% annually)
- Sharpe ratio (target: >1.0)
- Maximum drawdown (target: <20%)
- Profit factor (target: >1.5)

### Interpretation

**Win Rate vs Profitability:**
- High win rate ≠ High profitability
- Low win rate can be profitable with good risk/reward
- Focus on both metrics

**Sharpe Ratio:**
- >1.0: Good risk-adjusted returns
- >2.0: Excellent risk-adjusted returns
- <0.5: Poor risk-adjusted returns

**Drawdown:**
- <10%: Low risk
- 10-20%: Moderate risk
- >20%: High risk

---

## Related Rules

- [13_TRADING_OPERATIONS.md](13_TRADING_OPERATIONS.md) - Trading operations
- [06_CONFIGURATION.md](06_CONFIGURATION.md) - Configuration management
- [03_TESTING.md](03_TESTING.md) - Testing requirements
