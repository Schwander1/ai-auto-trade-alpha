# Extended Backtest Report - 20 Years, 12 Symbols

**Date:** 2025-11-15  
**Status:** ✅ **COMPLETE**

---

## Configuration

### Symbols Tested (12 total)
- **Stocks (8):** AAPL, NVDA, TSLA, MSFT, GOOGL, META, AMD, AMZN
- **ETFs (2):** SPY, QQQ
- **Crypto (2):** BTC-USD, ETH-USD

### Time Period
- **Period:** 20 years (or maximum available)
- **Data Source:** Massive S3 (if configured) or yfinance (fallback)

### Configurations Tested (5)
1. **Baseline** - No optimizations
2. **Weight Optimization** - Optimized source weights
3. **Regime Weights** - Regime-based weight adaptation
4. **Confidence 88** - Higher confidence threshold
5. **All Optimizations** - All features enabled

### Signal Generation Parameters (Adjusted)
- **RSI Thresholds:** 40/60 (was 30/70) - More signals
- **Base Confidence:** 65% (was 70%) - Lower threshold
- **Minimum Confidence:** 60% (was 65%) - More trades
- **MACD Confidence:** 68% (was 72%) - Lower threshold
- **Backtest Min Confidence:** 65% (was 70%) - More trades

---

## Expected Improvements

### Signal Generation
- **2-3x more signals** due to lowered thresholds
- **More trades** in backtests for better validation
- **Better framework testing** with increased activity

### Data Coverage
- **20 years** of historical data (vs 5 years before)
- **12 symbols** tested (vs 6 before)
- **60 total backtests** (vs 30 before)

---

## Results

See `argo/reports/comprehensive_backtest_results.json` for full results.

---

## Next Steps

1. **Review Results** - Analyze performance across all configurations
2. **Optimize Parameters** - Fine-tune based on backtest findings
3. **Statistical Analysis** - Run statistical significance tests
4. **Production Deployment** - Deploy best-performing configuration

---

**Status:** ✅ **COMPLETE**  
**Total Backtests:** 60 (12 symbols × 5 configurations)

