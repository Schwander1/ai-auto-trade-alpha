# Transaction Cost Model Assumptions

**Last Updated:** 2025-11-15  
**Model:** EnhancedTransactionCostModel

---

## Overview

The Enhanced Transaction Cost Model provides realistic cost estimates for backtesting by incorporating:
- Symbol-specific liquidity tiers
- Volume-based slippage (square-root model)
- Volatility-adjusted costs
- Market-specific adjustments

---

## Cost Components

### 1. Slippage

**Model:** Square-root slippage model

**Formula:**
```
slippage = base_slippage * sqrt(trade_size / avg_volume) * volatility_multiplier
```

**Assumptions:**
- Slippage increases with the square root of trade size relative to average volume
- Higher volatility increases slippage
- Base slippage varies by liquidity tier

**Liquidity Tiers:**
- **High Liquidity:** SPY, QQQ, AAPL, MSFT, GOOGL, NVDA
  - Base slippage: 0.01% (0.0001)
  - Volume threshold: > 10M shares/day
  
- **Medium Liquidity:** Most stocks
  - Base slippage: 0.02% (0.0002)
  - Volume threshold: 1M - 10M shares/day
  
- **Low Liquidity:** Small caps, some crypto
  - Base slippage: 0.05% (0.0005)
  - Volume threshold: < 1M shares/day

### 2. Spread

**Model:** Fixed percentage based on liquidity tier

**Assumptions:**
- Spread is constant for each liquidity tier
- Does not vary with trade size (simplification)
- Represents bid-ask spread

**Tiers:**
- **High Liquidity:** 0.01% (0.0001)
- **Medium Liquidity:** 0.02% (0.0002)
- **Low Liquidity:** 0.05% (0.0005)

### 3. Commission

**Model:** Fixed percentage

**Assumptions:**
- 0.1% (0.001) commission on all trades
- Applies to both entry and exit
- Represents typical retail broker commission

---

## Volatility Adjustments

**Model:** Volatility multiplier

**Formula:**
```
volatility_multiplier = 1 + (volatility - 0.02) * 2
```

**Assumptions:**
- Base volatility: 2% daily (0.02)
- Higher volatility increases costs
- Lower volatility decreases costs
- Multiplier ranges from ~0.8 (low vol) to ~1.6 (high vol)

---

## Market-Specific Adjustments

### Crypto Markets

**Multipliers:**
- Slippage: 1.5x
- Spread: 2.0x

**Rationale:**
- Crypto markets have higher spreads
- Lower liquidity than traditional markets
- More volatile execution

### Stock Markets

**Standard multipliers:**
- Slippage: 1.0x
- Spread: 1.0x

---

## Cost Application

### Entry Costs (LONG)
- **Pay:** Entry price + slippage + spread/2 + commission
- **Receive:** Entry price (before costs)

### Exit Costs (LONG)
- **Receive:** Exit price - slippage - spread/2 - commission
- **Pay:** Exit price (before costs)

### Entry Costs (SHORT)
- **Receive:** Entry price - slippage - spread/2 - commission
- **Pay:** Entry price (before costs)

### Exit Costs (SHORT)
- **Pay:** Exit price + slippage + spread/2 + commission
- **Receive:** Exit price (before costs)

---

## Limitations & Simplifications

### 1. Constant Spread
- **Reality:** Spread varies throughout the day
- **Model:** Fixed spread by liquidity tier
- **Impact:** Minor - spread is small relative to slippage

### 2. Square-Root Slippage
- **Reality:** Slippage can be linear or worse for very large trades
- **Model:** Square-root model (industry standard)
- **Impact:** May underestimate costs for very large trades

### 3. Volatility Calculation
- **Reality:** Volatility varies over time
- **Model:** Uses rolling volatility (20-day)
- **Impact:** Minor - captures most variation

### 4. Volume Assumption
- **Reality:** Volume varies throughout the day
- **Model:** Uses average daily volume
- **Impact:** Minor - average is representative

### 5. No Market Impact
- **Reality:** Large trades can move the market
- **Model:** No market impact (assumes small trades)
- **Impact:** Significant for very large trades

---

## Validation

### Expected Costs by Trade Size

**Small Trade (1% of daily volume):**
- High liquidity: ~0.02% total cost
- Medium liquidity: ~0.04% total cost
- Low liquidity: ~0.10% total cost

**Medium Trade (5% of daily volume):**
- High liquidity: ~0.05% total cost
- Medium liquidity: ~0.10% total cost
- Low liquidity: ~0.25% total cost

**Large Trade (20% of daily volume):**
- High liquidity: ~0.10% total cost
- Medium liquidity: ~0.20% total cost
- Low liquidity: ~0.50% total cost

---

## Comparison to Simple Model

### Simple Model
- Fixed 0.05% slippage
- Fixed 0.02% spread
- Fixed 0.1% commission
- **Total:** ~0.17% per trade (round trip: ~0.34%)

### Enhanced Model
- Variable slippage (0.01% - 0.50%+)
- Variable spread (0.01% - 0.05%)
- Fixed 0.1% commission
- **Total:** 0.12% - 0.65%+ per trade (round trip: ~0.24% - 1.30%+)

**Key Difference:**
- Enhanced model is **more realistic** for large trades
- Enhanced model is **more favorable** for small trades on high-liquidity symbols
- Enhanced model **better reflects** actual trading costs

---

## Recommendations

### When to Use Enhanced Model
- ✅ **Always** for production backtests
- ✅ When trade sizes vary significantly
- ✅ When trading multiple symbols with different liquidity
- ✅ When accuracy is important

### When Simple Model is Acceptable
- ⚠️ Quick backtests
- ⚠️ Small trade sizes only
- ⚠️ Single high-liquidity symbol
- ⚠️ Rough estimates

---

## References

1. **Square-Root Slippage Model:** Almgren & Chriss (2000)
2. **Transaction Cost Modeling:** Best practices from quantitative finance
3. **Industry Standards:** Typical retail broker costs

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-15

