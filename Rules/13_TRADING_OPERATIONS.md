# Trading Operations Rules

**Last Updated:** January 15, 2025  
**Version:** 2.0  
**Applies To:** Argo Trading Engine

---

## Overview

Trading operations rules for signal generation, risk management, position monitoring, and trade execution in the Argo trading system.

**Strategic Context:** Signal quality targets (96%+ win rate) align with strategic goals defined in [24_VISION_MISSION_GOALS.md](24_VISION_MISSION_GOALS.md) Goal 1.

---

## Signal Generation

### Signal Generation Service

**Component:** `argo/argo/core/signal_generation_service.py`

#### Key Rules

- **Generation Frequency:** Signals generated every 5 seconds
- **Multi-Source Aggregation:** Uses 6 data sources (Alpaca Pro, Massive.com, yfinance, Alpha Vantage, xAI Grok, Sonar AI)
- **Weighted Consensus:** Uses Weighted Consensus v6.0 algorithm
- **Minimum Confidence:** 60% confidence threshold required (configurable in config.json)
- **SHA-256 Verification:** All signals include SHA-256 hash for integrity
- **AI Reasoning:** All signals include AI-generated reasoning (minimum 20 characters)

#### Data Sources

**Current Weights (configurable in `config.json`):**
- Alpaca Pro: 40% weight (primary market data, real-time)
- Massive.com: 40% weight (fallback market data)
- yfinance: 25% weight (primary technical indicators, free)
- Alpha Vantage: 25% weight (supplement technical indicators)
- xAI Grok: 20% weight (sentiment analysis, Option 2B optimized)
- Sonar AI: 15% weight (AI analysis, optimized with caching)

**Priority Order:**
1. Alpaca Pro → Massive.com (fallback)
2. yfinance → Alpha Vantage (supplement)
3. xAI Grok (Option 2B: market hours stocks, 24/7 crypto, 90s cache)
4. Sonar AI (market hours stocks, 24/7 crypto, 120s cache)

**Rule:** Weights must sum to ~1.0 (±0.05 tolerance)
**Rule:** Primary sources tried first, fallbacks used if primary fails
**Rule:** Multiple sources can contribute to same signal (highest confidence used)

#### Market Regime Detection

**Regimes:** BULL, BEAR, CHOP, CRISIS

**Rule:** Confidence adjusted based on market regime
- BULL: Standard confidence
- BEAR: Slightly reduced confidence
- CHOP: Reduced confidence
- CRISIS: Significantly reduced confidence, higher threshold

---

## Risk Management

### 7-Layer Risk Protection System

**Component:** `argo/argo/core/signal_generation_service.py` → `_validate_trade()`

#### Layer 1: Account Status Checks
- **Rule:** Verify account is not blocked
- **Rule:** Verify trading is not paused
- **Rule:** Verify account has trading permissions

#### Layer 2: Confidence Thresholds
- **Rule:** Minimum confidence: 60% (configurable, current: 60%)
- **Rule:** Consensus threshold: 60% (configurable)
- **Action:** Reject signals below threshold

#### Layer 3: Position Size Limits
- **Rule:** Default position size: 9% of capital (configurable, current: 9%)
- **Rule:** Maximum position size: 16% of capital (configurable, current: 16%)
- **Rule:** Position size adjusted by confidence
- **Rule:** Position size adjusted by volatility

#### Layer 4: Correlation Limits
- **Rule:** Maximum correlated positions: 5 (configurable, current: 5)
- **Rule:** Check correlation groups before trade
- **Action:** Reject if correlation limit exceeded

#### Layer 5: Daily Loss Limits
- **Rule:** Daily loss limit: 5% of equity (configurable, current: 5%)
- **Rule:** Pause trading if limit exceeded
- **Action:** Circuit breaker activates

#### Layer 6: Drawdown Protection
- **Rule:** Maximum drawdown: 20% from peak equity (configurable, current: 20%)
- **Rule:** Track peak equity continuously
- **Action:** Block trades if drawdown exceeded

#### Layer 7: Buying Power Checks
- **Rule:** Verify sufficient buying power
- **Rule:** Leave 5% buffer for margin
- **Action:** Reject if insufficient capital

---

## Trade Execution

### Paper Trading Engine

**Component:** `argo/argo/core/paper_trading_engine.py`

#### Order Types

**Market Orders:**
- **Default:** Used when `use_limit_orders: false`
- **Execution:** Immediate execution at market price
- **Use When:** High confidence, urgent execution needed

**Limit Orders:**
- **Enabled:** When `use_limit_orders: true`
- **Offset:** Configurable offset from current price (default: 0.1%)
- **Use When:** Want better price, can wait

#### Bracket Orders

**Rule:** Always place bracket orders after primary trade
- **Stop-Loss:** Automatic stop-loss order
- **Take-Profit:** Automatic take-profit order
- **Configuration:** From `config.json` (profit_target, stop_loss)

#### Position Sizing

**Calculation:**
1. Base size: `position_size_pct` of account balance
2. Confidence adjustment: Scale by signal confidence
3. Volatility adjustment: Reduce for high volatility
4. Final size: Min of calculated size and `max_position_size_pct`

**Rule:** Minimum 1 share/coin (even for expensive assets)

#### Retry Logic

**Rule:** Exponential backoff for API failures
- **Max Attempts:** 3 (configurable)
- **Initial Delay:** 1 second (configurable)
- **Backoff:** Exponential (1s, 2s, 4s)

---

## Position Monitoring

### Real-Time Position Tracking

**Component:** `argo/argo/core/signal_generation_service.py` → `monitor_positions()`

#### Monitoring Rules

- **Frequency:** Check positions every 30 seconds
- **Cache:** Position cache TTL: 30 seconds
- **Actions:**
  - Check stop-loss levels
  - Check take-profit levels
  - Auto-close if targets hit
  - Record exit in performance tracker

#### Stop-Loss Execution

**Rule:** Automatically close position if stop-loss hit
- **Trigger:** Current price <= stop-loss price (for long)
- **Action:** Market order to close position
- **Tracking:** Record exit in performance tracker

#### Take-Profit Execution

**Rule:** Automatically close position if take-profit hit
- **Trigger:** Current price >= take-profit price (for long)
- **Action:** Market order to close position
- **Tracking:** Record exit in performance tracker

---

## Performance Tracking

### Unified Performance Tracker

**Component:** `argo/argo/tracking/unified_tracker.py`

#### Trade Recording

**Entry Recording:**
- **When:** After successful trade execution
- **Data:** Trade ID, symbol, entry price, quantity, timestamp
- **Verification:** SHA-256 hash for integrity

**Exit Recording:**
- **When:** Position closed (stop-loss, take-profit, manual)
- **Data:** Trade ID, exit price, P&L, timestamp
- **Verification:** SHA-256 hash for integrity

#### Metrics Calculated

- **Total P&L:** Sum of all trade profits/losses
- **Win Rate:** Percentage of profitable trades
- **Sharpe Ratio:** Risk-adjusted returns
- **Max Drawdown:** Maximum portfolio decline
- **Average Win/Loss:** Average profit vs average loss

---

## Environment-Specific Behavior

**See:** [16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md) for complete environment differences

### Quick Reference

**Development:**
- Dev Alpaca account (automatic)
- Trading can be disabled
- Optional signal storage
- **Cursor-Aware:** Automatically pauses when Cursor is closed or computer is asleep
- **Auto-Resume:** Automatically resumes when Cursor starts or computer wakes up
- Only trades when actively working

**Production:**
- Production Alpaca account (automatic)
- Trading always enabled
- Required signal storage
- Always active (24/7, never pauses)

---

## Configuration

### Trading Configuration (`config.json` → `trading`)

**Required Parameters:**
- `min_confidence`: 60.0 (minimum signal confidence, current: 60%)
- `consensus_threshold`: 60.0 (consensus requirement, current: 60%)
- `profit_target`: 0.05 (5% profit target)
- `stop_loss`: 0.025 (2.5% stop loss, current: 2.5%)
- `position_size_pct`: 9 (default position size %, current: 9%)
- `max_position_size_pct`: 16 (maximum position size %, current: 16%)
- `max_correlated_positions`: 5 (correlation limit, current: 5)
- `max_drawdown_pct`: 20 (maximum drawdown %, current: 20%)
- `daily_loss_limit_pct`: 5.0 (daily loss limit %, current: 5%)
- `auto_execute`: true (enable automatic trading)

**See:** [06_CONFIGURATION.md](06_CONFIGURATION.md) for full configuration details

---

## Best Practices

### DO
- ✅ Always validate trades through all 7 risk layers
- ✅ Monitor positions continuously
- ✅ Record all trades in performance tracker
- ✅ Use bracket orders for risk management
- ✅ Adjust position size based on confidence and volatility
- ✅ Respect daily loss limits
- ✅ Track peak equity for drawdown calculation

### DON'T
- ❌ Execute trades without risk validation
- ❌ Ignore correlation limits
- ❌ Skip position monitoring
- ❌ Trade without stop-loss/take-profit
- ❌ Exceed position size limits
- ❌ Trade after daily loss limit exceeded
- ❌ Ignore drawdown protection

---

## Prop Firm Trading (Argo Capital Only)

### Prop Firm Account Separation

**CRITICAL:** Prop firm trading uses a completely separate Alpaca account and is isolated from regular trading.

**Rule:** When `prop_firm.enabled = true`, the system automatically uses the `prop_firm_test` account instead of dev/production accounts.

**Rule:** Prop firm trading and regular trading NEVER interact or share positions.

**Rule:** Prop firm risk monitoring is completely independent from regular trading risk management.

### Prop Firm Configuration

**Component:** `argo/config.json` → `prop_firm` section

**Required Configuration:**
```json
{
  "prop_firm": {
    "enabled": true,
    "account": "prop_firm_test",
    "risk_limits": {
      "max_drawdown_pct": 2.0,
      "daily_loss_limit_pct": 4.5,
      "max_position_size_pct": 3.0,
      "min_confidence": 82.0,
      "max_positions": 3,
      "max_stop_loss_pct": 1.5
    },
    "monitoring": {
      "enabled": true,
      "check_interval_seconds": 5,
      "alert_on_warning": true,
      "auto_shutdown": true
    }
  },
  "alpaca": {
    "prop_firm_test": {
      "api_key": "...",
      "secret_key": "...",
      "paper": true
    }
  }
}
```

### Prop Firm Risk Monitoring

**Component:** `argo/argo/risk/prop_firm_risk_monitor.py`

**Rules:**
- **Real-time Monitoring:** Checks risk every 5 seconds (configurable)
- **Drawdown Tracking:** Monitors drawdown continuously
- **Daily P&L Tracking:** Tracks daily profit/loss
- **Portfolio Correlation:** Calculates position correlation
- **Emergency Shutdown:** Automatically halts trading on breach
- **Trading Halt Checks:** Prevents new trades when halted

**Risk Levels:**
- **NORMAL:** All metrics within safe limits
- **WARNING:** Approaching limits (70% of max)
- **CRITICAL:** Near limits (90% of max) - risk reduction triggered
- **BREACH:** Limits exceeded - emergency shutdown

### Prop Firm Position Limits

**Rule:** Maximum 3 positions (configurable)
**Rule:** Maximum 3% position size (conservative, configurable)
**Rule:** Minimum 82% confidence (high quality signals only)
**Rule:** Maximum 1.5% stop loss (tight risk control)

### Prop Firm Account Switching

**Rule:** Account selection is automatic based on `prop_firm.enabled` flag:
- `prop_firm.enabled = false` → Uses dev or production account (based on environment)
- `prop_firm.enabled = true` → Uses `prop_firm_test` account

**Rule:** No manual account selection needed - system handles switching automatically.

### Dual Service Operation (Optional)

**Rule:** Can run regular trading and prop firm trading simultaneously:
- **Regular Service:** Port 8000, `prop_firm.enabled = false`
- **Prop Firm Service:** Port 8001, `prop_firm.enabled = true`

**Rule:** Each service uses its own account and risk monitoring independently.

**See:** `docs/PROP_FIRM_SETUP_GUIDE.md` for complete setup documentation
**See:** `docs/PROP_FIRM_DEPLOYMENT_GUIDE.md` for dual service deployment

---

## Related Rules

- [16_DEV_PROD_DIFFERENCES.md](16_DEV_PROD_DIFFERENCES.md) - Dev vs Prod differences
- [06_CONFIGURATION.md](06_CONFIGURATION.md) - Configuration management
- [05_ENVIRONMENT.md](05_ENVIRONMENT.md) - Environment management
- [12A_ARGO_BACKEND.md](12A_ARGO_BACKEND.md) - Argo Capital Backend practices
- [07_SECURITY.md](07_SECURITY.md) - Security practices
- [10_MONOREPO.md](10_MONOREPO.md) - Entity separation (prop firm is Argo-only)

