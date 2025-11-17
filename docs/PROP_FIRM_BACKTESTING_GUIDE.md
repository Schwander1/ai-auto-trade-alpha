# Prop Firm Backtesting Guide

**Date:** January 2025  
**Status:** Complete Implementation Guide

---

## Executive Summary

This guide provides comprehensive guidance on backtesting strategies specifically for prop firm trading accounts. It leverages the existing backtesting infrastructure while adding prop firm-specific constraints and risk management.

---

## 1. Prop Firm Requirements

### Risk Limits

| Constraint | Prop Firm Limit | Conservative Limit | Description |
|------------|----------------|-------------------|-------------|
| **Max Drawdown** | 2.5% | 2.0% | Maximum peak-to-trough decline |
| **Daily Loss Limit** | 5.0% | 4.5% | Maximum loss per trading day |
| **Initial Capital** | $25,000-$100,000 | $25,000 | Starting account size |
| **Position Size** | Varies | 5-10% | Maximum position size per trade |
| **Max Positions** | Varies | 3-5 | Maximum concurrent positions |

### Key Differences from Standard Backtesting

1. **Tighter Drawdown Limits**: 2.0% vs typical 20% portfolio drawdown
2. **Daily Loss Tracking**: Must track and enforce daily loss limits
3. **Conservative Position Sizing**: Smaller positions to avoid breaching limits
4. **Higher Confidence Threshold**: Focus on 80%+ confidence signals
5. **Stricter Risk Management**: Automatic shutdown on breach

---

## 2. What We Can Reuse from Existing Backtesting

### ✅ Fully Reusable Components

1. **StrategyBacktester** (`argo/argo/backtest/strategy_backtester.py`)
   - Signal generation using WeightedConsensusEngine
   - Transaction cost modeling (slippage, spread, commission)
   - Enhanced cost model with square-root slippage
   - Portfolio-level risk management
   - Out-of-sample testing framework

2. **ProfitBacktester** (`argo/argo/backtest/profit_backtester.py`)
   - Full execution simulation
   - Position sizing
   - P&L calculation with costs
   - Performance metrics (Sharpe, Sortino, drawdown)

3. **Data Management** (`argo/argo/backtest/data_manager.py`)
   - Historical data fetching (20+ years)
   - Data validation and cleaning
   - Polars/DuckDB integration for performance

4. **Transaction Cost Models**
   - EnhancedTransactionCostModel (square-root slippage)
   - Symbol-specific cost adjustments
   - Volume-based market impact

5. **Risk Management**
   - PropFirmRiskMonitor (real-time monitoring)
   - Portfolio drawdown tracking
   - Position correlation management

### 🔧 Components to Adapt

1. **Risk Limits**: Override with prop firm constraints
2. **Position Sizing**: Reduce to 5-10% (vs 10-20%)
3. **Confidence Threshold**: Increase to 80%+ (vs 60-75%)
4. **Daily Loss Tracking**: Add daily reset logic
5. **Drawdown Calculation**: Use peak equity tracking

---

## 3. Prop Firm Backtester Implementation

### Architecture

```
PropFirmBacktester
├── Inherits from StrategyBacktester
├── Enforces prop firm constraints
├── Tracks daily P&L
├── Implements emergency shutdown
└── Generates prop firm-specific reports
```

### Key Features

1. **Conservative Risk Limits**
   - Max drawdown: 2.0% (vs 2.5% limit)
   - Daily loss limit: 4.5% (vs 5.0% limit)
   - Position size: 5-10% (vs 10-20%)

2. **Daily Loss Tracking**
   - Tracks P&L per trading day
   - Resets at start of each day
   - Enforces daily loss limit

3. **Peak Equity Tracking**
   - Tracks highest equity value
   - Calculates drawdown from peak
   - Triggers shutdown on breach

4. **Enhanced Reporting**
   - Prop firm compliance metrics
   - Daily P&L breakdown
   - Drawdown analysis
   - Risk limit proximity warnings

---

## 4. Backtesting Methodology for Prop Firms

### Data Splitting

**Standard Split (60/20/20):**
- Training: 2023-2024 (60%)
- Validation: 2025-01 to 2025-09 (20%)
- Test: 2025-10-01 onwards (20% - OUT-OF-SAMPLE)

**Prop Firm Focus:**
- Use test set for final validation
- Ensure all periods respect prop firm constraints
- Track constraint breaches across all periods

### Transaction Costs

**Standard Costs:**
- Slippage: 0.05%
- Spread: 0.02%
- Commission: 0.1%
- Total: ~0.17% per trade

**Prop Firm Considerations:**
- May have lower costs (prop firm benefits)
- Use enhanced cost model for accuracy
- Account for symbol-specific spreads

### Signal Quality

**Standard Threshold:**
- Minimum confidence: 60-75%

**Prop Firm Threshold:**
- Minimum confidence: 80%+
- Focus on quality over quantity
- Higher win rate required (90%+)

---

## 5. Go-Forward Strategy

### Phase 1: Backtesting (Week 1-2)

1. **Run Prop Firm Backtests**
   ```bash
   python argo/scripts/run_prop_firm_backtest.py
   ```

2. **Test Multiple Symbols**
   - SPY, QQQ (liquid ETFs)
   - AAPL, NVDA (high-volume stocks)
   - BTC-USD, ETH-USD (crypto)

3. **Validate Constraints**
   - Verify drawdown stays < 2.0%
   - Verify daily loss stays < 4.5%
   - Check position sizing compliance

4. **Optimize Parameters**
   - Confidence threshold (80-90%)
   - Position size (5-10%)
   - Stop loss/take profit ratios

### Phase 2: Paper Trading (Week 3-4)

1. **Paper Trade with Prop Firm Rules**
   - Use prop firm test account
   - Monitor real-time risk limits
   - Validate backtest results

2. **Track Performance**
   - Daily P&L
   - Drawdown tracking
   - Signal quality metrics

3. **Adjust Strategy**
   - Refine based on paper trading results
   - Optimize for prop firm constraints
   - Improve risk management

### Phase 3: Live Trading (Month 2+)

1. **Start with Small Account**
   - $25,000 prop firm account
   - Conservative position sizing
   - Focus on compliance

2. **Scale Gradually**
   - Increase position size as confidence grows
   - Add more symbols
   - Optimize for profitability

3. **Monitor Continuously**
   - Real-time risk monitoring
   - Daily compliance checks
   - Performance tracking

---

## 6. Key Metrics to Track

### Prop Firm Compliance Metrics

1. **Drawdown Metrics**
   - Current drawdown: < 2.0%
   - Peak drawdown: Historical maximum
   - Drawdown duration: Days in drawdown

2. **Daily P&L Metrics**
   - Daily P&L: < -4.5%
   - Daily win rate: % of profitable days
   - Average daily return: Mean daily P&L

3. **Position Metrics**
   - Average position size: % of capital
   - Max concurrent positions: Count
   - Position correlation: Portfolio risk

### Performance Metrics

1. **Returns**
   - Total return: % gain/loss
   - Annualized return: Yearly return
   - Monthly return: Target 5-10%

2. **Risk-Adjusted Returns**
   - Sharpe ratio: > 2.0 (excellent)
   - Sortino ratio: > 2.0 (excellent)
   - Calmar ratio: Return / Max drawdown

3. **Trade Statistics**
   - Win rate: > 90% (prop firm target)
   - Profit factor: > 2.0
   - Average win/loss ratio: > 2:1

---

## 7. Risk Management Best Practices

### Pre-Trade Checks

1. **Daily Loss Limit**
   - Check current daily P&L
   - Stop trading if < -4.5%
   - Reset at start of new day

2. **Drawdown Check**
   - Calculate current drawdown
   - Stop trading if > 2.0%
   - Track peak equity

3. **Position Limits**
   - Check max positions (3-5)
   - Verify position size (5-10%)
   - Check portfolio correlation

### During Trade

1. **Real-Time Monitoring**
   - Update equity continuously
   - Track drawdown in real-time
   - Monitor daily P&L

2. **Dynamic Adjustments**
   - Tighten stops if drawdown increases
   - Reduce position size if approaching limits
   - Close positions if breach imminent

### Post-Trade

1. **Daily Review**
   - Review all trades
   - Analyze drawdown periods
   - Identify improvement opportunities

2. **Weekly Analysis**
   - Performance metrics
   - Risk limit compliance
   - Strategy optimization

---

## 8. Implementation Files

### New Files to Create

1. **`argo/argo/backtest/prop_firm_backtester.py`**
   - Prop firm-specific backtester
   - Enforces prop firm constraints
   - Tracks daily P&L

2. **`argo/scripts/run_prop_firm_backtest.py`**
   - Script to run prop firm backtests
   - Multi-symbol testing
   - Results analysis

3. **`argo/scripts/analyze_prop_firm_results.py`**
   - Prop firm-specific analysis
   - Compliance reporting
   - Performance visualization

### Configuration

Add to `argo/config.json`:
```json
{
  "prop_firm": {
    "max_drawdown_pct": 2.0,
    "daily_loss_limit_pct": 4.5,
    "initial_capital": 25000.0,
    "max_position_size_pct": 10.0,
    "min_confidence": 80.0,
    "max_positions": 5
  }
}
```

---

## 9. Expected Performance

### Conservative Targets

- **Monthly Return**: 5-10%
- **Win Rate**: 90%+
- **Max Drawdown**: < 1.5% (safety margin)
- **Sharpe Ratio**: > 2.0
- **Daily Loss**: < 3.0% (safety margin)

### Realistic Expectations

- **First Month**: 3-5% return (learning phase)
- **Months 2-3**: 5-8% return (optimization)
- **Months 4+**: 8-12% return (mature strategy)

### Risk Considerations

- Prop firm constraints are strict
- Focus on consistency over high returns
- Preserve capital is priority #1
- Quality signals over quantity

---

## 10. Next Steps

1. **Implement PropFirmBacktester** (Priority 1)
   - Create prop firm-specific backtester
   - Enforce all constraints
   - Add daily P&L tracking

2. **Run Comprehensive Backtests** (Priority 2)
   - Test multiple symbols
   - Validate constraints
   - Optimize parameters

3. **Paper Trading Validation** (Priority 3)
   - Test with real-time data
   - Validate backtest results
   - Refine strategy

4. **Live Trading** (Priority 4)
   - Start with small account
   - Monitor closely
   - Scale gradually

---

## Conclusion

The existing backtesting infrastructure provides a solid foundation for prop firm backtesting. By adapting risk limits, position sizing, and confidence thresholds, we can create a prop firm-specific backtester that validates strategies before live trading.

**Key Success Factors:**
1. Strict adherence to prop firm constraints
2. Conservative position sizing
3. High-quality signals (80%+ confidence)
4. Continuous risk monitoring
5. Focus on consistency over high returns

