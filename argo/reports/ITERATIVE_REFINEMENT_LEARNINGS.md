# Iterative Refinement Learnings - v3
**Date:** January 15, 2025  
**Iteration:** v3 (Profit Factor Optimization)

---

## Executive Summary

This iteration focused on **improving profit factor** by analyzing win/loss ratios and making targeted adjustments to stop loss and profit target multipliers for underperforming symbols.

### Key Changes (v3)

1. **Base Profit Multiplier**: 3.2 → 3.3 (+0.1)
2. **Symbol-Specific Refinements**:
   - **SPY**: stop_multiplier 2.0 → 1.7, profit_multiplier 3.2 → 3.5
   - **AMZN**: stop_multiplier 1.9 → 1.7, profit_multiplier 3.2 → 3.6
   - **MSFT/AMD/QQQ**: stop_multiplier 2.0 → 1.8, profit_multiplier 3.2 → 3.5
   - **AAPL/NVDA**: profit_multiplier 3.4 → 3.5
   - **META/TSLA**: profit_multiplier 3.3 → 3.4
3. **Profit Caps**: Increased from 25% to 27% (28% for SPY/AMZN)

---

## Results Comparison

| Metric | Final Refined | Iterative v3 | Change |
|--------|---------------|--------------|--------|
| **Avg Return** | 41.54% | **42.24%** | **+0.70%** ✅ |
| **Avg Win Rate** | 43.17% | 43.07% | -0.10% |
| **Avg Sharpe** | 0.86 | 0.86 | 0.00 |
| **Profit Factor** | 0.93 | **0.94** | **+0.01** ✅ |
| **Total Trades** | 6,313 | 6,314 | +1 |

---

## Per-Symbol Profit Factor Changes

| Symbol | Final Refined | Iterative v3 | Change | Status |
|--------|---------------|--------------|--------|--------|
| **AAPL** | 0.99 | **1.00** | **+0.01** | ✅ **Crossed 1.0!** |
| **NVDA** | 0.98 | 0.99 | +0.01 | ⚠️ Close |
| **TSLA** | 0.93 | 0.94 | +0.01 | ⚠️ Improved |
| **MSFT** | 0.82 | **0.85** | **+0.03** | ✅ Improved |
| **GOOGL** | 1.00 | 0.98 | -0.02 | ⚠️ Slight decrease |
| **META** | 0.95 | 0.96 | +0.01 | ⚠️ Improved |
| **AMD** | 0.85 | 0.84 | -0.01 | ⚠️ Slight decrease |
| **AMZN** | 0.75 | **0.81** | **+0.06** | ✅ **Significant improvement** |
| **SPY** | 0.59 | 0.59 | 0.00 | ❌ **No change - still critical** |
| **QQQ** | 0.82 | **0.85** | **+0.03** | ✅ Improved |
| **BTC-USD** | 1.15 | 1.15 | 0.00 | ✅ Maintained |
| **ETH-USD** | 1.32 | 1.32 | 0.00 | ✅ Maintained |

---

## Key Learnings

### 1. Profit Factor Improvements ✅

**Successes:**
- **AAPL**: Crossed the 1.0 threshold (0.99 → 1.00)
- **AMZN**: Significant improvement (+0.06) - still needs work but trending better
- **MSFT, QQQ**: Improved by +0.03 each
- **Overall**: Average profit factor improved from 0.93 to 0.94

**Insights:**
- Increasing profit_multiplier helps when win/loss ratio is already >1.0
- Tighter stops help reduce average loss size
- Combination of both (tighter stops + higher profit targets) works best

### 2. SPY Remains Critical ❌

**Problem:**
- Profit factor unchanged at 0.59 (still critical)
- Win/loss ratio is 0.87 (losing more per loss than winning per win)
- Tighter stops (2.0 → 1.7) didn't help

**Analysis:**
- SPY is an ETF with low volatility
- Current approach may not be suitable for low-volatility assets
- May need different strategy entirely (e.g., longer timeframes, different indicators)

**Recommendation:**
- Consider excluding SPY from strategy or using different parameters
- Test with even tighter stops (1.5x ATR) or different approach
- May need trend-following rather than mean-reversion for ETFs

### 3. Symbol-Specific Optimization Works ✅

**Evidence:**
- Different symbols respond differently to parameter changes
- AMZN improved significantly with tighter stops + higher profit targets
- AAPL crossed 1.0 threshold with small profit_multiplier increase
- Crypto (BTC, ETH) maintained good profit factors with minimal changes

**Insight:**
- One-size-fits-all doesn't work
- Symbol-specific tuning is essential
- Need to analyze each symbol's characteristics (volatility, trend, etc.)

### 4. Trade-offs

**Positive:**
- Average return increased (+0.70%)
- Profit factor improved (+0.01)
- Several symbols improved significantly

**Neutral:**
- Win rate essentially unchanged (-0.10%)
- Sharpe ratio unchanged (0.86)
- Total trades unchanged

**Negative:**
- SPY still critical (no improvement)
- Some symbols slightly decreased (GOOGL, AMD)

---

## Recommendations for Next Iteration

### 1. SPY Strategy Overhaul 🔴

**Options:**
1. **Exclude SPY** from strategy (if it consistently underperforms)
2. **Different approach**: Use longer timeframes, different indicators
3. **Even tighter stops**: Test 1.5x ATR (may reduce trades too much)
4. **Different entry criteria**: Require higher confidence or different signals

### 2. Continue Profit Factor Optimization

**Focus on:**
- Symbols still below 1.0: NVDA (0.99), TSLA (0.94), META (0.96), MSFT (0.85), AMD (0.84), AMZN (0.81), QQQ (0.85), SPY (0.59)
- Test even higher profit_multiplier for symbols with good win/loss ratios
- Consider asymmetric stops (tighter stops, wider profit targets)

### 3. Win Rate Optimization

**Current:** 43.07% (down from baseline 47.68%)

**Options:**
- Raise confidence threshold (currently 58%)
- Add additional filters (volume, trend, etc.)
- Improve entry timing

**Trade-off:** Higher win rate may reduce returns (fewer trades, smaller profits)

### 4. Sharpe Ratio Improvement

**Current:** 0.86 (down from baseline 1.05)

**Options:**
- Tighter stops overall (reduce volatility)
- Better position sizing
- More selective entries

**Trade-off:** May reduce absolute returns

---

## Iterative Process Insights

### What Worked Well ✅

1. **Data-Driven Analysis**: Profit factor analysis identified specific issues
2. **Targeted Refinements**: Symbol-specific adjustments based on analysis
3. **Comprehensive Tracking**: All iterations tracked for comparison
4. **Incremental Changes**: Small, focused changes rather than large swings

### What Needs Improvement ⚠️

1. **SPY Strategy**: Current approach not working - needs different solution
2. **Profit Factor**: Still below 1.0 overall (0.94) - need to push higher
3. **Win Rate**: Decreased from baseline - may need to address
4. **Sharpe Ratio**: Decreased from baseline - risk-adjusted returns need work

### Process Improvements 🔧

1. **Automated Analysis**: Scripts for profit factor analysis are helpful
2. **Iterative Testing**: Quick iteration cycles allow rapid learning
3. **Symbol-Specific Tuning**: Essential for diverse asset types
4. **Comprehensive Metrics**: Tracking all metrics (not just returns) is important

---

## Next Steps

1. **Address SPY**: Test different approach or consider exclusion
2. **Continue Profit Factor**: Push more symbols above 1.0
3. **Balance Metrics**: Improve Sharpe ratio while maintaining returns
4. **Win Rate**: Consider if 43% is acceptable or needs improvement

---

**Iteration v3 Complete**  
**Overall Assessment:** ✅ Positive progress - profit factor improved, returns increased, but SPY remains critical issue

