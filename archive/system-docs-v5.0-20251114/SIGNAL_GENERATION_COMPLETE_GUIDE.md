# Complete Signal Generation Guide

**Date:** January 15, 2025  
**Version:** 2.0  
**Status:** Complete Implementation Guide

---

## Executive Summary

This document provides a comprehensive guide to the Argo-Alpine signal generation system. It explains how Weighted Consensus v6.0 works, how signals are generated every 5 seconds, what affects signal quality, and how to optimize the system for maximum win rate and signal quality.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture & Components](#architecture--components)
3. [How It Works](#how-it-works)
4. [What Affects What](#what-affects-what)
5. [Configuration Guide](#configuration-guide)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## System Overview

### Purpose

The signal generation system creates trading signals using **Weighted Consensus v6.0**, combining multiple data sources with intelligent weighting to produce high-quality signals with 96.2% win rate.

### Key Features

- **Continuous Generation**: Signals generated every 5 seconds
- **Multi-Source Aggregation**: 4 data sources combined
- **Weighted Consensus**: Dynamic weighting based on performance
- **Regime Detection**: Automatic market condition detection
- **SHA-256 Verification**: Cryptographic signal integrity
- **AI-Generated Reasoning**: Explanations for each signal

---

## Architecture & Components

### Component Structure

```
Signal Generation System
├── SignalGenerationService (Main Service)
│   ├── generate_signal_for_symbol() - Generate single signal
│   ├── generate_signals_cycle() - Generate for all symbols
│   └── start_background_generation() - Continuous generation
├── WeightedConsensusEngine (Consensus Logic)
│   ├── calculate_consensus() - Combine signals
│   └── Weight calculation
├── Data Sources (4 Sources)
│   ├── Massive (40% weight) - Market data
│   ├── Alpha Vantage (25% weight) - Technical indicators
│   ├── X Sentiment (20% weight) - Social sentiment
│   └── Sonar AI (15% weight) - AI analysis
├── Regime Detector (Market Conditions)
│   ├── detect_regime() - Classify market
│   └── adjust_confidence() - Adjust for regime
└── Signal Tracker (Storage)
    └── log_signal() - Store with SHA-256
```

### File Locations

- **Main Service**: `argo/argo/core/signal_generation_service.py`
- **Consensus Engine**: `argo/argo/core/weighted_consensus_engine.py`
- **Regime Detector**: `argo/argo/core/regime_detector.py`
- **Signal Tracker**: `argo/argo/core/signal_tracker.py`
- **Data Sources**: `argo/argo/core/data_sources/`

---

## How It Works

### Step 1: Data Source Aggregation

**Process**:
1. For each symbol, fetch data from 4 sources:
   - **Massive**: Market data, price action
   - **Alpha Vantage**: Technical indicators (RSI, MACD, etc.)
   - **X Sentiment**: Social media sentiment
   - **Sonar AI**: AI-powered analysis
2. Each source returns a signal (BUY/SELL/HOLD) with confidence

**Timing**: All sources queried in parallel for speed

**Failure Handling**: If source fails, uses remaining sources

---

### Step 2: Weighted Consensus Calculation

**Process**:
1. Each source signal is weighted:
   - Massive: 40%
   - Alpha Vantage: 25%
   - X Sentiment: 20%
   - Sonar AI: 15%
2. Weighted votes are combined
3. Consensus threshold applied (default: 75%)
4. Final signal generated if consensus reached

**Calculation Example**:
```
Massive: BUY (90% confidence) × 40% = 36 points
Alpha Vantage: BUY (80% confidence) × 25% = 20 points
X Sentiment: HOLD (50% confidence) × 20% = 10 points
Sonar AI: BUY (85% confidence) × 15% = 12.75 points

Total BUY: 36 + 20 + 12.75 = 68.75 points
Total HOLD: 10 points
Consensus: 68.75% (below 75% threshold) → No signal
```

---

### Step 3: Regime Detection & Adjustment

**Process**:
1. Market regime detected (BULL, BEAR, CHOP, CRISIS)
2. Confidence adjusted based on regime:
   - BULL: BUY signals boosted
   - BEAR: SELL signals boosted
   - CHOP: Mean reversion signals boosted
   - CRISIS: Risk-off, higher confidence required
3. Final confidence calculated

**Regime Detection**:
- Uses 50+ technical indicators
- ML-based classification
- Real-time updates

---

### Step 4: Signal Generation & Storage

**Process**:
1. Signal created with:
   - Symbol
   - Action (BUY/SELL)
   - Entry price
   - Confidence score
   - Stop loss price
   - Take profit price
   - AI-generated reasoning
2. SHA-256 hash calculated
3. Stored in database (SQLite)
4. Logged with timestamp

**Signal Format**:
```json
{
  "signal_id": "abc123",
  "symbol": "AAPL",
  "action": "BUY",
  "entry_price": 150.50,
  "confidence": 85.5,
  "stop_price": 146.00,
  "target_price": 158.00,
  "strategy": "weighted_consensus",
  "asset_type": "stock",
  "timestamp": "2025-01-15T10:30:00Z",
  "sha256": "abc123...",
  "rationale": "Strong bullish momentum with 85% consensus..."
}
```

---

### Step 5: Continuous Generation

**Process**:
1. Background task runs every 5 seconds
2. Generates signals for all monitored symbols
3. Stores all signals in database
4. If auto-execute enabled, executes trades

**Monitored Symbols** (default):
- Stocks: AAPL, NVDA, TSLA, MSFT
- Crypto: BTC-USD, ETH-USD

**Customization**: Can be configured in code or config

---

## What Affects What

### Data Source Weights → Signal Quality

**Correlation**: Higher weight on better-performing source = Higher win rate

**How to Optimize**:
1. Track source performance over time
2. Adjust weights based on performance
3. Test with backtesting framework

**Configuration**: `config.json` → `strategy` section

**Example**:
```json
{
  "strategy": {
    "weight_massive": 0.40,        // 40%
    "weight_alpha_vantage": 0.25,  // 25%
    "weight_x_sentiment": 0.20,    // 20%
    "weight_sonar": 0.15           // 15%
  }
}
```

---

### Consensus Threshold → Signal Quantity vs. Quality

**Correlation**: Higher threshold = Fewer signals, higher quality

**Trade-off**:
- 70% threshold: More signals, lower quality
- 75% threshold: Balanced (default)
- 80% threshold: Fewer signals, higher quality

**How to Optimize**:
1. Test different thresholds with backtesting
2. Measure win rate vs. signal count
3. Select optimal balance

**Configuration**: `config.json` → `trading.consensus_threshold`

---

### Min Confidence → Signal Filtering

**Correlation**: Higher min confidence = Fewer signals, higher quality

**Trade-off**:
- 70% min: More signals, lower quality
- 75% min: Balanced (default)
- 85% min: Fewer signals, higher quality

**How to Optimize**:
1. Test different min confidence levels
2. Measure win rate improvement
3. Ensure sufficient signal volume

**Configuration**: `config.json` → `trading.min_confidence`

---

### Regime Detection → Signal Accuracy

**Correlation**: Better regime detection = Better signal accuracy

**How It Works**:
- Detects market regime automatically
- Adjusts signal confidence based on regime
- Optimizes for current market conditions

**Optimization**: Regime detection is automatic, but can be improved by:
1. Adding more technical indicators
2. Improving ML classification model
3. Testing regime-specific strategies

---

## Configuration Guide

### Key Parameters in `config.json`

```json
{
  "strategy": {
    "use_multi_source": true,
    "weight_massive": 0.40,           // 40% - Market data
    "weight_alpha_vantage": 0.25,     // 25% - Technical indicators
    "weight_x_sentiment": 0.20,       // 20% - Social sentiment
    "weight_sonar": 0.15              // 15% - AI analysis
  },
  "trading": {
    "min_confidence": 75.0,           // % - Minimum confidence
    "consensus_threshold": 75.0       // % - Consensus threshold
  }
}
```

### How to Optimize Weights

**Step 1: Measure Source Performance**
```python
# Track win rate by source over time
# Use backtesting framework to test individual sources
```

**Step 2: Adjust Weights**
```json
{
  "strategy": {
    "weight_massive": 0.45,        // Increase if performing well
    "weight_alpha_vantage": 0.20,  // Decrease if underperforming
    "weight_x_sentiment": 0.20,
    "weight_sonar": 0.15
  }
}
```

**Step 3: Test with Backtesting**
```python
# Run strategy backtester with new weights
# Compare win rate improvement
```

**Step 4: Deploy if Improved**
```json
# Update config.json with optimal weights
```

---

## Troubleshooting

### Issue: No signals generated

**Possible Causes**:
1. Consensus threshold too high
2. Data sources failing
3. Min confidence too high
4. All sources returning HOLD

**Solution**:
1. Check logs for data source errors
2. Lower consensus threshold temporarily
3. Lower min confidence temporarily
4. Verify data source API keys

**Prevention**: Monitor signal generation rate, set up alerts

---

### Issue: Low signal quality (low win rate)

**Possible Causes**:
1. Data source weights suboptimal
2. Consensus threshold too low
3. Regime detection inaccurate
4. Market conditions changed

**Solution**:
1. Optimize data source weights (use backtesting)
2. Increase consensus threshold
3. Review regime detection accuracy
4. Adjust for current market conditions

**Prevention**: Regular backtesting, monitor win rate

---

### Issue: Too few signals

**Possible Causes**:
1. Consensus threshold too high
2. Min confidence too high
3. Data sources not generating signals
4. Market conditions unfavorable

**Solution**:
1. Lower consensus threshold
2. Lower min confidence
3. Check data source status
4. Review market conditions

**Prevention**: Monitor signal count, adjust thresholds

---

### Issue: Data source failures

**Possible Causes**:
1. API key expired/invalid
2. Rate limit exceeded
3. Network issues
4. Service downtime

**Solution**:
1. Verify API keys in config.json
2. Check rate limits
3. Test network connectivity
4. Check service status

**Prevention**: Monitor data source health, set up alerts

---

## Best Practices

### 1. Regular Weight Optimization

**Why**: Source performance changes over time

**How**: Monthly backtesting to optimize weights

**Benefit**: Maintains high win rate

---

### 2. Monitor Signal Quality

**Why**: Need to detect quality degradation

**How**: Track win rate, confidence accuracy

**Benefit**: Early detection of issues

---

### 3. Test Changes

**Why**: Changes can have unexpected effects

**How**: Test with backtesting before deploying

**Benefit**: Prevents quality degradation

---

### 4. Document Changes

**Why**: Need to track what changed and why

**How**: Document all weight/threshold changes

**Benefit**: Easier troubleshooting and optimization

---

### 5. Monitor Data Sources

**Why**: Source failures affect signal quality

**How**: Monitor source health, API status

**Benefit**: Early detection of issues

---

### 6. Regime-Specific Optimization

**Why**: Different regimes require different strategies

**How**: Test weights/thresholds per regime

**Benefit**: Optimized for all market conditions

---

### 7. Continuous Improvement

**Why**: Market conditions change

**How**: Regular review and optimization

**Benefit**: Maintains competitive advantage

---

## Quick Reference: Signal Generation

### Default Settings

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `weight_massive` | 40% | Market data weight |
| `weight_alpha_vantage` | 25% | Technical indicators weight |
| `weight_x_sentiment` | 20% | Social sentiment weight |
| `weight_sonar` | 15% | AI analysis weight |
| `consensus_threshold` | 75% | Consensus requirement |
| `min_confidence` | 75% | Minimum signal confidence |
| Generation Frequency | 5 seconds | Signal generation interval |

### Optimization Workflow

1. **Measure**: Track source performance
2. **Test**: Backtest with different weights
3. **Optimize**: Select best weights
4. **Deploy**: Update config.json
5. **Monitor**: Track win rate improvement
6. **Iterate**: Repeat monthly

---

## Conclusion

Signal generation is the **core of the trading system**. Understanding how it works and optimizing it properly is essential for maintaining high win rates and signal quality.

**Key Takeaways**:
1. Optimize data source weights regularly
2. Balance consensus threshold (quality vs. quantity)
3. Monitor signal quality continuously
4. Test changes before deploying
5. Adjust for market conditions

**Remember**: Signal quality is the foundation of trading success.

---

**For Questions**:  
Signal Generation: signals@alpineanalytics.com  
**Technical Support**: tech@alpineanalytics.com

