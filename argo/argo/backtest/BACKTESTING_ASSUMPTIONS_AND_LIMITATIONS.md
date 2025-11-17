# Backtesting System - Assumptions and Limitations

**Last Updated:** 2025-01-27
**Version:** 1.0

---

## Overview

This document outlines the key assumptions, limitations, and design decisions in the Argo-Alpine backtesting system. Understanding these is critical for interpreting backtest results and making informed trading decisions.

---

## 1. Look-Ahead Bias Prevention

### Assumptions

1. **Pre-calculated Indicators are Safe**
   - Pandas `.rolling()` is backward-looking only
   - Indicator at index `i` uses data from `[i-window+1:i+1]`
   - Pre-calculation does not introduce look-ahead bias
   - **Validation:** `_validate_no_lookahead()` method verifies this

2. **Historical Data Slicing**
   - `df.iloc[:index+1]` ensures only historical data is used
   - Signal generation uses data up to current index only
   - No future data is accessible during signal generation

### Limitations

- **Indicator Calculation:** Pre-calculated indicators assume backward-looking behavior
- **Data Availability:** Assumes all required historical data is available at each point
- **Real-Time vs Historical:** Historical backtests may not perfectly match real-time execution

### Validation

- `BiasPrevention.validate_no_lookahead()` checks timestamp ordering
- `BiasPrevention.validate_data_slice()` verifies data slice boundaries
- `StrategyBacktester._validate_no_lookahead()` validates pre-calculated indicators

---

## 2. Transaction Cost Modeling

### Assumptions

1. **Enhanced Transaction Cost Model (Default)**
   - Square-root slippage model (industry standard)
   - Symbol-specific liquidity tiers
   - Realistic spread and commission modeling
   - **Default:** Enabled (`use_enhanced_cost_model=True`)

2. **Simple Cost Model (Fallback)**
   - Fixed percentage slippage
   - Fixed percentage spread
   - Fixed percentage commission
   - Used when enhanced model parameters unavailable

### Limitations

- **Market Impact:** Models may not capture extreme market conditions
- **Liquidity Assumptions:** Assumes average liquidity throughout backtest period
- **Slippage Model:** Square-root model is an approximation
- **Commission:** Fixed rates may not reflect actual broker fees

### Cost Components

1. **Slippage:** Market impact of trade execution
2. **Spread:** Bid-ask spread cost
3. **Commission:** Broker fees

---

## 3. Exit Conditions

### Assumptions

1. **Stop Loss Priority**
   - Stop losses can trigger **before** minimum holding period
   - Risk management takes precedence over holding period rules
   - **Implementation:** `_check_exit_conditions()` allows stop loss exits regardless of `min_holding_bars`

2. **Take Profit Respects Holding Period**
   - Take profit exits require minimum holding period
   - Prevents excessive trading and transaction costs
   - **Implementation:** `_check_exit_conditions()` blocks take profit if `bars_held < min_holding_bars`

3. **Minimum Holding Period**
   - Default: 5 bars
   - Configurable via `min_holding_bars` parameter
   - Applies to normal exits, not stop losses

### Limitations

- **Stop Loss Execution:** Assumes stop loss can be executed at exact price
- **Slippage on Stops:** Stop loss execution may have additional slippage (not fully modeled)
- **Gap Risk:** Overnight gaps may cause stop loss to execute at worse price

---

## 4. Position Sizing

### Assumptions

1. **Adaptive Position Sizing**
   - Position size based on signal confidence
   - Volatility-adjusted sizing
   - Symbol-specific adjustments
   - **Implementation:** `PerformanceEnhancer.calculate_position_size()`

2. **Capital Management**
   - Maximum position size limits
   - Portfolio-level risk management
   - Drawdown-based position reduction

### Limitations

- **Confidence Calibration:** Assumes confidence scores are well-calibrated
- **Volatility Estimation:** Uses historical volatility, may not predict future
- **Liquidity Constraints:** Does not account for position size vs. market liquidity

---

## 5. Data Assumptions

### Assumptions

1. **Data Quality**
   - Historical data is accurate and complete
   - No missing bars or data gaps
   - Prices are adjusted for splits/dividends

2. **Data Availability**
   - All required indicators can be calculated
   - Sufficient historical data for warmup period
   - Data is available at each backtest point

### Limitations

- **Data Gaps:** Missing data may cause incorrect signals
- **Survivorship Bias:** Only includes symbols that exist throughout backtest period
- **Corporate Actions:** Assumes data is properly adjusted
- **Data Snooping:** Multiple backtests on same data may overfit

---

## 6. Signal Generation

### Assumptions

1. **Historical Signal Generation**
   - `HistoricalSignalGenerator` prevents look-ahead bias
   - Uses only data available at each historical point
   - Matches real-time signal generation logic

2. **Consensus Engine**
   - `WeightedConsensusEngine` behavior is consistent
   - Source weights are stable over time
   - ML models are not retrained during backtest

### Limitations

- **Model Drift:** ML models may perform differently over time
- **Source Availability:** Assumes all data sources available historically
- **Regime Changes:** May not account for changing market regimes

---

## 7. Performance Metrics

### Assumptions

1. **Metrics Calculation**
   - Equity curve is accurate
   - All trades are properly recorded
   - Returns are calculated correctly

2. **Risk Metrics**
   - Sharpe ratio uses 252 trading days/year
   - Sortino ratio uses downside deviation
   - Drawdown is calculated from peak equity

### Limitations

- **Annualization:** Assumes 252 trading days/year
- **Risk-Free Rate:** Uses 0% risk-free rate (simplification)
- **Distribution Assumptions:** Some metrics assume normal distribution

---

## 8. Execution Assumptions

### Assumptions

1. **Perfect Execution**
   - Orders execute at specified prices
   - No partial fills
   - No order rejection

2. **Market Hours**
   - Assumes trades execute during market hours
   - No after-hours or pre-market trading

### Limitations

- **Slippage:** Actual execution may have additional slippage
- **Order Rejection:** Orders may be rejected in real trading
- **Partial Fills:** Large orders may not fill completely
- **Market Hours:** Real trading may occur outside market hours

---

## 9. Known Limitations

### Critical Limitations

1. **Look-Ahead Bias Risk**
   - Pre-calculated indicators are validated but complex logic may still have bias
   - **Mitigation:** `_validate_no_lookahead()` method checks for bias

2. **Transaction Cost Accuracy**
   - Enhanced model is more accurate but still an approximation
   - Extreme market conditions may have higher costs

3. **Data Quality**
   - Assumes perfect data quality
   - Missing or incorrect data may cause errors

### Moderate Limitations

1. **Model Stability**
   - ML models may not be stable over long periods
   - Source weights may change over time

2. **Regime Changes**
   - Backtests may not account for changing market regimes
   - Past performance may not predict future

3. **Execution Reality**
   - Perfect execution assumed
   - Real trading may have additional costs/delays

---

## 10. Best Practices

### When Interpreting Results

1. **Consider Limitations**
   - Results are estimates, not guarantees
   - Account for transaction costs and slippage
   - Consider regime changes

2. **Validate Assumptions**
   - Verify data quality
   - Check for look-ahead bias
   - Validate cost model assumptions

3. **Use Multiple Metrics**
   - Don't rely on single metric (e.g., Sharpe ratio)
   - Consider drawdown, win rate, profit factor
   - Look at trade distribution

### When Running Backtests

1. **Use Enhanced Cost Model**
   - Default: `use_enhanced_cost_model=True`
   - More realistic cost estimates

2. **Validate Data**
   - Check for missing data
   - Verify data quality
   - Ensure sufficient historical data

3. **Test Multiple Scenarios**
   - Vary parameters
   - Test different time periods
   - Consider out-of-sample testing

---

## 11. Future Improvements

### Planned Enhancements

1. **Better Cost Modeling**
   - Dynamic liquidity modeling
   - Regime-specific cost adjustments
   - Order size impact modeling

2. **Enhanced Validation**
   - Automated look-ahead bias detection
   - Data quality checks
   - Model stability testing

3. **More Realistic Execution**
   - Partial fill modeling
   - Order rejection handling
   - Market hours enforcement

---

## 12. References

- **Backtesting Review:** `argo/reports/BACKTESTING_REVIEW_ANALYSIS.md`
- **Implementation:** `argo/argo/backtest/strategy_backtester.py`
- **Bias Prevention:** `argo/argo/backtest/bias_prevention.py`
- **Cost Model:** `argo/argo/backtest/enhanced_transaction_cost.py`
- **Tests:** `argo/tests/backtest/test_backtest_validation.py`

---

## 13. Change Log

- **2025-01-27:** Initial documentation created
- **2025-01-27:** Added look-ahead bias validation section
- **2025-01-27:** Added exit conditions documentation
- **2025-01-27:** Added transaction cost assumptions

---

**Note:** This document should be updated as the backtesting system evolves. All assumptions and limitations should be reviewed regularly.
