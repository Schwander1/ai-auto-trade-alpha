# Signal Storage Locations

**Date:** November 18, 2025

---

## Signal Storage Overview

Signals are stored in **three locations**:

1. **Primary: SQLite Database** (Argo local storage)
2. **Secondary: Alpine Backend** (PostgreSQL - production database)
3. **Tertiary: File Log** (Text log for audit trail)

---

## 1. Primary Storage: SQLite Database

### Location

**Development/Local:**
- Path: `argo/data/signals.db`
- Full path: `/path/to/argo-alpine-workspace/argo/data/signals.db`

**Production:**
- Path: `/root/argo-production-prop-firm/data/signals.db`
- Created automatically on first signal storage

### Database Details

- **Type:** SQLite 3
- **Mode:** WAL (Write-Ahead Logging) for better concurrency
- **Connection Pooling:** Max 5 connections
- **Batch Inserts:** 50 signals per batch
- **Batch Timeout:** 5 seconds

### Schema

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

### Storage Process

1. **Signal Generated** → Queued in `_pending_signals` list
2. **Batch Reached** → 50 signals OR 5 seconds timeout
3. **Batch Insert** → Async non-blocking database write
4. **SHA-256 Hash** → Generated for data integrity

### Access

**Via Code:**
```python
from argo.core.signal_tracker import SignalTracker

tracker = SignalTracker()
signal_id = await tracker.log_signal_async(signal)
```

**Via SQL:**
```bash
sqlite3 /root/argo-production-prop-firm/data/signals.db
SELECT * FROM signals ORDER BY timestamp DESC LIMIT 10;
```

---

## 2. Secondary Storage: Alpine Backend (PostgreSQL)

### Location

- **Server:** 91.98.153.49:8001
- **Database:** PostgreSQL (production)
- **Table:** `signals`
- **Endpoint:** `POST /api/v1/external-signals/sync/signal`

### Sync Process

1. **Signal Stored Locally** → SQLite database
2. **Async Sync** → `AlpineSyncService` sends to Alpine backend
3. **HTTP POST** → Signal data with SHA-256 hash
4. **Verification** → Alpine backend verifies hash
5. **Storage** → Stored in PostgreSQL `signals` table

### Sync Details

- **Method:** Async, non-blocking
- **Retry Logic:** Up to 3 retries with exponential backoff
- **Authentication:** X-API-Key header
- **Hash Verification:** SHA-256 verification on Alpine side

### Access

**Via API:**
```bash
curl http://91.98.153.49:8001/api/v1/signals
```

**Via Database:**
```sql
SELECT * FROM signals ORDER BY created_at DESC LIMIT 10;
```

---

## 3. Tertiary Storage: File Log

### Location

**Development/Local:**
- Path: `argo/logs/signals.log`

**Production:**
- Path: `/root/argo-production-prop-firm/logs/signals.log`
- Created automatically on first signal storage

### Log Format

- **Format:** JSON Lines (one signal per line)
- **Purpose:** Audit trail, debugging, backup
- **Rotation:** Not currently implemented (manual cleanup needed)

### Example Entry

```json
{"signal_id": "abc123...", "symbol": "AAPL", "action": "BUY", "entry_price": 150.50, "confidence": 85.5, "timestamp": "2025-11-18T02:00:00Z", "sha256": "..."}
```

---

## Storage Flow

```
Signal Generated
    ↓
1. Store in SQLite (async batch insert)
    ├─→ signals.db (primary storage)
    └─→ signals.log (audit trail)
    ↓
2. Sync to Alpine Backend (async)
    └─→ PostgreSQL signals table (production database)
    ↓
3. Track in Lifecycle Tracker
    └─→ In-memory tracking for active signals
```

---

## Production Locations

### Prop Firm Service

**SQLite Database:**
- `/root/argo-production-prop-firm/data/signals.db`
- Created on first signal storage

**Log File:**
- `/root/argo-production-prop-firm/logs/signals.log`
- Created on first signal storage

**Alpine Backend:**
- PostgreSQL database on `91.98.153.49:8001`
- Table: `signals`

### Regular Trading Service

**SQLite Database:**
- `/root/argo-production-green/data/signals.db`

**Log File:**
- `/root/argo-production-green/logs/signals.log`

---

## Querying Signals

### Check Signal Count

```bash
# Production prop firm
ssh root@178.156.194.174 'cd /root/argo-production-prop-firm && sqlite3 data/signals.db "SELECT COUNT(*) FROM signals;"'
```

### View Recent Signals

```bash
# Production prop firm
ssh root@178.156.194.174 'cd /root/argo-production-prop-firm && sqlite3 data/signals.db "SELECT signal_id, symbol, action, confidence, timestamp FROM signals ORDER BY timestamp DESC LIMIT 10;"'
```

### Check Database Size

```bash
ssh root@178.156.194.174 'ls -lh /root/argo-production-prop-firm/data/signals.db'
```

---

## Performance Optimizations

1. **Batch Inserts:** 50 signals per batch (reduces DB writes)
2. **Async Operations:** Non-blocking storage and sync
3. **Connection Pooling:** Max 5 SQLite connections
4. **WAL Mode:** Better concurrency for SQLite
5. **Indexes:** On signal_id, symbol, timestamp, confidence
6. **Query Caching:** 30-second cache for frequent queries

---

## Backup & Recovery

### Database Backup

```bash
# Backup SQLite database
cp /root/argo-production-prop-firm/data/signals.db /root/backups/signals_$(date +%Y%m%d).db
```

### Log Backup

```bash
# Backup log file
cp /root/argo-production-prop-firm/logs/signals.log /root/backups/signals_$(date +%Y%m%d).log
```

### Recovery

- **SQLite:** Restore from backup file
- **Alpine Backend:** Signals are in PostgreSQL (separate backup)
- **Log File:** Text file, can be restored from backup

---

## Monitoring

### Check Storage Status

```bash
# Check if database exists
ls -lh /root/argo-production-prop-firm/data/signals.db

# Check signal count
sqlite3 /root/argo-production-prop-firm/data/signals.db "SELECT COUNT(*) FROM signals;"

# Check latest signal
sqlite3 /root/argo-production-prop-firm/data/signals.db "SELECT MAX(timestamp) FROM signals;"
```

### Check Sync Status

- Review Alpine sync logs
- Check Alpine backend for received signals
- Verify signal count matches between Argo and Alpine

---

## Summary

| Storage Type | Location | Purpose | Access |
|--------------|----------|---------|--------|
| **SQLite DB** | `/root/argo-production-prop-firm/data/signals.db` | Primary storage | `SignalTracker` class |
| **PostgreSQL** | `91.98.153.49:8001` (Alpine backend) | Production database | HTTP API or direct DB |
| **Log File** | `/root/argo-production-prop-firm/logs/signals.log` | Audit trail | Text file |

---

**Status:** ✅ **SIGNAL STORAGE LOCATIONS DOCUMENTED**

