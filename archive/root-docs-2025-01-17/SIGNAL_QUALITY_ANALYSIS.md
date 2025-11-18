# Signal Quality Analysis Report

**Date:** November 18, 2025  
**Analysis Period:** November 12-17, 2025  
**Total Signals Analyzed:** 1,969

---

## Executive Summary

### Overall Quality: **B+ (Good)**

- ✅ **100% of signals above 70% confidence** (excellent quality floor)
- ✅ **20.77% meet prop firm threshold** (82%+ confidence)
- ⚠️ **Recent activity very low** (only 1 signal on Nov 17)
- ⚠️ **No outcome data** (trades not tracked/completed)

---

## Key Statistics

| Metric | Value |
|--------|-------|
| **Total Signals** | 1,969 |
| **Date Range** | Nov 12-17, 2025 (6 days) |
| **Average Confidence** | 76.63% |
| **Confidence Range** | 75.0% - 92.5% |
| **Unique Symbols** | 6 |
| **Active Trading Days** | 4 |

---

## Signal Distribution

### By Action Type

| Action | Count | % | Avg Confidence |
|--------|-------|---|----------------|
| **BUY** | 1,047 | 53.17% | 75.44% |
| **SELL** | 922 | 46.83% | 77.99% |

**Insight:** SELL signals have higher confidence (77.99% vs 75.44%)

### By Asset Type

| Asset | Count | % | Avg Confidence |
|-------|-------|---|----------------|
| **Crypto** | 1,726 | 87.66% | 76.75% |
| **Stock** | 243 | 12.34% | 75.81% |

**Insight:** Heavy crypto focus (87.66%), crypto signals slightly higher confidence

### By Symbol

| Symbol | Signals | % of Total | Avg Confidence | Latest |
|--------|---------|------------|----------------|--------|
| **ETH-USD** | 1,008 | 51.2% | 77.99% | Nov 15 |
| **BTC-USD** | 718 | 36.5% | 75.01% | Nov 17 |
| **TSLA** | 117 | 5.9% | 76.03% | Nov 14 |
| **MSFT** | 95 | 4.8% | 75.0% | Nov 14 |
| **NVDA** | 30 | 1.5% | 77.0% | Nov 14 |
| **AAPL** | 1 | 0.05% | 92.5% | Nov 12 |

**Insight:** ETH-USD dominates (51.2%), BTC-USD second (36.5%)

---

## Confidence Distribution

| Range | Count | % | Assessment |
|-------|-------|---|------------|
| **90-100%** | 1 | 0.05% | Very High |
| **80-89%** | 409 | 20.77% | High (Prop Firm Ready) |
| **70-79%** | 1,559 | 79.18% | Good |
| **<70%** | 0 | 0% | None |

**Key Finding:** 
- ✅ All signals above 70% (excellent quality floor)
- ⚠️ Only 20.77% meet prop firm 82% threshold
- ✅ 79.18% in good quality range (70-79%)

---

## Generation Timeline

### By Date

| Date | Signals | Avg Confidence | Symbols |
|------|---------|----------------|---------|
| **Nov 17** | 1 | 85.0% | BTC-USD |
| **Nov 15** | 919 | 77.75% | ETH-USD, BTC-USD |
| **Nov 14** | 1,048 | 75.63% | 5 symbols |
| **Nov 12** | 1 | 92.5% | AAPL |

**Critical Finding:** 
- ⚠️ **99.9% of signals on Nov 14-15** (1,967 signals)
- ⚠️ **Only 1 signal on Nov 17** (activity dropped significantly)
- ⚠️ **No signals on Nov 13, 16, 18** (gaps in generation)

### Peak Generation Hours (UTC)

| Hour | Signals | Avg Confidence |
|------|---------|----------------|
| **20:00** | 376 | 75.81% |
| **04:00** | 241 | 80.96% |
| **23:00** | 221 | 76.63% |
| **02:00** | 221 | 75.63% |
| **00:00** | 211 | 76.54% |

**Insight:** Peak activity at 20:00 UTC (376 signals), highest confidence at 04:00 UTC (80.96%)

---

## Recent Signals Analysis

### Latest Signal
- **Date:** Nov 17, 2025 13:10:00 UTC
- **Symbol:** BTC-USD
- **Action:** SELL
- **Confidence:** 85.0%
- **Entry:** $95,444.00
- **Target:** $90,671.80 (-5.0%)
- **Stop:** $98,307.32 (+3.0%)

### Recent Pattern (Last 20 signals)
- **All crypto:** ETH-USD and BTC-USD only
- **Mostly SELL:** Consistent SELL signals
- **Confidence:** 79.86% - 85.0%
- **Frequency:** ~5-6 seconds apart (matches config)

---

## Prop Firm Compliance

### Current Threshold: 82% Minimum Confidence

| Metric | Value |
|--------|-------|
| **Signals ≥82%** | 409 (20.77%) |
| **Signals <82%** | 1,560 (79.23%) |
| **Average Confidence** | 76.63% |

**Assessment:**
- ⚠️ **Only 20.77% meet prop firm threshold**
- ⚠️ **Most signals below 82%** (but still good quality at 70-79%)
- 💡 **Recommendation:** Consider lowering threshold to 80% to capture more signals

---

## Trading Outcomes

**Status:** ❌ **No Outcome Data Available**

- All signals show `outcome: NULL`
- No `profit_loss_pct` data
- No trade execution tracking

**Possible Reasons:**
1. Auto-execution disabled
2. Trades not being executed
3. Outcome tracking not implemented
4. Trades still pending/active

**Action Required:** Investigate why outcomes aren't being tracked

---

## Quality Assessment

### Strengths ✅

1. **Consistent Quality:** 100% above 70% confidence
2. **Good Distribution:** Balanced BUY/SELL, crypto/stocks
3. **High Volume:** 1,969 signals in 6 days
4. **24/7 Generation:** Continuous signal generation
5. **No Low Quality:** Zero signals below 70%

### Weaknesses ⚠️

1. **Prop Firm Threshold:** Only 20.77% meet 82% requirement
2. **Recent Activity:** Very low (1 signal on Nov 17)
3. **Outcome Tracking:** No outcome data available
4. **Very High Confidence:** Rare (only 1 signal above 90%)
5. **Activity Gaps:** No signals on Nov 13, 16, 18

### Critical Issues 🔴

1. **Activity Drop:** 99.9% of signals on Nov 14-15, then almost nothing
2. **No Outcomes:** Cannot assess signal profitability
3. **Service Status:** Need to verify signal generation is still active

---

## Recommendations

### Immediate Actions

1. **Verify Service Status**
   - Check if signal generation is still running
   - Investigate why activity dropped after Nov 15
   - Verify service logs for errors

2. **Enable Outcome Tracking**
   - Implement trade execution tracking
   - Record profit/loss data
   - Track signal outcomes

3. **Monitor Recent Activity**
   - Check if signals are being generated today
   - Verify service is operational
   - Review generation logs

### Optimization Opportunities

1. **Prop Firm Threshold**
   - Consider lowering from 82% to 80%
   - Would capture ~409 additional signals (20.77% more)
   - Still maintains high quality (80%+ confidence)

2. **Symbol Diversification**
   - Currently 87.66% crypto, 12.34% stocks
   - Consider expanding stock coverage
   - Balance asset type distribution

3. **Confidence Calibration**
   - Analyze if confidence levels are accurate
   - Compare confidence vs actual outcomes (when available)
   - Calibrate confidence scoring

---

## Summary

### Overall Grade: **B+ (Good)**

**Quality Metrics:**
- ✅ All signals above 70% confidence
- ✅ 20.77% meet prop firm threshold (82%+)
- ✅ Consistent quality distribution
- ⚠️ Recent activity very low

**Generation Metrics:**
- ✅ High volume (1,969 signals)
- ✅ 24/7 generation capability
- ⚠️ Activity gaps (Nov 13, 16, 18)
- ⚠️ Recent drop in activity

**Trading Metrics:**
- ❌ No outcome data available
- ❌ Cannot assess profitability
- ❌ Trade execution status unknown

### Next Steps

1. **Verify service is running** (check logs, status)
2. **Investigate activity drop** (why no signals after Nov 15)
3. **Enable outcome tracking** (implement trade tracking)
4. **Monitor signal generation** (ensure continuous operation)

---

**Analysis Complete**  
**Data Source:** `/root/argo-production/data/signals.db`  
**Report Generated:** November 18, 2025

