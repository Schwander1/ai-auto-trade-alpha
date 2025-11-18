# 🔍 Comprehensive Investigation: Buying and Selling in Production

**Date:** 2025-01-15  
**Status:** ✅ Complete Investigation  
**Purpose:** Comprehensive analysis of buying and selling functionality in production

---

## Executive Summary

This document provides a comprehensive investigation of the buying and selling mechanisms in production, including:
- How buying works (BUY/LONG orders)
- How selling works (SELL/SHORT orders)
- Production configuration and setup
- Recent issues and fixes
- Monitoring and logging capabilities
- How to check current trading activity

---

## 1. Trading Architecture Overview

### Core Components

1. **SignalGenerationService** (`argo/argo/core/signal_generation_service.py`)
   - Generates trading signals every 5 seconds
   - Uses Weighted Consensus v6.0 algorithm
   - Multi-source aggregation (6 data sources)
   - Validates trades before execution

2. **PaperTradingEngine** (`argo/argo/core/paper_trading_engine.py`)
   - Executes trades through Alpaca API
   - Handles position sizing, order placement, and bracket orders
   - Manages account and position caching
   - Supports both stocks and crypto

3. **UnifiedPerformanceTracker** (`argo/argo/tracking/unified_tracker.py`)
   - Tracks all trades and performance metrics
   - Records entry/exit prices, P&L, win rates
   - Syncs to Tradervue for external tracking

---

## 2. How Buying Works (BUY/LONG Orders)

### 2.1 Signal Generation → Trade Execution Flow

```
Signal Generated (BUY action)
    ↓
_validate_trade() - Risk checks
    ├─ Check buying power
    ├─ Check position limits
    ├─ Check correlation groups
    └─ Check prop firm limits (if enabled)
    ↓
Check existing position
    ├─ If SHORT exists → Close SHORT (BUY to close)
    ├─ If LONG exists → Skip (duplicate)
    └─ If no position → Open new LONG
    ↓
_calculate_position_size()
    ├─ Get buying power from account
    ├─ Calculate position size % (10-15% default, 3% prop firm)
    ├─ Adjust for confidence (75%+ scales up)
    ├─ Adjust for volatility (ATR-based)
    └─ Calculate quantity (shares for stocks, fractional for crypto)
    ↓
_prepare_buy_order_details()
    ├─ Determine if closing SHORT or opening LONG
    ├─ Set order side (BUY)
    ├─ Set quantity
    └─ Set bracket orders (stop loss, take profit)
    ↓
_execute_live()
    ├─ Convert symbol format (crypto: BTC-USD → BTCUSD)
    ├─ Check connection health
    ├─ Validate minimum order size
    ├─ Submit main order (Market or Limit)
    └─ Place bracket orders (stop loss, take profit)
    ↓
Track & Log
    ├─ Record in performance tracker
    ├─ Journal trade
    ├─ Sync to Tradervue
    └─ Invalidate caches
```

### 2.2 Position Sizing Logic

**Standard Trading Mode:**
- Base position size: 10% of buying power
- Max position size: 15% of buying power
- Confidence scaling: 75%+ confidence increases position size
- Volatility adjustment: Lower volatility = larger position

**Prop Firm Mode:**
- Fixed position size: 3% of buying power
- Min confidence: 82% (rejects lower confidence signals)
- Max stop loss: 1.5%
- Max positions: 3 concurrent positions

**Crypto-Specific:**
- Fractional quantities allowed (minimum 0.000001)
- For expensive crypto (>$10,000), uses minimum 0.5% of buying power
- Symbol conversion: BTC-USD → BTCUSD for Alpaca API

**Stock-Specific:**
- Whole shares only (minimum 1 share)
- Standard position sizing applies

### 2.3 Order Types

**Market Orders (Default):**
- Executes immediately at current market price
- Used for most trades
- Configurable via `use_limit_orders: false`

**Limit Orders (Optional):**
- Executes at specified price or better
- Offset: 0.1% above entry price (configurable)
- Used when `use_limit_orders: true` in config

### 2.4 Bracket Orders (Risk Management)

**Stop Loss Order:**
- Automatically placed after main order fills
- Protects against large losses
- Configurable per signal or via default risk limits

**Take Profit Order:**
- Automatically placed after main order fills
- Locks in profits at target price
- Configurable per signal

**Bracket Order Placement:**
- Retry logic: 2 attempts with 0.5s delay
- Partial failures logged but don't cancel main order
- Main order can execute even if brackets fail

---

## 3. How Selling Works (SELL/SHORT Orders)

### 3.1 SELL Signal Flow

```
Signal Generated (SELL action)
    ↓
_validate_trade() - Risk checks
    ↓
Check existing position
    ├─ If LONG exists → Close LONG (SELL to close)
    ├─ If SHORT exists → Skip (duplicate)
    └─ If no position → Open new SHORT
    ↓
_prepare_sell_order_details()
    ├─ If closing LONG: Use existing position qty, side=SELL
    ├─ If opening SHORT: Calculate position size, side=SELL
    └─ Set bracket orders (stop loss above entry, target below)
    ↓
_execute_live()
    ├─ Submit order
    └─ Place bracket orders
    ↓
Track & Log
```

### 3.2 Closing Positions

**Closing LONG Position:**
- Signal: SELL
- Order side: SELL
- Quantity: Existing position quantity
- No bracket orders (position is closing)

**Closing SHORT Position:**
- Signal: BUY
- Order side: BUY (to close SHORT)
- Quantity: Existing position quantity
- No bracket orders (position is closing)

### 3.3 Opening SHORT Positions

**New SHORT Position:**
- Signal: SELL
- Order side: SELL
- Quantity: Calculated position size
- Bracket orders: Stop loss above entry, take profit below entry

---

## 4. Production Configuration

### 4.1 Production Server Details

**Argo Service:**
- **Server:** 178.156.194.174
- **Port:** 8000
- **Active Environment:** blue (blue/green deployment)
- **Service:** `argo-trading.service`
- **Log File:** `/tmp/argo-blue.log`

**Prop Firm Service:**
- **Server:** 178.156.194.174
- **Port:** 8001
- **Config Path:** `/root/argo-production-prop-firm/config.json`
- **Service:** `argo-trading-prop-firm.service`

### 4.2 Account Configuration

**Regular Production:**
- Account: Production paper trading account
- Environment: `production`
- Auto-execute: Always enabled
- 24/7 mode: Enabled

**Prop Firm:**
- Account: `prop_firm_test` account
- Environment: `production`
- Prop firm mode: Enabled
- Stricter risk limits applied

### 4.3 Trading Configuration

**Key Settings:**
```json
{
  "trading": {
    "position_size_pct": 10,
    "max_position_size_pct": 15,
    "use_limit_orders": false,
    "limit_order_offset_pct": 0.001,
    "auto_execute": true,
    "max_retry_attempts": 3,
    "retry_delay_seconds": 1
  },
  "prop_firm": {
    "enabled": false,
    "account": "prop_firm_test",
    "risk_limits": {
      "max_drawdown_pct": 2.0,
      "daily_loss_limit_pct": 4.5,
      "max_position_size_pct": 3.0,
      "min_confidence": 82.0,
      "max_positions": 3,
      "max_stop_loss_pct": 1.5
    }
  }
}
```

---

## 5. Recent Issues and Fixes

### 5.1 Fixed Issues

#### ✅ ETH-USD Trading Execution (Fixed)
**Problem:** ETH-USD orders failing with `422: asset "ETH-USD" not found`

**Solution:**
- Added `_convert_symbol_for_alpaca()` method
- ETH-USD → ETHUSD (Alpaca format)
- BTC-USD → BTCUSD (Alpaca format)
- Stocks remain unchanged

**Status:** ✅ Fixed in `paper_trading_engine.py`

#### ✅ BTC-USD Position Sizing (Fixed)
**Problem:** BTC-USD orders failing with "Calculated qty is 0"

**Solution:**
- Enhanced position sizing for crypto
- Crypto uses fractional quantities (0.000001 minimum)
- Added minimum position size for expensive crypto (0.5% of buying power)
- Improved validation for fractional vs whole shares

**Status:** ✅ Fixed in `paper_trading_engine.py`

#### ✅ API Key Error Handling (Fixed)
**Problem:** Invalid API keys causing repeated failed calls

**Solution:**
- Enhanced error detection for xAI Grok (400, 401, 403 errors)
- Enhanced error detection for Massive API (401 errors)
- Auto-disable data sources when invalid API keys detected
- Clear error messages with actionable steps

**Status:** ✅ Fixed in data source modules

### 5.2 Current Issues

#### ⚠️ API Key Problems
- **xAI Grok API:** Invalid API key (needs update)
- **Massive API:** Invalid API key (needs update)
- **Impact:** Degraded signal quality (still functional with other sources)

#### ⚠️ Alpine Backend Service
- **Status:** DOWN
- **Server:** 91.98.153.49:8001
- **Impact:** Signal sync to Alpine backend not working

---

## 6. Monitoring and Logging

### 6.1 Log Locations

**Production Logs:**
- **Argo Service:** `/tmp/argo-blue.log` (or `/tmp/argo-green.log`)
- **Prop Firm Service:** `/root/argo-production-prop-firm/logs/*.log`
- **Signal Logs:** `/root/argo-production-prop-firm/logs/signals.log`

### 6.2 Key Log Patterns

**Buy Orders:**
```bash
grep -E "BUY|Order placed|MARKET.*buy" /tmp/argo-blue.log
```

**Sell Orders:**
```bash
grep -E "SELL|Order placed|MARKET.*sell" /tmp/argo-blue.log
```

**Crypto Trading:**
```bash
grep -E "ETH-USD|BTC-USD|Converted symbol" /tmp/argo-blue.log
```

**Order Execution:**
```bash
grep -E "Order.*placed|Order ID|filled" /tmp/argo-blue.log
```

**Errors:**
```bash
grep -E "ERROR|Exception|Invalid|Unauthorized" /tmp/argo-blue.log
```

### 6.3 Monitoring Scripts

**Production Trading Monitor:**
```bash
./scripts/monitor_production_trading.sh [duration_seconds]
```

**View Logs:**
```bash
./commands/lib/view-logs-production.sh [follow|view] [argo|alpine|all]
```

**Health Check:**
```bash
./commands/lib/health-check-production.sh
```

### 6.4 Performance Tracking

**Database Storage:**
- **Primary:** SQLite (`/root/argo-production-prop-firm/data/signals.db`)
- **Secondary:** PostgreSQL (Alpine backend - currently down)
- **Tertiary:** File logs (`signals.log`)

**Performance Metrics:**
- Win rate, ROI, profit factor
- Average win/loss
- Total P&L
- Trade count by asset class

**Access Performance Data:**
```python
from argo.tracking.unified_tracker import UnifiedPerformanceTracker

tracker = UnifiedPerformanceTracker()
stats = tracker.get_performance_stats(days=30)
recent_trades = tracker.get_recent_trades(limit=100)
```

---

## 7. How to Check Current Trading Activity

### 7.1 Check Current Positions

**Via API:**
```bash
# Get account status (includes positions)
curl http://178.156.194.174:8000/api/v1/trading/status
```

**Via Python Script:**
```python
from argo.core.paper_trading_engine import PaperTradingEngine

engine = PaperTradingEngine()
positions = engine.get_positions()

for pos in positions:
    print(f"{pos['symbol']}: {pos['side']} {pos['qty']} @ ${pos['entry_price']:.2f}")
    print(f"  Current: ${pos['current_price']:.2f}, P&L: {pos['pnl_pct']:.2f}%")
```

**Via Direct Script:**
```bash
python3 argo/argo/core/paper_trading_engine.py
```

### 7.2 Check Recent Orders

**Via API:**
```bash
# Get latest signals (includes executed trades)
curl http://178.156.194.174:8000/api/signals/latest?limit=10
```

**Via Python:**
```python
from argo.core.paper_trading_engine import PaperTradingEngine

engine = PaperTradingEngine()
orders = engine.get_all_orders(status="all", limit=50)

for order in orders:
    print(f"Order {order['id']}: {order['side']} {order['qty']} {order['symbol']}")
    print(f"  Status: {order['status']}, Filled: {order['filled_qty']}")
```

### 7.3 Check Account Status

**Via API:**
```bash
curl http://178.156.194.174:8000/api/v1/trading/status
```

**Response includes:**
- Portfolio value
- Buying power
- Cash balance
- Account status
- Current positions count

### 7.4 Check Signal Generation

**Via API:**
```bash
# Latest signals
curl http://178.156.194.174:8000/api/signals/latest?limit=5

# Signal stats
curl http://178.156.194.174:8000/api/signals/stats
```

### 7.5 Check Performance Metrics

**Via Python Script:**
```bash
python3 argo/scripts/evaluate_performance.py
```

**Or Enhanced Version:**
```bash
python3 argo/scripts/evaluate_performance_enhanced.py
```

---

## 8. Trade Execution Details

### 8.1 Order Validation

**Pre-Execution Checks:**
1. **Risk Validation:**
   - Buying power check
   - Position size limits
   - Correlation group limits
   - Prop firm limits (if enabled)

2. **Position Check:**
   - Existing position detection
   - Duplicate prevention
   - Position flipping logic

3. **Market Hours:**
   - Stocks: Market hours only
   - Crypto: 24/7 trading

4. **Connection Health:**
   - Alpaca API connectivity
   - Account status check

### 8.2 Order Submission

**Main Order:**
- Market or Limit order
- Quantity calculated from position sizing
- Symbol converted for Alpaca API (crypto only)
- Time in force: DAY (market hours) or GTC (crypto)

**Bracket Orders:**
- Stop loss: Placed after main order
- Take profit: Placed after main order
- Retry logic: 2 attempts with 0.5s delay
- Partial failures logged but don't block main order

### 8.3 Order Tracking

**Internal Tracker:**
- Order ID, symbol, side, quantity
- Entry price, stop price, target price
- Signal metadata
- Timestamp

**Performance Tracker:**
- Trade entry/exit recording
- P&L calculation
- Win/loss tracking
- Regime classification

**Tradervue Sync:**
- Automatic sync on trade entry
- Automatic sync on trade exit
- Full trade lifecycle tracking

---

## 9. Error Handling and Recovery

### 9.1 Retry Logic

**Order Submission:**
- Max retries: 3 (configurable)
- Exponential backoff: 1s, 2s, 3s
- Rate limit handling: Longer backoff (2^retry_count, max 30s)

**Bracket Orders:**
- Max retries: 2
- Delay: 0.5s between attempts
- Partial success handling

### 9.2 Error Types

**Connection Errors:**
- Invalidates caches
- Retries with backoff
- Logs error details

**Insufficient Buying Power:**
- Invalidates account cache
- Logs warning
- Skips trade

**Asset Not Found:**
- Logs error with symbol
- No retry (configuration issue)
- Suggests symbol format check

**Rate Limits:**
- Exponential backoff
- Longer delays for rate limits
- Continues retrying up to max attempts

### 9.3 Cache Management

**Account Cache:**
- TTL: 30 seconds
- Invalidated after trades
- Invalidated on errors

**Positions Cache:**
- TTL: 10 seconds
- Invalidated after trades
- Invalidated on errors

**Volatility Cache:**
- TTL: 1 hour
- Per-symbol caching
- Automatic cleanup (keeps last 100 symbols)

---

## 10. Production Monitoring Checklist

### Daily Checks

- [ ] Service status (systemctl status argo-trading.service)
- [ ] Health endpoint (curl http://178.156.194.174:8000/health)
- [ ] Latest signals (curl http://178.156.194.174:8000/api/signals/latest)
- [ ] Recent errors (grep ERROR /tmp/argo-blue.log | tail -20)
- [ ] Account status (check buying power, portfolio value)
- [ ] Current positions (engine.get_positions())

### Weekly Checks

- [ ] Performance metrics (evaluate_performance.py)
- [ ] API key status (check for invalid key errors)
- [ ] Trade execution success rate
- [ ] Position sizing accuracy
- [ ] Bracket order success rate

### Monthly Checks

- [ ] Overall win rate and ROI
- [ ] Trade distribution by asset class
- [ ] Error rate trends
- [ ] System stability (restarts, crashes)
- [ ] Database size and cleanup needs

---

## 11. Troubleshooting Guide

### Issue: Orders Not Executing

**Check:**
1. Service status: `systemctl status argo-trading.service`
2. Health endpoint: `curl http://178.156.194.174:8000/health`
3. Account status: Check buying power
4. Market hours: Stocks only trade during market hours
5. Logs: `tail -f /tmp/argo-blue.log | grep -E "Order|ERROR"`

### Issue: Zero Quantity Errors

**Check:**
1. Buying power: `engine.get_account_details()['buying_power']`
2. Entry price: Signal entry price
3. Position size calculation: Check logs for position sizing details
4. Crypto minimum: 0.000001 for crypto, 1 for stocks

### Issue: Asset Not Found Errors

**Check:**
1. Symbol format: Crypto should be BTC-USD (converted to BTCUSD)
2. Asset availability: Check if asset is tradeable on Alpaca
3. Account permissions: Check if account can trade the asset

### Issue: Bracket Orders Failing

**Check:**
1. Main order status: Verify main order filled
2. Stop/target prices: Validate prices are reasonable
3. Retry logs: Check for retry attempts
4. Partial success: Check if one bracket order succeeded

---

## 12. API Endpoints Reference

### Trading Endpoints

**Get Trading Status:**
```bash
GET /api/v1/trading/status
```

**Execute Trade (Manual):**
```bash
POST /api/v1/trading/execute
Content-Type: application/json
{
  "symbol": "AAPL",
  "action": "BUY",
  "confidence": 85,
  "entry_price": 150.00
}
```

### Signal Endpoints

**Get Latest Signals:**
```bash
GET /api/signals/latest?limit=10
```

**Get Signal Stats:**
```bash
GET /api/signals/stats
```

### Health Endpoints

**Health Check:**
```bash
GET /health
GET /api/v1/health/
GET /api/v1/health/readiness
GET /api/v1/health/liveness
```

---

## 13. Key Files Reference

### Core Trading Files

- `argo/argo/core/paper_trading_engine.py` - Main trading engine
- `argo/argo/core/signal_generation_service.py` - Signal generation and execution
- `argo/argo/tracking/unified_tracker.py` - Performance tracking

### Configuration Files

- `/root/argo-production-blue/config.json` - Regular production config
- `/root/argo-production-prop-firm/config.json` - Prop firm config

### Monitoring Scripts

- `scripts/monitor_production_trading.sh` - Production trading monitor
- `commands/lib/view-logs-production.sh` - View production logs
- `argo/scripts/evaluate_performance.py` - Performance evaluation

---

## 14. Summary

### Buying (BUY/LONG)
- ✅ Signal generation → validation → position sizing → order execution
- ✅ Supports both opening new LONG and closing SHORT positions
- ✅ Dynamic position sizing based on confidence and volatility
- ✅ Automatic bracket orders (stop loss, take profit)
- ✅ Crypto symbol conversion (BTC-USD → BTCUSD)
- ✅ Fractional quantities for crypto

### Selling (SELL/SHORT)
- ✅ Signal generation → validation → order execution
- ✅ Supports both closing LONG and opening SHORT positions
- ✅ Position-aware order preparation
- ✅ Automatic bracket orders for new SHORT positions
- ✅ No bracket orders when closing positions

### Production Status
- ✅ Service running and operational
- ✅ Signal generation active (every 5 seconds)
- ✅ Auto-execute enabled
- ⚠️ Some API keys need updating (xAI Grok, Massive)
- ⚠️ Alpine backend service down (signal sync affected)

### Monitoring
- ✅ Comprehensive logging in `/tmp/argo-blue.log`
- ✅ Performance tracking in database
- ✅ API endpoints for status checks
- ✅ Monitoring scripts available

---

**Investigation Complete:** 2025-01-15  
**Next Steps:** Monitor trading activity, update API keys, investigate Alpine backend downtime

