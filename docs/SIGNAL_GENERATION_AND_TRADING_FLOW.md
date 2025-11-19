# Signal Generation and Trading Flow - Complete Guide

**Date:** January 16, 2025  
**Version:** 1.0  
**Status:** Complete System Overview

---

## Executive Summary

This document explains the complete end-to-end flow of how signals are generated and how they trigger trading execution in the Argo-Alpine trading system.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Signal Generation Flow](#signal-generation-flow)
3. [Trading Execution Flow](#trading-execution-flow)
4. [Long and Short Position Handling](#long-and-short-position-handling)
5. [Complete End-to-End Flow](#complete-end-to-end-flow)
6. [Key Components](#key-components)
7. [Configuration](#configuration)

---

## System Overview

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Signal Generation Service                       │
│  (runs every 5 seconds, processes all symbols)              │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Fetch Data from Multiple Sources (Parallel)             │
│     - Alpaca Pro / Massive.com (market data)                │
│     - yfinance / Alpha Vantage (technical indicators)       │
│     - xAI Grok (sentiment)                                  │
│     - Sonar AI (AI analysis)                                │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Generate Source Signals                                 │
│     - Each data source generates its own signal             │
│     - Signals include: direction, confidence, price         │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Weighted Consensus Calculation                          │
│     - Combines all source signals using weights             │
│     - Detects market regime (BULL/BEAR/CHOP/CRISIS)        │
│     - Adjusts confidence based on regime                    │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Signal Validation                                       │
│     - Check confidence threshold (75%+ default)             │
│     - Validate data quality                                 │
│     - Generate AI reasoning                                 │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Store Signal in Database                                │
│     - SignalTracker stores with SHA-256 hash                │
│     - Sync to Alpine backend (async)                        │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Trading Execution (if auto_execute enabled)             │
│     - Validate trade against risk rules                     │
│     - Calculate position size                               │
│     - Submit order to Alpaca                                │
│     - Place bracket orders (stop/target)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Signal Generation Flow

### Step 1: Main Loop (`generate_signals_cycle`)

**Location:** `argo/argo/core/signal_generation_service.py:1810`

**Frequency:** Every 5 seconds

**Process:**
1. Get list of symbols to process (default: AAPL, NVDA, TSLA, MSFT, BTC-USD, ETH-USD)
2. Prioritize symbols by volatility (high volatility first)
3. Process symbols in batches of 6 (parallel)
4. For each symbol, call `generate_signal_for_symbol()`

### Step 2: Generate Signal for Symbol (`generate_signal_for_symbol`)

**Location:** `argo/argo/core/signal_generation_service.py:766`

**Process:**

#### 2.1 Early Exit Checks
- Check if symbol price changed significantly (< 0.5% change = skip)
- Return cached signal if no significant change

#### 2.2 Fetch Market Data (Parallel Race Condition)
- **Alpaca Pro** and **Massive.com** fetch in parallel
- Use first successful response (30s timeout)
- Generate signal from successful source
- Cancel remaining tasks once we have data

#### 2.3 Fetch Independent Sources (Parallel)
- **yfinance** - Technical indicators
- **Alpha Vantage** - Technical indicators (supplement)
- **xAI Grok** - Sentiment analysis (90s cache)
- **Sonar AI** - AI analysis (120s cache)
- **Chinese Models** - AI analysis (if available)

All fetch in parallel using `asyncio.gather()`

#### 2.4 Validate Source Signals
- Data quality monitor validates each signal
- Reject signals with quality issues
- Early exit if all signals rejected

#### 2.5 Calculate Weighted Consensus
- **Weighted Consensus Engine** combines all source signals
- Weights (configurable in `config.json`):
  - Alpaca Pro: 40%
  - Massive.com: 40%
  - yfinance: 25%
  - Alpha Vantage: 25%
  - xAI Grok: 20%
  - Sonar AI: 15%
- Detects market regime (BULL/BEAR/CHOP/CRISIS)
- Adjusts confidence based on regime

#### 2.6 Apply Confidence Threshold
- Check if consensus confidence >= threshold
- Threshold varies by regime:
  - TRENDING: 85%
  - CONSOLIDATION: 90%
  - VOLATILE: 88%
  - Default: 75% (or 88% if feature flag enabled)

#### 2.7 Build Final Signal
- Create signal dictionary with:
  - `symbol`: Stock/crypto symbol
  - `action`: BUY or SELL
  - `entry_price`: Entry price
  - `target_price`: Take profit price
  - `stop_price`: Stop loss price
  - `confidence`: Consensus confidence
  - `regime`: Market regime
  - `sources_used`: List of data sources
  - `timestamp`: UTC timestamp

#### 2.8 Generate AI Reasoning
- **SignalExplainer** generates human-readable reasoning
- Cached to avoid redundant API calls
- Minimum 20 characters required

#### 2.9 Cache Results
- Cache last price and signal for symbol
- Update volatility tracking
- Return signal or None

### Step 3: Store Signal

**Location:** `argo/argo/core/signal_generation_service.py:1851`

**Process:**
1. **SignalTracker** stores signal in database
2. Returns `signal_id` (SHA-256 hash)
3. Signal synced to Alpine backend (async, non-blocking)
4. Signal lifecycle tracked (if enabled)

---

## Trading Execution Flow

### Step 1: Check Auto-Execute

**Location:** `argo/argo/core/signal_generation_service.py:1885`

**Conditions:**
- `auto_execute` must be `true` in config
- `trading_engine` must be initialized
- Account must be available
- System must not be paused (dev mode only)

### Step 2: Get Trading Context

**Location:** `argo/argo/core/signal_generation_service.py:1969`

**Process:**
1. Get account details from Alpaca
2. Get existing positions (cached for 30s)
3. Update risk monitor with current equity
4. Sync position tracking in risk monitor

### Step 3: Validate Trade (`_validate_trade`)

**Location:** `argo/argo/core/signal_generation_service.py:1734`

**7-Layer Risk Protection:**

#### Layer 1: Account Status
- Check if trading is paused (daily loss limit)
- Check if account is blocked
- Check if trading is blocked

#### Layer 2: Prop Firm Rules (if enabled)
- Check risk monitor can trade
- Check position count limit
- Check confidence threshold (82%+ for prop firm)
- Check symbol restrictions

#### Layer 3: Daily Loss Limit
- Calculate daily P&L
- Check if daily loss limit exceeded (default: 5%)
- Pause trading if limit exceeded

#### Layer 4: Drawdown Protection
- Track peak equity
- Calculate current drawdown
- Check if max drawdown exceeded (default: 10%)
- Block trades if exceeded

#### Layer 5: Buying Power
- Calculate required capital (position size %)
- Check if sufficient buying power available
- Leave 5% buffer for margin

#### Layer 6: Existing Position
- Check if position already exists for symbol
- Skip if position exists

#### Layer 7: Correlation Limits
- Check correlation groups (tech, finance, energy, etc.)
- Check if max correlated positions reached (default: 3)
- Skip if limit exceeded

### Step 4: Execute Trade (`_execute_trade_if_valid`)

**Location:** `argo/argo/core/signal_generation_service.py:2017`

**Process:**
1. Call `_validate_trade()` - if fails, skip
2. Check existing position - if exists, skip
3. Check correlation limits - if exceeded, skip
4. Call `trading_engine.execute_signal(signal)`
5. Handle successful trade

### Step 5: Trading Engine Execution (`PaperTradingEngine.execute_signal`)

**Location:** `argo/argo/core/paper_trading_engine.py:337`

**Process:**

#### 5.1 Check Trade Allowed
- Check market hours (for stocks)
- Check account status
- Check symbol restrictions

#### 5.2 Prepare Order Details
- Calculate position size:
  - Base: `position_size_pct` (default: 10%)
  - Confidence multiplier: `1.0 + ((confidence - 75) / 25) * 0.5`
  - Volatility adjustment: `min(avg_volatility / asset_volatility, 1.5)`
  - Final: `base × confidence_mult × volatility_mult` (capped at `max_position_size_pct`)
- Calculate quantity: `position_value / entry_price`
- Determine order type: Market or Limit (based on config)

#### 5.3 Submit Main Order
- Create `MarketOrderRequest` or `LimitOrderRequest`
- Submit to Alpaca API
- Track order ID

#### 5.4 Place Bracket Orders
- **Stop Loss Order**: Closes position if price hits stop
  - For LONG: Stop below entry price
  - For SHORT: Stop above entry price (price rises = loss)
- **Take Profit Order**: Closes position if price hits target
  - For LONG: Target above entry price
  - For SHORT: Target below entry price (price falls = profit)
- Both placed automatically after main order

#### 5.5 Retry Logic
- If order fails, retry with exponential backoff
- Max attempts: 3 (configurable)
- Delay: `retry_delay_seconds × attempt_number`

### Step 6: Handle Successful Trade

**Location:** `argo/argo/core/signal_generation_service.py:2045`

**Process:**
1. Get order status from Alpaca
2. Record trade in performance tracker
3. Journal trade (Tradervue integration)
4. Update position cache
5. Log success

---

## Long and Short Position Handling

The system supports both **LONG** and **SHORT** trading positions. This section explains how signals are converted to positions and how position management works.

### Signal to Position Mapping

**Location:** `argo/argo/core/signal_generation_service.py:1924-1927`

Signals are generated with a `direction` (LONG or SHORT) which is converted to an `action`:

- **LONG direction** → **BUY action** → Opens LONG position
- **SHORT direction** → **SELL action** → Opens SHORT position

```python
direction = consensus["direction"]  # "LONG" or "SHORT"
action = "BUY" if direction == "LONG" else "SELL"
```

### Opening Positions

#### LONG Positions (BUY Signals)

**Location:** `argo/argo/core/paper_trading_engine.py:717-790`

When a **BUY signal** is executed:
1. Check for existing position
2. If **SHORT position exists** → Close SHORT (BUY to cover)
3. If **no position exists** → Open LONG (BUY to open)
4. Place bracket orders (stop loss below entry, take profit above entry)

**Example:**
```
BUY signal for AAPL @ $175.50
→ Opens LONG position
→ Stop Loss: $170.00 (below entry)
→ Take Profit: $184.00 (above entry)
```

#### SHORT Positions (SELL Signals)

**Location:** `argo/argo/core/paper_trading_engine.py:674-723`

When a **SELL signal** is executed:
1. Check for existing position
2. If **LONG position exists** → Close LONG (SELL to close)
3. If **no position exists** → **Open SHORT** (SELL to open)
4. Place bracket orders (stop loss above entry, take profit below entry)

**Example:**
```
SELL signal for SPY @ $450.00
→ Opens SHORT position
→ Stop Loss: $459.00 (above entry - price rises = loss)
→ Take Profit: $441.00 (below entry - price falls = profit)
```

### Closing Positions

The system intelligently handles position closing:

#### Closing LONG Positions
- **SELL signal** when LONG position exists → Closes LONG position
- Uses SELL order to close

#### Closing SHORT Positions
- **BUY signal** when SHORT position exists → Closes SHORT position
- Uses BUY order to cover (close) SHORT

### Position Flipping

The system allows flipping between LONG and SHORT:

**Location:** `argo/argo/core/signal_generation_service.py:2874-2914`

- **LONG → SHORT**: SELL signal when LONG exists → Closes LONG, then opens SHORT
- **SHORT → LONG**: BUY signal when SHORT exists → Closes SHORT, then opens LONG

**Example:**
```
Current: LONG AAPL @ $175.00
Signal: SELL AAPL @ $180.00
→ Closes LONG @ $180.00 (profit: +$5.00)
→ Opens SHORT @ $180.00
```

### Position Detection

**Location:** `argo/argo/core/paper_trading_engine.py:1441-1527`

The system properly detects LONG vs SHORT positions from Alpaca:
- Checks `side` attribute (enum or string)
- Falls back to quantity sign (negative = SHORT)
- Normalizes quantity to positive value for consistency

### Risk Management for SHORT Positions

**Location:** `argo/argo/core/paper_trading_engine.py:1108-1149`

SHORT positions have inverted risk management:

#### Stop Loss for SHORT
- **Must be ABOVE entry price** (price rises = loss)
- Validated: `stop_price > entry_price`
- Example: Entry $450, Stop $459 (2% above)

#### Take Profit for SHORT
- **Must be BELOW entry price** (price falls = profit)
- Validated: `target_price < entry_price`
- Example: Entry $450, Target $441 (2% below)

### Position Size Calculation

**Location:** `argo/argo/core/paper_trading_engine.py:792-984`

Position sizing works for both LONG and SHORT:
- Uses buying power for calculation
- Applies confidence multiplier
- Applies volatility adjustment
- Handles crypto (fractional) vs stocks (whole shares)

### Logging and Monitoring

Enhanced logging tracks SHORT positions:

**Opening SHORT:**
```
📉 Opening NEW SHORT position: SELL 10 SPY @ $450.00 ($4,500.00)
   🛡️  Stop Loss: $459.00 | 🎯 Take Profit: $441.00
   📊 Confidence: 85.0% | Risk: 2.00%
```

**Closing SHORT:**
```
🔄 Closing SHORT position: 10 SPY
   📉 SHORT Entry: $450.00 | Current: $441.00 | P&L: +2.00%
   💰 BUY 10 SPY @ $441.00 to cover SHORT position
```

### Verification Tools

Use these scripts to verify SHORT position handling:

1. **`scripts/verify_short_positions.py`** - Comprehensive verification
   - Checks database for SELL signals
   - Verifies Alpaca positions
   - Checks order history
   - Monitors for errors

2. **`scripts/test_short_position.py`** - Test SHORT opening
   - Generates test SELL signal
   - Executes to open SHORT
   - Verifies position and bracket orders

3. **`scripts/query_short_positions.py`** - Database queries
   - SELL signal execution rates
   - SHORT vs LONG comparison
   - Symbol-specific activity

### Common Scenarios

#### Scenario 1: Opening SHORT from SELL Signal
```
1. No position exists for SPY
2. SELL signal generated (SHORT direction)
3. System opens SHORT position
4. Places stop loss above entry
5. Places take profit below entry
```

#### Scenario 2: Closing LONG with SELL Signal
```
1. LONG position exists for AAPL @ $175
2. SELL signal generated
3. System closes LONG position
4. No new position opened
```

#### Scenario 3: Flipping LONG to SHORT
```
1. LONG position exists for TSLA @ $250
2. SELL signal generated @ $255
3. System closes LONG @ $255 (profit)
4. System opens SHORT @ $255
```

---

## Complete End-to-End Flow

### Example: Signal Generation → Trade Execution

```
Time: 09:30:00.000
┌─────────────────────────────────────────────────────────────┐
│ Signal Generation Service starts cycle                      │
│ Symbols: [AAPL, NVDA, TSLA, MSFT, BTC-USD, ETH-USD]        │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
Time: 09:30:00.100
┌─────────────────────────────────────────────────────────────┐
│ Processing AAPL (high volatility, prioritized)              │
│ 1. Fetch market data: Alpaca Pro + Massive.com (parallel)  │
│    → Alpaca Pro responds first (200ms)                     │
│    → Cancel Massive.com task                                │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
Time: 09:30:00.300
┌─────────────────────────────────────────────────────────────┐
│ 2. Fetch independent sources (parallel):                    │
│    - yfinance: Technical indicators (500ms)                 │
│    - Alpha Vantage: Technical indicators (600ms)            │
│    - xAI Grok: Sentiment (cached, 50ms)                     │
│    - Sonar AI: AI analysis (cached, 50ms)                   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
Time: 09:30:00.900
┌─────────────────────────────────────────────────────────────┐
│ 3. Source Signals Generated:                                │
│    - alpaca_pro: BUY @ $150.00, 85% confidence              │
│    - yfinance: BUY @ $150.00, 80% confidence                │
│    - alpha_vantage: BUY @ $150.00, 82% confidence           │
│    - x_sentiment: BUY @ $150.00, 75% confidence             │
│    - sonar: BUY @ $150.00, 78% confidence                   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
Time: 09:30:01.000
┌─────────────────────────────────────────────────────────────┐
│ 4. Weighted Consensus Calculation:                          │
│    - Combined confidence: 82.5%                             │
│    - Regime: TRENDING                                       │
│    - Adjusted confidence: 82.5% (no adjustment)             │
│    - Threshold: 85% (TRENDING regime)                       │
│    → BELOW THRESHOLD, REJECT                                │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
Time: 09:30:01.100
┌─────────────────────────────────────────────────────────────┐
│ Processing NVDA (next symbol)                               │
│ ... (same process) ...                                      │
│ Consensus: 88.5% confidence, TRENDING regime                │
│ → ABOVE THRESHOLD (85%), ACCEPT                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
Time: 09:30:02.000
┌─────────────────────────────────────────────────────────────┐
│ 5. Build Final Signal:                                      │
│    {                                                         │
│      "symbol": "NVDA",                                      │
│      "action": "BUY",                                       │
│      "entry_price": 450.00,                                 │
│      "target_price": 472.50,  // 5% profit                  │
│      "stop_price": 436.50,   // 3% stop                     │
│      "confidence": 88.5,                                    │
│      "regime": "TRENDING",                                  │
│      "sources_used": ["alpaca_pro", "yfinance", ...]        │
│    }                                                         │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
Time: 09:30:02.100
┌─────────────────────────────────────────────────────────────┐
│ 6. Generate AI Reasoning:                                   │
│    "Strong bullish momentum with high volume. Technical     │
│     indicators show oversold bounce. Sentiment positive."   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
Time: 09:30:02.200
┌─────────────────────────────────────────────────────────────┐
│ 7. Store Signal in Database:                                │
│    - SignalTracker stores with SHA-256 hash                 │
│    - signal_id: "abc123..."                                 │
│    - Sync to Alpine backend (async)                         │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
Time: 09:30:02.300
┌─────────────────────────────────────────────────────────────┐
│ 8. Trading Execution (auto_execute enabled):                │
│    a. Get trading context:                                  │
│       - Account: $100,000 equity, $100,000 buying power     │
│       - Existing positions: []                              │
│                                                              │
│    b. Validate trade (7-layer risk check):                  │
│       ✅ Account status: OK                                 │
│       ✅ Daily loss limit: OK                               │
│       ✅ Drawdown: OK                                       │
│       ✅ Buying power: OK                                   │
│       ✅ Existing position: None                            │
│       ✅ Correlation limits: OK                             │
│                                                              │
│    c. Calculate position size:                              │
│       - Base: 10% of $100,000 = $10,000                     │
│       - Confidence multiplier: 1.27x (88.5% confidence)     │
│       - Volatility adjustment: 1.2x (low volatility)        │
│       - Final: $10,000 × 1.27 × 1.2 = $15,240               │
│       - Capped at 15% = $15,000                             │
│       - Quantity: $15,000 / $450 = 33 shares                │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
Time: 09:30:02.500
┌─────────────────────────────────────────────────────────────┐
│ 9. Submit Order to Alpaca:                                  │
│    - Order Type: Market Order                               │
│    - Symbol: NVDA                                           │
│    - Side: BUY                                              │
│    - Quantity: 33 shares                                    │
│    - Time in Force: DAY                                     │
│    → Order ID: "order_12345"                                │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
Time: 09:30:02.600
┌─────────────────────────────────────────────────────────────┐
│ 10. Place Bracket Orders:                                   │
│     - Stop Loss: $436.50 (3% below entry)                   │
│     - Take Profit: $472.50 (5% above entry)                 │
│     → Both orders placed                                    │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
Time: 09:30:02.700
┌─────────────────────────────────────────────────────────────┐
│ 11. Record Trade:                                           │
│     - Performance tracker records entry                     │
│     - Tradervue integration journals trade                  │
│     - Position cache updated                                │
│     - Log: "✅ Trade executed: NVDA BUY - Order ID: ..."    │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
Time: 09:30:05.000
┌─────────────────────────────────────────────────────────────┐
│ Next cycle starts (every 5 seconds)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Components

### Signal Generation Service
- **File:** `argo/argo/core/signal_generation_service.py`
- **Purpose:** Main orchestrator for signal generation
- **Key Methods:**
  - `generate_signals_cycle()`: Main loop (every 5 seconds)
  - `generate_signal_for_symbol()`: Generate signal for one symbol
  - `_fetch_market_data_signals()`: Fetch market data (parallel)
  - `_fetch_independent_source_signals()`: Fetch independent sources (parallel)
  - `_calculate_consensus()`: Weighted consensus calculation
  - `_validate_trade()`: 7-layer risk validation
  - `_execute_trade_if_valid()`: Execute trade if valid

### Paper Trading Engine
- **File:** `argo/argo/core/paper_trading_engine.py`
- **Purpose:** Execute trades on Alpaca
- **Key Methods:**
  - `execute_signal()`: Execute signal with retry logic
  - `_execute_live()`: Execute live trade on Alpaca
  - `_prepare_order_details()`: Calculate position size
  - `_submit_main_order()`: Submit order to Alpaca
  - `_place_bracket_orders()`: Place stop/target orders

### Weighted Consensus Engine
- **File:** `argo/argo/core/weighted_consensus_engine.py`
- **Purpose:** Combine multiple source signals
- **Algorithm:** Weighted Consensus v6.0
- **Weights:** Configurable in `config.json`

### Signal Tracker
- **File:** `argo/argo/core/signal_tracker.py`
- **Purpose:** Store signals in database
- **Features:**
  - SHA-256 hash verification
  - Batch inserts for performance
  - SQLite database storage

### Data Sources
- **Alpaca Pro:** `argo/argo/core/data_sources/alpaca_pro_source.py`
- **Massive.com:** `argo/argo/core/data_sources/massive_source.py`
- **yfinance:** `argo/argo/core/data_sources/yfinance_source.py`
- **Alpha Vantage:** `argo/argo/core/data_sources/alpha_vantage_source.py`
- **xAI Grok:** `argo/argo/core/data_sources/xai_grok_source.py`
- **Sonar AI:** `argo/argo/core/data_sources/sonar_source.py`

---

## Configuration

### Key Settings in `config.json`

```json
{
  "trading": {
    "auto_execute": true,              // Enable automatic trading
    "min_confidence": 75.0,            // Minimum signal confidence
    "position_size_pct": 10,           // Base position size (%)
    "max_position_size_pct": 15,       // Maximum position size (%)
    "stop_loss": 0.03,                 // Stop loss (3%)
    "profit_target": 0.05,             // Take profit (5%)
    "max_correlated_positions": 3,     // Max correlated positions
    "max_drawdown_pct": 10,            // Max drawdown (%)
    "daily_loss_limit_pct": 5.0,       // Daily loss limit (%)
    "use_limit_orders": false,         // Use limit vs market orders
    "max_retry_attempts": 3            // Retry attempts
  },
  "data_sources": {
    "weights": {
      "alpaca_pro": 0.40,
      "massive": 0.40,
      "yfinance": 0.25,
      "alpha_vantage": 0.25,
      "x_sentiment": 0.20,
      "sonar": 0.15
    }
  }
}
```

---

## Summary

### Signal Generation
1. **Frequency:** Every 5 seconds
2. **Process:** Parallel data fetching → Source signals → Weighted consensus → Validation → Storage
3. **Data Sources:** 6 sources (Alpaca, Massive, yfinance, Alpha Vantage, xAI Grok, Sonar)
4. **Consensus:** Weighted Consensus v6.0 algorithm
5. **Threshold:** 75%+ confidence (regime-adjusted)

### Trading Execution
1. **Trigger:** Automatic if `auto_execute: true`
2. **Validation:** 7-layer risk protection
3. **Position Sizing:** Dynamic based on confidence and volatility
4. **Order Types:** Market or Limit orders
5. **Risk Management:** Stop loss and take profit automatically placed

### Key Features
- **Parallel Processing:** All data sources fetch in parallel
- **Early Exit:** Skip symbols with no significant price change
- **Caching:** Multiple levels of caching for performance
- **Risk Management:** 7-layer protection system
- **Retry Logic:** Exponential backoff for failed orders
- **Position Monitoring:** Continuous monitoring of open positions

---

**For Questions:**  
Signal Generation: signals@alpineanalytics.com  
Trading Execution: trading@alpineanalytics.com  
**Technical Support:** tech@alpineanalytics.com

