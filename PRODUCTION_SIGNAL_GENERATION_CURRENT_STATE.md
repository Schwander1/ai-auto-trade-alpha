# Production Signal Generation - Current State

**Last Updated:** November 19, 2025  
**Architecture:** Unified Architecture v3.0  
**Status:** ✅ **OPERATIONAL**

---

## Architecture Overview

The production system uses a **Unified Architecture (v3.0)**:

```
┌─────────────────────────────────────────────┐
│   Unified Signal Generator (Port 7999)     │
│   ✅ Generates ALL signals                  │
│   ✅ Stores in unified database             │
│   ✅ Distributes to executors               │
└──────────────┬──────────────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
┌─────▼──────┐  ┌───────▼──────────┐
│ Argo       │  │ Prop Firm        │
│ Executor   │  │ Executor         │
│ (Port 8000)│  │ (Port 8001)      │
│ ✅ Executes│  │ ✅ Executes      │
│   trades   │  │   trades         │
└────────────┘  └──────────────────┘
      │                 │
      └────────┬────────┘
               │
      ┌────────▼────────┐
      │ Unified Database│
      │ signals_unified │
      │     .db         │
      └─────────────────┘
```

### Key Points

- **ONE** service generates signals: Unified Signal Generator (port 7999)
- **TWO** services execute trades: Argo Executor (8000), Prop Firm Executor (8001)
- **Executors DO NOT generate signals** - they only execute trades
- All signals stored in unified database: `/root/argo-production-unified/data/signals_unified.db`

---

## Current Status

### ✅ Unified Signal Generator (Port 7999)

**Service:** `argo-signal-generator.service`  
**Status:** ✅ ACTIVE and generating signals  
**Latest Signal:** Generated within last few minutes  
**Generation Rate:** ~990 signals/hour (~16.5 signals/minute)  
**Database:** `/root/argo-production-unified/data/signals_unified.db`

**Configuration:**
- `auto_execute: true`
- `force_24_7_mode: true`
- Generates signals every 5 seconds
- Distributes to both executors

### ✅ Argo Trading Executor (Port 8000)

**Service:** `argo-trading-executor.service`  
**Status:** ✅ ACTIVE (may have restart issues - monitor)  
**Role:** Executes trades for Argo account  
**Receives signals from:** Unified Signal Generator via Signal Distributor

**Configuration:**
- `auto_execute: true`
- `force_24_7_mode: true`
- Min confidence: 75.0%
- Position size: 9%

### ✅ Prop Firm Executor (Port 8001)

**Service:** `argo-prop-firm-executor.service`  
**Status:** ✅ ACTIVE  
**Role:** Executes trades for Prop Firm account  
**Receives signals from:** Unified Signal Generator via Signal Distributor

**Configuration:**
- `auto_execute: true`
- `force_24_7_mode: true`
- Min confidence: 82.0%
- Position size: 3%
- Max drawdown: 2.0%

---

## Auto-Trading Configuration

### Both Executors Configured for Auto-Trading ✅

**Market Hours Behavior:**
- **Stocks (AAPL, TSLA, NVDA, MSFT):**
  - Signals generated 24/7
  - Trades execute only during market hours (9:30 AM - 4:00 PM ET, Mon-Fri)
  
- **Crypto (BTC-USD, ETH-USD):**
  - Signals generated 24/7
  - Trades execute 24/7 (crypto markets never close)

**Signal Distribution:**
- Unified Generator distributes signals to both executors
- Each executor validates and executes independently
- Executors apply their own risk rules and confidence thresholds

---

## Monitoring Commands

### Check Signal Generation
```bash
# Check unified signal generator status
ssh root@178.156.194.174 "systemctl status argo-signal-generator.service"

# Check recent signals
ssh root@178.156.194.174 "sqlite3 /root/argo-production-unified/data/signals_unified.db \"SELECT COUNT(*) FROM signals WHERE timestamp >= datetime('now', '-1 hour');\""

# Monitor signal generation logs
ssh root@178.156.194.174 "journalctl -u argo-signal-generator.service -f"
```

### Check Executors
```bash
# Check executor status
ssh root@178.156.194.174 "systemctl status argo-trading-executor.service argo-prop-firm-executor.service"

# Check health endpoints
curl http://localhost:8000/health  # Argo Executor
curl http://localhost:8001/health  # Prop Firm Executor
curl http://localhost:7999/health  # Unified Signal Generator
```

### Check Signal Distribution
```bash
# Check recent signal distribution logs
ssh root@178.156.194.174 "journalctl -u argo-signal-generator.service --since '10 minutes ago' | grep -i 'distribut\|executor'"
```

---

## Important Notes

### ⚠️ Common Misconceptions

1. **Ports 8000/8001 do NOT generate signals**
   - These are executors that only execute trades
   - Signal generation happens on port 7999

2. **Old database paths are deprecated**
   - `/root/argo-production-green/data/signals.db` - OLD (may not exist)
   - `/root/argo-production-prop-firm/data/signals.db` - OLD (may not exist)
   - `/root/argo-production-unified/data/signals_unified.db` - CURRENT

3. **Old service names are deprecated**
   - `argo-trading.service` - OLD (may still exist but is executor)
   - `argo-trading-prop-firm.service` - OLD (may still exist but is executor)
   - `argo-signal-generator.service` - CURRENT (generates signals)
   - `argo-trading-executor.service` - CURRENT (executes trades)
   - `argo-prop-firm-executor.service` - CURRENT (executes trades)

---

## Related Documentation

- `PRODUCTION_SIGNAL_GENERATION_ACTUAL_STATE.md` - Detailed current state analysis
- `docs/UNIFIED_ARCHITECTURE_COMPLETE_GUIDE.md` - Complete architecture guide
- `Rules/13_TRADING_OPERATIONS.md` - Trading operations rules (v3.0)
- `production_deployment/UNIFIED_ARCHITECTURE_DEPLOYMENT.md` - Deployment guide

---

## Quick Status Check

Run the updated diagnostic script:
```bash
python3 check_production_signal_generation.py
```

This script now correctly checks:
1. Unified Signal Generator (port 7999) for signal generation
2. Executors (ports 8000, 8001) for trade execution
3. Unified database for signal storage

