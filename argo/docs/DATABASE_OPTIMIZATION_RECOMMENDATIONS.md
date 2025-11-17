# Database Optimization Recommendations

**Date:** January 2025
**Status:** Recommendations for Production

---

## Overview

This document provides recommendations for optimizing signal storage and database performance as the system scales.

---

## Current Implementation

### Argo Signal Storage (SQLite)

**Location:** `argo/data/signals.db`

**Current Optimizations:**
- ✅ WAL mode enabled for better concurrency
- ✅ Connection pooling
- ✅ Batch inserts (50 signals per batch)
- ✅ Indexes on key columns (signal_id, symbol, created_at, confidence)
- ✅ Optimized SQLite settings (cache_size, temp_store, mmap_size)

**Current Schema:**
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

## Optimization Recommendations

### 1. Table Partitioning by Date

**Problem:** As signal count grows, queries become slower.

**Solution:** Partition signals table by date (monthly or weekly).

**Implementation:**
```sql
-- Create partitioned tables
CREATE TABLE signals_2025_01 (
    -- Same schema as signals
) INHERITS (signals);

-- Or use SQLite's ATTACH for separate databases
ATTACH DATABASE 'signals_2025_01.db' AS signals_jan;
```

**Benefits:**
- Faster queries (smaller tables)
- Easier archiving
- Better index performance

**Priority:** Medium (implement when signal count > 1M)

---

### 2. Archive Old Signals

**Problem:** Database grows indefinitely.

**Solution:** Archive signals older than 1 year to separate archive database.

**Implementation:**
```python
# Archive script
def archive_old_signals(months: int = 12):
    cutoff_date = datetime.now() - timedelta(days=months * 30)
    # Move signals older than cutoff to archive database
```

**Benefits:**
- Keeps main database small
- Preserves historical data
- Faster queries on recent data

**Priority:** High (implement when database > 10GB)

---

### 3. Add Composite Indexes

**Current Indexes:**
- `signal_id` (UNIQUE)
- `symbol`
- `created_at`
- `confidence`

**Recommended Additional Indexes:**
```sql
-- For common query patterns
CREATE INDEX idx_signals_symbol_confidence ON signals(symbol, confidence);
CREATE INDEX idx_signals_created_outcome ON signals(created_at, outcome);
CREATE INDEX idx_signals_confidence_outcome ON signals(confidence, outcome);
```

**Priority:** Medium (implement when query performance degrades)

---

### 4. Optimize Query Patterns

**Common Queries:**
1. Recent signals by symbol
2. Signals by confidence tier
3. Performance by symbol/confidence

**Optimizations:**
- Use covering indexes
- Limit result sets
- Use EXPLAIN QUERY PLAN to analyze

**Priority:** Low (optimize as needed)

---

### 5. Consider PostgreSQL Migration

**Current:** SQLite (good for < 1M signals)

**Future:** PostgreSQL (better for > 1M signals)

**Benefits:**
- Better concurrency
- Advanced indexing (GIN, GiST)
- Partitioning support
- Better query optimizer

**Migration Path:**
1. Keep SQLite for local development
2. Use PostgreSQL for production
3. Sync between databases

**Priority:** Low (consider when SQLite becomes bottleneck)

---

### 6. Add Materialized Views

**For Analytics:**
```sql
-- Daily signal summary
CREATE MATERIALIZED VIEW daily_signal_summary AS
SELECT
    DATE(created_at) as date,
    symbol,
    COUNT(*) as signal_count,
    AVG(confidence) as avg_confidence,
    COUNT(CASE WHEN outcome = 'win' THEN 1 END) as wins,
    COUNT(CASE WHEN outcome = 'loss' THEN 1 END) as losses
FROM signals
GROUP BY DATE(created_at), symbol;
```

**Benefits:**
- Faster analytics queries
- Pre-computed aggregations
- Reduced query load

**Priority:** Low (implement when analytics queries become slow)

---

## Alpine Backend (PostgreSQL)

### Current Implementation

**Location:** PostgreSQL database

**Current Optimizations:**
- ✅ Composite indexes on common query patterns
- ✅ Indexes on confidence, is_active, created_at
- ✅ Immutability triggers

### Recommendations

1. **Partitioning:** Use PostgreSQL table partitioning by date
2. **Archiving:** Archive old signals to separate schema
3. **Connection Pooling:** Ensure proper connection pool sizing
4. **Query Optimization:** Use EXPLAIN ANALYZE for slow queries

---

## Monitoring

### Key Metrics to Monitor

1. **Database Size:**
   - SQLite: `du -h argo/data/signals.db`
   - PostgreSQL: `SELECT pg_size_pretty(pg_database_size('alpine_db'));`

2. **Query Performance:**
   - Monitor slow queries (> 1 second)
   - Track index usage

3. **Signal Count:**
   - Monitor growth rate
   - Plan for archiving

### Monitoring Script

```python
# scripts/monitor_database.py
def check_database_health():
    # Check size
    # Check query performance
    # Check index usage
    # Alert if issues
```

---

## Implementation Priority

1. **High Priority:**
   - Archive old signals (when database > 10GB)
   - Monitor database size and query performance

2. **Medium Priority:**
   - Add composite indexes (when queries slow)
   - Implement table partitioning (when signal count > 1M)

3. **Low Priority:**
   - Consider PostgreSQL migration (when SQLite becomes bottleneck)
   - Add materialized views (when analytics queries slow)

---

## Conclusion

Current database implementation is well-optimized for current scale. As the system grows, implement optimizations based on actual performance metrics and growth patterns.

**Next Steps:**
1. Set up database monitoring
2. Track database size and query performance
3. Implement optimizations as needed based on metrics
