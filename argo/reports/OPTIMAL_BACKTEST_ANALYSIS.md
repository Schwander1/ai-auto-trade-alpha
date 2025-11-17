# Optimal Backtest Configuration Analysis

**Generated:** 2025-11-16 17:18:47

---

## Executive Summary

This report analyzes all backtest iterations to identify the **optimal configuration** for production use.

---

## 📊 Iteration Rankings (Composite Score)

| Rank | Iteration | Score | Win Rate | Return | Sharpe | Drawdown | Profit Factor |
|------|-----------|-------|----------|--------|--------|----------|---------------|
| 1 | **ITERATIVE_V7** | 0.688 | 43.31% | 43.06% | 0.86 | -23.21% | 0.98 |
| 2 | **ITERATIVE_V5** | 0.687 | 43.27% | 42.93% | 0.86 | -23.20% | 0.97 |
| 3 | **ITERATIVE_V6** | 0.687 | 43.27% | 42.93% | 0.86 | -23.20% | 0.97 |
| 4 | **ITERATIVE_V4** | 0.687 | 43.04% | 43.59% | 0.86 | -23.73% | 0.95 |
| 5 | **ITERATIVE_V3** | 0.681 | 43.07% | 42.24% | 0.86 | -23.35% | 0.94 |
| 6 | **ITERATIVE_V8** | 0.672 | 47.02% | 36.89% | 0.85 | -23.41% | 1.15 |
| 7 | **ITERATIVE_V9** | 0.590 | 49.03% | 17.31% | 0.85 | -23.09% | 1.39 |
| 8 | **ITERATIVE_V11** | 0.573 | 49.39% | 13.19% | 0.80 | -21.93% | 1.50 |
| 9 | **ITERATIVE_V10** | 0.556 | 49.74% | 11.15% | 0.66 | -18.50% | 1.47 |

---

## 🏆 Optimal Configuration: **ITERATIVE_V7**

### Performance Metrics
- **Composite Score:** 0.688
- **Win Rate:** 43.31%
- **Total Return:** 43.06%
- **Sharpe Ratio:** 0.86
- **Max Drawdown:** -23.21%
- **Profit Factor:** 0.98
- **Total Trades:** 6,075

### Configuration
```json
{
  "min_confidence": 55.0,
  "initial_capital": 100000,
  "symbol_specific_optimizations": true,
  "adaptive_stops": true,
  "trailing_stops": true,
  "position_sizing": true
}
```

---

## 📈 Detailed Comparison

### Win Rate Analysis

| Iteration | Win Rate |
|-----------|----------|
| ITERATIVE_V10 | 49.74% |
| ITERATIVE_V11 | 49.39% |
| ITERATIVE_V9 | 49.03% |
| ITERATIVE_V8 | 47.02% |
| ITERATIVE_V7 | 43.31% |

### Return Analysis

| Iteration | Return |
|-----------|--------|
| ITERATIVE_V4 | 43.59% |
| ITERATIVE_V7 | 43.06% |
| ITERATIVE_V5 | 42.93% |
| ITERATIVE_V6 | 42.93% |
| ITERATIVE_V3 | 42.24% |

### Sharpe Ratio Analysis

| Iteration | Sharpe |
|-----------|--------|
| ITERATIVE_V4 | 0.86 |
| ITERATIVE_V5 | 0.86 |
| ITERATIVE_V6 | 0.86 |
| ITERATIVE_V7 | 0.86 |
| ITERATIVE_V3 | 0.86 |

### Drawdown Analysis

| Iteration | Drawdown |
|-----------|----------|
| ITERATIVE_V10 | -18.50% |
| ITERATIVE_V11 | -21.93% |
| ITERATIVE_V9 | -23.09% |
| ITERATIVE_V5 | -23.20% |
| ITERATIVE_V6 | -23.20% |

### Profit Factor Analysis

| Iteration | Profit Factor |
|-----------|---------------|
| ITERATIVE_V11 | 1.50 |
| ITERATIVE_V10 | 1.47 |
| ITERATIVE_V9 | 1.39 |
| ITERATIVE_V8 | 1.15 |
| ITERATIVE_V7 | 0.98 |

---

## 🎯 Recommendations

### Best Overall: **ITERATIVE_V7**
- **Best for:** Production use, balanced performance
- **Strengths:** Good Returns (43.06%)
- **Trade-offs:** Drawdown: -23.21%

### Alternative Configurations


- **Best Win Rate:** ITERATIVE_V10 (49.74%)
- **Best Returns:** ITERATIVE_V4 (43.59%)
- **Best Sharpe:** ITERATIVE_V4 (0.86)
- **Best Drawdown:** ITERATIVE_V10 (-18.50%)

---

## 📝 Conclusion

**Recommended Configuration:** **ITERATIVE_V7**

This configuration provides the best overall balance of:
- Risk-adjusted returns (Sharpe ratio)
- Profitability (profit factor)
- Return generation
- Risk management

**Next Steps:**
1. Use ITERATIVE_V7 configuration for production
2. Monitor performance in live trading
3. Consider fine-tuning based on specific symbol performance
4. Continue iterative improvements

---

**Report Generated:** 2025-11-16 17:18:47
