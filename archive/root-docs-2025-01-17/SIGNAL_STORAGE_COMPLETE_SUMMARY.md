# Signal Storage - Complete Summary

**Date:** November 18, 2025

---

## Signal Storage Locations

### 1. **Primary: SQLite Database**

**Actual Location (Production Prop Firm):**
- **Path:** `/root/argo-production/data/signals.db`
- **Status:** ✅ Exists and contains signals
- **Note:** Path resolves to parent directory due to BASE_DIR calculation

**Expected Location:**
- `/root/argo-production-prop-firm/data/signals.db`
- **Status:** ⚠️ Not created (using parent directory instead)

**Why:** The `BASE_DIR` in `SignalTracker` resolves to `/root/argo-production/` instead of `/root/argo-production-prop-firm/` because it goes up 4 parent directories from the signal_tracker.py file location.

### 2. **Secondary: Alpine Backend (PostgreSQL)**

**Location:**
- **Server:** `91.98.153.49:8001`
- **Database:** PostgreSQL
- **Table:** `signals`
- **Endpoint:** `POST /api/v1/external-signals/sync/signal`

**Sync Service:**
- **Class:** `AlpineSyncService` (`argo/argo/core/alpine_sync.py`)
- **Method:** Async HTTP POST with retry logic
- **Status:** ✅ Implemented and integrated

### 3. **Tertiary: File Log**

**Location:**
- **Path:** `/root/argo-production/logs/signals.log`
- **Format:** JSON Lines
- **Purpose:** Audit trail

---

## Storage Flow

```
Signal Generated (every 5 seconds)
    ↓
1. Store in SQLite (async batch insert)
    ├─→ /root/argo-production/data/signals.db ✅
    └─→ /root/argo-production/logs/signals.log ✅
    ↓
2. Sync to Alpine Backend (async)
    └─→ PostgreSQL on 91.98.153.49:8001 ✅
    ↓
3. Track in Lifecycle Tracker
    └─→ In-memory tracking ✅
```

---

## Database Schema

```sql
CREATE TABLE signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id TEXT UNIQUE NOT NULL,
    symbol TEXT NOT NULL,
    action TEXT NOT NULL,
    entry_price REAL NOT NULL,
    target_price REAL NOT NULL,
    stop_price REAL NOT NULL,
    confidence REAL NOT NULL,
    strategy TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    data_source TEXT DEFAULT 'weighted_consensus',
    timestamp TEXT NOT NULL,
    outcome TEXT DEFAULT NULL,
    exit_price REAL DEFAULT NULL,
    profit_loss_pct REAL DEFAULT NULL,
    sha256 TEXT NOT NULL,
    order_id TEXT DEFAULT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

---

## Query Commands

### Check Signal Count
```bash
ssh root@178.156.194.174 'sqlite3 /root/argo-production/data/signals.db "SELECT COUNT(*) FROM signals;"'
```

### View Recent Signals
```bash
ssh root@178.156.194.174 'sqlite3 /root/argo-production/data/signals.db "SELECT signal_id, symbol, action, confidence, timestamp FROM signals ORDER BY timestamp DESC LIMIT 10;"'
```

### Check Database Size
```bash
ssh root@178.156.194.174 'ls -lh /root/argo-production/data/signals.db'
```

### Check Latest Signal
```bash
ssh root@178.156.194.174 'sqlite3 /root/argo-production/data/signals.db "SELECT MAX(timestamp) FROM signals;"'
```

---

## Storage Features

### Optimizations
- ✅ **Batch Inserts:** 50 signals per batch
- ✅ **Async Storage:** Non-blocking writes
- ✅ **Connection Pooling:** Max 5 connections
- ✅ **WAL Mode:** Better concurrency
- ✅ **Indexes:** On signal_id, symbol, timestamp, confidence
- ✅ **SHA-256 Verification:** Data integrity

### Sync Features
- ✅ **Async Sync:** Non-blocking Alpine backend sync
- ✅ **Retry Logic:** 3 retries with exponential backoff
- ✅ **Health Checks:** Alpine backend connectivity checks
- ✅ **Error Handling:** Graceful degradation

---

## Status Summary

| Storage Type | Location | Status | Notes |
|--------------|----------|--------|-------|
| **SQLite DB** | `/root/argo-production/data/signals.db` | ✅ Active | Shared with regular service |
| **PostgreSQL** | `91.98.153.49:8001` | ✅ Active | Alpine backend |
| **Log File** | `/root/argo-production/logs/signals.log` | ✅ Active | Audit trail |

---

## Important Notes

1. **Path Resolution:** The database is stored in `/root/argo-production/` instead of `/root/argo-production-prop-firm/` due to BASE_DIR calculation. This means both services (regular and prop firm) may share the same database.

2. **Signal Isolation:** If you need separate databases for prop firm vs regular trading, you'll need to configure different database paths.

3. **Alpine Sync:** Signals are automatically synced to Alpine backend PostgreSQL database for centralized storage and access.

---

**Status:** ✅ **SIGNAL STORAGE OPERATIONAL**

