#!/usr/bin/env python3
"""
TRADE SECRET - PROPRIETARY ALGORITHM
Argo Capital - Confidential

Enterprise Signal Tracker v4.1
Immutable Audit Trail System with SHA-256 Verification

This code contains proprietary algorithms and trade secrets.
Unauthorized disclosure, copying, or use is strictly prohibited.

PATENT-PENDING TECHNOLOGY
Patent Application: [Application Number]
Filing Date: [Date]

This code implements patent-pending technology.
Unauthorized use may infringe on pending patent rights.

PATENT CLAIM: [Claim Number] - Immutable audit trail for trading signals
PATENT CLAIM: [Claim Number] - Cryptographic verification system
See: docs/SystemDocs/PATENT_PENDING_TECHNOLOGY.md for patent details
"""
import json, hashlib, sqlite3, logging, threading, time, asyncio
from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager
from typing import List, Dict, Optional, Tuple
from collections import deque

# Use relative path that works in both dev and production
import os
if os.path.exists("/root/argo-production"):
    BASE_DIR = Path("/root/argo-production")
else:
    # Development/local path
    BASE_DIR = Path(__file__).parent.parent.parent.parent
DB_FILE = BASE_DIR / "data" / "signals.db"
SIGNALS_LOG = BASE_DIR / "logs" / "signals.log"

for directory in [BASE_DIR / "data", BASE_DIR / "logs"]:
    directory.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SignalTracker")

class SignalTracker:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.db_file = DB_FILE
            self.signals_log = SIGNALS_LOG
            
            # OPTIMIZATION: Connection pooling for SQLite
            self._connection_pool = deque(maxlen=5)  # Max 5 connections in pool
            self._pool_lock = threading.Lock()
            
            # OPTIMIZATION: Batch insert queue (optimized batch size)
            self._pending_signals = []
            self._batch_lock = threading.Lock()
            self._batch_size = 50  # Optimal batch size (increased from 10)
            self._batch_timeout = 5.0  # Or after 5 seconds (increased from 0.5s)
            self._last_flush = datetime.now(timezone.utc)
            
            # OPTIMIZATION: Query result caching
            self._query_cache: Dict[str, tuple] = {}  # {cache_key: (timestamp, result)}
            self._cache_ttl = 30  # 30 second cache for queries
            
            self._init_database()
            self._initialized = True
            logger.info("✅ Signal Tracker initialized (with connection pooling and batch inserts)")
    
    def _init_database(self):
        """Initialize database with WAL mode for better concurrency"""
        # Create initial connection for setup (before pool is ready)
        conn = sqlite3.connect(str(self.db_file), check_same_thread=False, timeout=10.0)
        cursor = conn.cursor()
        
        # Enable WAL mode for better concurrency (OPTIMIZATION)
        cursor.execute('PRAGMA journal_mode=WAL')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS signals (
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
        )''')
        
        # OPTIMIZATION: Add indexes for better query performance
        from argo.core.database_indexes import DatabaseIndexes
        from argo.backtest.constants import DatabaseConstants
        
        DatabaseIndexes.create_all_indexes(cursor)
        
        # OPTIMIZATION: Optimize SQLite settings for better concurrency
        cursor.execute(f'PRAGMA synchronous={DatabaseConstants.SQLITE_SYNCHRONOUS}')
        cursor.execute(f'PRAGMA cache_size=-{DatabaseConstants.SQLITE_CACHE_SIZE_KB}')
        cursor.execute(f'PRAGMA temp_store={DatabaseConstants.SQLITE_TEMP_STORE}')
        cursor.execute(f'PRAGMA mmap_size={DatabaseConstants.SQLITE_MMAP_SIZE_BYTES}')
        
        conn.commit()
        conn.close()
    
    @contextmanager
    def _get_connection(self):
        """Get connection from pool or create new one (OPTIMIZATION: Connection pooling)"""
        conn = None
        try:
            # Try to get from pool
            with self._pool_lock:
                if self._connection_pool:
                    conn = self._connection_pool.popleft()
                    # Test connection is still valid
                    try:
                        conn.execute('SELECT 1').fetchone()
                    except sqlite3.Error:
                        # Connection is stale, create new one
                        try:
                            conn.close()
                        except (sqlite3.Error, AttributeError, OSError):
                            # Ignore errors when closing stale connection
                            pass
                        conn = None
            
            # Create new connection if pool is empty or connection was stale
            if conn is None:
                from argo.backtest.constants import DatabaseConstants
                conn = sqlite3.connect(str(self.db_file), check_same_thread=False, timeout=DatabaseConstants.SQLITE_CONNECTION_TIMEOUT)
                # Enable WAL mode for better concurrency
                conn.execute('PRAGMA journal_mode=WAL')
            
            yield conn
            
            # Return to pool
            with self._pool_lock:
                from argo.backtest.constants import DatabaseConstants
                if len(self._connection_pool) < DatabaseConstants.SQLITE_MAX_POOL_SIZE:
                    self._connection_pool.append(conn)
                else:
                    conn.close()
        except Exception:
            if conn:
                try:
                    conn.close()
                except (sqlite3.Error, AttributeError, OSError):
                    # Ignore errors when closing connection in error handler
                    pass
            raise
    
    def _generate_signal_id(self):
        # OPTIMIZATION: Use timezone-aware datetime for consistency
        timestamp = datetime.now(timezone.utc).isoformat()
        combined = f"{timestamp}:{threading.current_thread().ident}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def _calculate_sha256(self, signal):
        hashable = {k: signal[k] for k in ['signal_id', 'symbol', 'action', 'entry_price', 
                    'target_price', 'stop_price', 'confidence', 'strategy', 'timestamp'] if k in signal}
        return hashlib.sha256(json.dumps(hashable, sort_keys=True).encode()).hexdigest()
    
    def log_signal(self, signal):
        """
        Log signal with latency tracking and server timestamp
        OPTIMIZED: Uses batch inserts for better performance
        
        PATENT CLAIM: Real-time delivery tracking (<500ms)
        """
        start_time = time.time()
        
        with self._lock:
            signal = self._prepare_signal(signal, start_time)
            
            # OPTIMIZATION: Queue for batch insert instead of immediate insert
            with self._batch_lock:
                self._pending_signals.append((signal, start_time))
                
                # Check for async batch flushing if enabled
                try:
                    from argo.core.feature_flags import get_feature_flags
                    feature_flags = get_feature_flags()
                    
                    if feature_flags.is_enabled('async_batch_db'):
                        # Schedule async flush if needed
                        import asyncio
                        if len(self._pending_signals) >= self._batch_size:
                            # Schedule async flush
                            try:
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    asyncio.create_task(self._flush_batch_async())
                                else:
                                    loop.run_until_complete(self._flush_batch_async())
                            except RuntimeError:
                                # No event loop, fall back to sync
                                self._flush_batch()
                        elif not hasattr(self, '_flush_task') or (hasattr(self, '_flush_task') and (self._flush_task is None or self._flush_task.done())):
                            # Schedule timeout flush
                            try:
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    self._flush_task = asyncio.create_task(self._flush_after_timeout())
                            except RuntimeError:
                                pass  # No event loop, skip async
                    else:
                        # Sync batch flush
                        if len(self._pending_signals) >= self._batch_size:
                            self._flush_batch()
                except Exception as e:
                    logger.debug(f"Could not use async batch flush: {e}, using sync")
                    # Fallback to sync
                    if len(self._pending_signals) >= self._batch_size:
                        self._flush_batch()
            
            # Still log to file immediately (for audit trail)
            self._log_to_file(signal)
            
            return signal['signal_id']
    
    async def log_signal_async(self, signal):
        """
        Async version of log_signal for non-blocking signal logging
        OPTIMIZED: Uses async batch inserts with automatic background flushing
        """
        start_time = time.time()
        
        signal = self._prepare_signal(signal, start_time)
        
        with self._batch_lock:
            self._pending_signals.append((signal, start_time))
            
            # Flush if batch is full
            if len(self._pending_signals) >= self._batch_size:
                await self._flush_batch_async()
            elif not hasattr(self, '_flush_task') or (hasattr(self, '_flush_task') and (self._flush_task is None or self._flush_task.done())):
                # Schedule timeout flush
                import asyncio
                self._flush_task = asyncio.create_task(self._flush_after_timeout())
        
        # Still log to file immediately (for audit trail)
        self._log_to_file(signal)
        
        return signal['signal_id']
    
    async def _flush_after_timeout(self):
        """Flush batch after timeout (5 seconds)"""
        import asyncio
        await asyncio.sleep(self._batch_timeout)  # Use configured timeout
        await self._flush_batch_async()
    
    async def _flush_batch_async(self):
        """Async batch insert (non-blocking)"""
        if not self._pending_signals:
            return
        
        # Copy and clear pending signals
        signals_to_insert = self._pending_signals.copy()
        self._pending_signals.clear()
        
        try:
            # Use sync connection in async context (SQLite doesn't have native async)
            # But we can run it in executor to avoid blocking
            import asyncio
            loop = asyncio.get_event_loop()
            
            def sync_flush():
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    insert_data = []
                    for signal, start_time in signals_to_insert:
                        insert_data.append((
                            signal['signal_id'], signal['symbol'], signal['action'],
                            signal['entry_price'], signal['target_price'], signal['stop_price'],
                            signal['confidence'], signal['strategy'],
                            signal.get('asset_type', 'unknown'),
                            signal.get('data_source', 'weighted_consensus'),
                            signal['timestamp'], signal['sha256'],
                            signal.get('order_id')
                        ))
                    
                    cursor.executemany('''INSERT INTO signals (
                        signal_id, symbol, action, entry_price, target_price, stop_price,
                        confidence, strategy, asset_type, data_source, timestamp, sha256, order_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', insert_data)
                    
                    conn.commit()
                    
                    # Record metrics
                    for signal, start_time in signals_to_insert:
                        self._record_metrics(start_time)
            
            # Run in executor to avoid blocking
            await loop.run_in_executor(None, sync_flush)
            
            logger.info(f"✅ Async batch inserted {len(signals_to_insert)} signals")
        except Exception as e:
            logger.error(f"Async batch insert error: {e}")
            # Fallback to sync
            self._pending_signals.extend(signals_to_insert)
            self._flush_batch()
    
    def _flush_batch(self):
        """Flush pending signals in batch insert (OPTIMIZATION)"""
        if not self._pending_signals:
            return
        
        # Copy and clear pending signals
        signals_to_insert = self._pending_signals.copy()
        self._pending_signals.clear()
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Batch insert all signals in single transaction
                insert_data = []
                for signal, start_time in signals_to_insert:
                    insert_data.append((
                        signal['signal_id'], signal['symbol'], signal['action'],
                        signal['entry_price'], signal['target_price'], signal['stop_price'],
                        signal['confidence'], signal['strategy'],
                        signal.get('asset_type', 'unknown'),
                        signal.get('data_source', 'weighted_consensus'),
                        signal['timestamp'], signal['sha256'],
                        signal.get('order_id')
                    ))
                
                cursor.executemany('''INSERT INTO signals (
                    signal_id, symbol, action, entry_price, target_price, stop_price,
                    confidence, strategy, asset_type, data_source, timestamp, sha256, order_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', insert_data)
                
                conn.commit()
                
                # Record metrics for all signals
                for signal, start_time in signals_to_insert:
                    self._record_metrics(start_time)
                
                logger.info(f"✅ Batch inserted {len(signals_to_insert)} signals")
        except sqlite3.IntegrityError as e:
            # Handle duplicate signals individually
            logger.warning(f"Batch insert had integrity errors, inserting individually: {e}")
            for signal, start_time in signals_to_insert:
                try:
                    self._persist_signal_individual(signal)
                    self._record_metrics(start_time)
                except sqlite3.IntegrityError:
                    logger.warning(f"Signal {signal['signal_id']} already exists")
        except Exception as e:
            logger.error(f"Batch insert error: {e}")
            # Fallback to individual inserts
            for signal, start_time in signals_to_insert:
                try:
                    self._persist_signal_individual(signal)
                    self._record_metrics(start_time)
                except Exception as e2:
                    logger.error(f"Individual insert error: {e2}")
    
    def flush_pending(self):
        """Manually flush pending signals (call before shutdown)"""
        with self._batch_lock:
            if self._pending_signals:
                self._flush_batch()
    
    def _prepare_signal(self, signal, start_time):
        """Prepare signal with ID, timestamp, hash, and latency tracking"""
        # OPTIMIZATION: Single datetime call for consistency
        now = datetime.now(timezone.utc)
        
        if 'signal_id' not in signal:
            signal['signal_id'] = self._generate_signal_id()
        if 'timestamp' not in signal:
            signal['timestamp'] = now.isoformat()
        
        # Add server timestamp for latency calculation
        signal['server_timestamp'] = start_time
        
        signal['sha256'] = self._calculate_sha256(signal)
        
        # Calculate generation latency
        generation_latency_ms = int((time.time() - start_time) * 1000)
        signal['generation_latency_ms'] = generation_latency_ms
        
        return signal
    
    def _persist_signal_individual(self, signal):
        """Persist single signal to database (fallback method)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''INSERT INTO signals (
                    signal_id, symbol, action, entry_price, target_price, stop_price,
                    confidence, strategy, asset_type, data_source, timestamp, sha256, order_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (signal['signal_id'], signal['symbol'], signal['action'],
                 signal['entry_price'], signal['target_price'], signal['stop_price'],
                 signal['confidence'], signal['strategy'],
                 signal.get('asset_type', 'unknown'),
                 signal.get('data_source', 'weighted_consensus'),
                 signal['timestamp'], signal['sha256'],
                 signal.get('order_id')))
                conn.commit()
                logger.info(f"✅ Signal logged: {signal['signal_id']} - {signal['symbol']}")
            except sqlite3.IntegrityError:
                logger.warning(f"Signal {signal['signal_id']} already exists")
    
    def _log_to_file(self, signal):
        """Write signal to log file"""
        with self.signals_log.open('a') as f:
            f.write(json.dumps(signal, sort_keys=True) + '\n')
    
    def _record_metrics(self, start_time):
        """Record Prometheus metrics if available"""
        try:
            from argo.core.metrics import signal_generation_latency
            signal_generation_latency.observe(time.time() - start_time)
        except (ImportError, AttributeError):
            pass  # Metrics not available
    
    def get_latest_signals(self, symbol: str, limit: int = 10):
        """
        Get latest signals with caching (OPTIMIZATION)
        
        Args:
            symbol: Trading symbol
            limit: Maximum number of signals to return
        
        Returns:
            List of signal dictionaries
        """
        cache_key = f"latest_signals:{symbol}:{limit}"
        cache_time, cached_result = self._query_cache.get(cache_key, (None, None))
        
        # Check if cache is still valid
        if cache_time and (datetime.now(timezone.utc) - cache_time).total_seconds() < self._cache_ttl:
            logger.debug(f"✅ Query cache hit for {symbol}")
            return cached_result
        
        # Query database
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT signal_id, symbol, action, entry_price, target_price, stop_price,
                          confidence, strategy, timestamp, outcome, profit_loss_pct
                   FROM signals 
                   WHERE symbol = ? 
                   ORDER BY timestamp DESC 
                   LIMIT ?""",
                (symbol, limit)
            )
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            results = []
            for row in rows:
                results.append({
                    'signal_id': row[0],
                    'symbol': row[1],
                    'action': row[2],
                    'entry_price': row[3],
                    'target_price': row[4],
                    'stop_price': row[5],
                    'confidence': row[6],
                    'strategy': row[7],
                    'timestamp': row[8],
                    'outcome': row[9],
                    'profit_loss_pct': row[10]
                })
        
        # Cache result
        self._query_cache[cache_key] = (datetime.now(timezone.utc), results)
        
        # Cleanup old cache entries
        self._cleanup_query_cache()
        
        return results
    
    def _cleanup_query_cache(self):
        """Clean up expired query cache entries"""
        now = datetime.now(timezone.utc)
        expired_keys = [
            key for key, (cache_time, _) in self._query_cache.items()
            if (now - cache_time).total_seconds() >= self._cache_ttl
        ]
        for key in expired_keys:
            del self._query_cache[key]
    
    def get_stats(self):
        """Get statistics using connection pool"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''SELECT 
                COUNT(*),
                SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END),
                SUM(CASE WHEN outcome = 'loss' THEN 1 ELSE 0 END),
                AVG(CASE WHEN outcome IS NOT NULL THEN profit_loss_pct END)
            FROM signals''')
            
            total, wins, losses, avg_return = cursor.fetchone()
            completed = wins + losses
            win_rate = (wins / completed * 100) if completed > 0 else 0
            
            return {
                'total_signals': total,
                'wins': wins,
                'losses': losses,
                'win_rate': round(win_rate, 2),
                'average_return': round(avg_return or 0, 2),
                'last_updated': datetime.utcnow().isoformat()
            }
