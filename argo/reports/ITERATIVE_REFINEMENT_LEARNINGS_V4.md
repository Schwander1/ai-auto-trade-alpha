# Iterative Refinement Learnings - v4
**Date:** January 15, 2025  
**Iteration:** v4 (Aggressive Profit Factor Optimization)

---

## Executive Summary

This iteration focused on **aggressive profit factor optimization** with special attention to SPY's critical issue. Implemented asymmetric stop/profit approach for SPY and pushed more symbols above 1.0 profit factor threshold.

### Key Changes (v4)

1. **Base Profit Multiplier**: 3.3 → 3.4 (+0.1)
2. **SPY Aggressive Asymmetric Approach**:
   - stop_multiplier: 1.7 → 1.5 (much tighter)
   - profit_multiplier: 3.5 → 4.0 (much wider)
   - Max stop: 6% → 5% (very tight)
   - Max profit: 28% → 30% (very wide)
3. **Near 1.0 Symbols**: Increased profit_multiplier for NVDA, GOOGL, META
4. **AMZN**: Further tightening (1.7 → 1.65) and higher profit (3.6 → 3.8)
5. **Profit Caps**: Increased to 30% for SPY, AMZN, NVDA, GOOGL, META

---

## Results Comparison

| Metric | Iterative v3 | Iterative v4 | Change |
|--------|--------------|--------------|--------|
| **Avg Return** | 42.24% | **43.59%** | **+1.35%** ✅ |
| **Avg Win Rate** | 43.07% | 43.04% | -0.03% |
| **Avg Sharpe** | 0.86 | 0.86 | 0.00 |
| **Profit Factor** | 0.94 | **0.95** | **+0.01** ✅ |
| **Total Trades** | 6,314 | 6,291 | -23 |

---

## Per-Symbol Profit Factor Changes

| Symbol | v3 | v4 | Change | Status |
|--------|----|----|--------|--------|
| **AAPL** | 1.00 | 1.00 | 0.00 | ✅ Maintained |
| **NVDA** | 0.99 | 0.99 | 0.00 | ⚠️ Still 0.99 |
| **TSLA** | 0.94 | 0.92 | -0.02 | ⚠️ Slight decrease |
| **MSFT** | 0.85 | 0.84 | -0.01 | ⚠️ Slight decrease |
| **GOOGL** | 0.98 | 0.98 | 0.00 | ⚠️ No change |
| **META** | 0.96 | 0.95 | -0.01 | ⚠️ Slight decrease |
| **AMD** | 0.84 | 0.84 | 0.00 | ⚠️ No change |
| **AMZN** | 0.81 | **0.83** | **+0.02** | ✅ Improved |
| **SPY** | 0.59 | **0.66** | **+0.07** | ✅ **Significant improvement!** |
| **QQQ** | 0.85 | **0.86** | **+0.01** | ✅ Improved |
| **BTC-USD** | 1.15 | 1.15 | 0.00 | ✅ Maintained |
| **ETH-USD** | 1.32 | 1.32 | 0.00 | ✅ Maintained |

---

## Key Learnings

### 1. SPY Asymmetric Approach Works! ✅

**Results:**
- Profit factor: 0.59 → 0.66 (+0.07) - **11.9% improvement**
- Return: 18.16% → 27.88% (+9.72%) - **53.5% improvement!**
- Win rate: 40.44% → 38.71% (-1.73%) - slight decrease
- Max drawdown: -25.00% → -19.75% (+5.25%) - **better risk control**

**Insights:**
- Asymmetric approach (tight stops, wide profits) works for low-volatility ETFs
- SPY still critical (0.66) but trending in right direction
- Return improvement is significant - strategy is working better
- May need even more aggressive asymmetry or different approach

**Recommendation:**
- Continue asymmetric approach for SPY
- Consider even tighter stops (1.4x ATR) or wider profits (4.5x ATR)
- Or test different strategy entirely (trend-following, longer timeframes)

### 2. Profit Factor Improvements ✅

**Successes:**
- **SPY**: Significant improvement (+0.07) - biggest win
- **AMZN**: Continued improvement (+0.02)
- **QQQ**: Small improvement (+0.01)
- **Overall**: Average profit factor improved from 0.94 to 0.95

**Challenges:**
- **NVDA**: Still at 0.99 (didn't cross 1.0 threshold)
- **GOOGL**: No change (0.98)
- **META**: Slight decrease (0.96 → 0.95)

**Insight:**
- Symbols near 1.0 threshold are harder to push over
- May need different approach (entry quality, timing, etc.)
- Not just about stop/profit ratios

### 3. Return Improvements ✅

**Major Wins:**
- **SPY**: +9.72% return improvement (18.16% → 27.88%)
- **AMZN**: +4.60% return improvement (68.47% → 73.07%)
- **Overall**: +1.35% average return improvement

**Insight:**
- Asymmetric approach improves returns significantly
- Higher profit targets allow winners to run longer
- Tighter stops reduce losses, improving net returns

### 4. Trade-offs

**Positive:**
- Average return increased (+1.35%)
- Profit factor improved (+0.01)
- SPY significantly improved
- Better risk control (lower drawdowns)

**Neutral:**
- Win rate essentially unchanged (-0.03%)
- Sharpe ratio unchanged (0.86)
- Total trades slightly decreased (-23)

**Negative:**
- Some symbols slightly decreased (TSLA, MSFT, META)
- NVDA still at 0.99 (didn't cross threshold)
- SPY still critical (0.66) despite improvement

---

## SPY Deep Dive Analysis

### The Problem
- Win/loss ratio: 0.87 (losing more per loss than winning per win)
- Low volatility ETF - current strategy may not be optimal
- Profit factor: 0.66 (still critical but improving)

### The Solution (v4)
- Asymmetric approach: 1.5x ATR stops, 4.0x ATR profits
- Max 5% stop, max 30% profit
- Result: +0.07 profit factor, +9.72% return

### Next Steps for SPY
1. **Even more aggressive**: Test 1.4x stops, 4.5x profits
2. **Different strategy**: Consider trend-following or longer timeframes
3. **Entry quality**: Require higher confidence or different signals
4. **Consider exclusion**: If consistently underperforming, may exclude

---

## Recommendations for Next Iteration

### 1. Continue SPY Optimization 🔴

**Options:**
1. **More aggressive asymmetry**: 1.4x stops, 4.5x profits
2. **Different entry criteria**: Higher confidence threshold for SPY
3. **Test exclusion**: See if overall performance improves without SPY
4. **Different timeframe**: Test with longer holding periods

### 2. Push Symbols Over 1.0 Threshold

**Focus:**
- **NVDA** (0.99): So close! May need entry quality improvement
- **GOOGL** (0.98): Similar - entry quality or timing
- **META** (0.95): Needs improvement

**Approach:**
- Not just stop/profit ratios
- May need better entry signals
- Consider confidence threshold adjustments
- Test different indicators or filters

### 3. Maintain Improvements

**Protect:**
- SPY improvements (don't regress)
- AMZN improvements
- Overall profit factor gains

### 4. Address Decreases

**Monitor:**
- TSLA: 0.94 → 0.92 (-0.02)
- MSFT: 0.85 → 0.84 (-0.01)
- META: 0.96 → 0.95 (-0.01)

**Action:**
- Review what changed
- May need symbol-specific adjustments
- Balance with overall improvements

---

## Iterative Process Insights

### What Worked Well ✅

1. **Asymmetric Approach**: SPY improved significantly with tight stops + wide profits
2. **Aggressive Optimization**: Pushing profit_multiplier higher helped
3. **Symbol-Specific Tuning**: Different approaches for different symbols
4. **Data-Driven**: Analysis-driven refinements are effective

### What Needs Improvement ⚠️

1. **Threshold Crossing**: Hard to push symbols from 0.99 to 1.0+
2. **SPY Strategy**: Still critical despite improvement
3. **Trade-offs**: Some symbols decreased slightly
4. **Entry Quality**: May need better signals, not just stop/profit ratios

### Process Improvements 🔧

1. **Asymmetric Testing**: Test more asymmetric approaches
2. **Entry Quality**: Focus on signal quality, not just exits
3. **Symbol Exclusion**: Consider excluding consistently underperforming symbols
4. **Multi-Objective**: Balance profit factor, returns, Sharpe ratio

---

## Next Steps

1. **SPY**: Test even more aggressive asymmetry or different approach
2. **Threshold Symbols**: Focus on entry quality for NVDA, GOOGL, META
3. **Maintain Gains**: Protect SPY and AMZN improvements
4. **Balance**: Address slight decreases in TSLA, MSFT, META

---

**Iteration v4 Complete**  
**Overall Assessment:** ✅ Positive progress - SPY significantly improved, overall returns and profit factor increased, but threshold symbols need different approach

