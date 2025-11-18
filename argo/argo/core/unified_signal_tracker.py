#!/usr/bin/env python3
"""
TRADE SECRET - PROPRIETARY ALGORITHM
Argo Capital - Confidential

Unified Signal Tracker v1.0
Single database for all services with service tagging

This code contains proprietary algorithms and trade secrets.
Unauthorized disclosure, copying, or use is strictly prohibited.

PATENT-PENDING TECHNOLOGY
"""
import json
import hashlib
import sqlite3
import logging
import threading
import time
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from contextlib import contextmanager
from typing import List, Dict, Optional, Tuple
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UnifiedSignalTracker")


class UnifiedSignalTracker:
    """
    Unified Signal Tracker - Single database for all services
    Supports service tagging for multi-executor architecture
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: Optional[Path] = None):
        if not hasattr(self, '_initialized'):
            # Determine unified database path
            if db_path is None:
                # Check for unified production path first
                if Path("/root/argo-production-unified").exists():
                    BASE_DIR = Path("/root/argo-production-unified")
                elif Path("/root/argo-production-prop-firm").exists():
                    # Fallback to prop firm if unified doesn't exist yet
                    BASE_DIR = Path("/root/argo-production-prop-firm")
                elif Path("/root/argo-production-green").exists():
                    BASE_DIR = Path("/root/argo-production-green")
                elif Path("/root/argo-production").exists():
                    BASE_DIR = Path("/root/argo-production")
                else:
                    # Development/local path
                    BASE_DIR = Path(__file__).parent.parent.parent.parent
                
                self.db_file = BASE_DIR / "data" / "signals_unified.db"
            else:
                self.db_file = db_path
            
            # Ensure directories exist
            for directory in [self.db_file.parent, BASE_DIR / "logs"]:
                directory.mkdir(parents=True, exist_ok=True)
            
            self.signals_log = BASE_DIR / "logs" / "signals.log"
            
            # OPTIMIZATION: Connection pooling
            self._connection_pool = deque(maxlen=5)
            self._pool_lock = threading.Lock()
            
            # OPTIMIZATION: Batch insert queue
            self._pending_signals = []
            self._batch_lock = threading.Lock()
            self._batch_size = 50
            self._batch_timeout = 5.0
            self._periodic_flush_interval = 10.0
            self._last_flush = datetime.now(timezone.utc)
            self._periodic_flush_task = None
            
            # OPTIMIZATION: Query result caching
            self._query_cache: Dict[str, tuple] = {}
            self._cache_ttl = 30
            
            self._init_database()
            self._initialized = True
            logger.info(f"✅ Unified Signal Tracker initialized: {self.db_file}")
    
    def _init_database(self):
        """Initialize unified database with service tagging"""
        conn = sqlite3.connect(str(self.db_file), check_same_thread=False, timeout=10.0)
        cursor = conn.cursor()
        
        # Enable WAL mode for better concurrency
        cursor.execute('PRAGMA journal_mode=WAL')
        
        # Enhanced schema with service tagging
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
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
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                -- NEW: Service tagging for unified architecture
                service_type TEXT DEFAULT 'both',
                executor_id TEXT DEFAULT NULL,
                generated_by TEXT DEFAULT 'signal_generator',
                -- Additional metadata
                regime TEXT DEFAULT NULL,
                reasoning TEXT DEFAULT NULL
            )
        ''')
        
        # Add new columns if they don't exist (for migration)
        try:
            cursor.execute('ALTER TABLE signals ADD COLUMN service_type TEXT DEFAULT "both"')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute('ALTER TABLE signals ADD COLUMN executor_id TEXT DEFAULT NULL')
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute('ALTER TABLE signals ADD COLUMN generated_by TEXT DEFAULT "signal_generator"')
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute('ALTER TABLE signals ADD COLUMN regime TEXT DEFAULT NULL')
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute('ALTER TABLE signals ADD COLUMN reasoning TEXT DEFAULT NULL')
        except sqlite3.OperationalError:
            pass
        
        # Indexes for service-based queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_service_type ON signals(service_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_executor_id ON signals(executor_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_generated_by ON signals(generated_by)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_symbol_created ON signals(symbol, created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_confidence ON signals(confidence)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON signals(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_id ON signals(order_id)')
        
        # OPTIMIZATION: Optimize SQLite settings
        try:
            from argo.backtest.constants import DatabaseConstants
            cursor.execute(f'PRAGMA synchronous={DatabaseConstants.SQLITE_SYNCHRONOUS}')
            cursor.execute(f'PRAGMA cache_size=-{DatabaseConstants.SQLITE_CACHE_SIZE_KB}')
            cursor.execute(f'PRAGMA temp_store={DatabaseConstants.SQLITE_TEMP_STORE}')
            cursor.execute(f'PRAGMA mmap_size={DatabaseConstants.SQLITE_MMAP_SIZE_BYTES}')
        except ImportError:
            # Fallback if constants not available
            cursor.execute('PRAGMA synchronous=NORMAL')
            cursor.execute('PRAGMA cache_size=-64000')
            cursor.execute('PRAGMA temp_store=MEMORY')
            cursor.execute('PRAGMA mmap_size=268435456')
        
        conn.commit()
        conn.close()
    
    @contextmanager
    def _get_connection(self):
        """Get connection from pool or create new one"""
        conn = None
        try:
            with self._pool_lock:
                if self._connection_pool:
                    conn = self._connection_pool.popleft()
                    try:
                        conn.execute('SELECT 1').fetchone()
                    except sqlite3.Error:
                        try:
                            conn.close()
                        except:
                            pass
                        conn = None
            
            if conn is None:
                conn = sqlite3.connect(str(self.db_file), check_same_thread=False, timeout=10.0)
                conn.execute('PRAGMA journal_mode=WAL')
            
            yield conn
            
            with self._pool_lock:
                if len(self._connection_pool) < 5:
                    self._connection_pool.append(conn)
                else:
                    conn.close()
        except Exception:
            if conn:
                try:
                    conn.close()
                except:
                    pass
            raise
    
    def _generate_signal_id(self):
        """Generate unique signal ID"""
        timestamp = datetime.now(timezone.utc).isoformat()
        combined = f"{timestamp}:{threading.current_thread().ident}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def _calculate_sha256(self, signal):
        """Calculate SHA-256 hash for signal verification"""
        hashable = {k: signal[k] for k in ['signal_id', 'symbol', 'action', 'entry_price', 
                    'target_price', 'stop_price', 'confidence', 'strategy', 'timestamp'] if k in signal}
        return hashlib.sha256(json.dumps(hashable, sort_keys=True).encode()).hexdigest()
    
    def log_signal(self, signal: Dict) -> str:
        """
        Log signal synchronously (for backward compatibility)
        Returns signal_id
        """
        start_time = time.time()
        
        signal = self._prepare_signal(signal, start_time)
        
        with self._batch_lock:
            self._pending_signals.append(signal)
            
            # Flush if batch is full
            if len(self._pending_signals) >= self._batch_size:
                self._flush_batch()
        
        return signal.get('signal_id', '')
    
    async def log_signal_async(self, signal: Dict) -> str:
        """
        Log signal asynchronously (preferred method)
        Returns signal_id
        """
        start_time = time.time()
        
        signal = self._prepare_signal(signal, start_time)
        
        with self._batch_lock:
            self._pending_signals.append(signal)
            
            # Flush if batch is full
            if len(self._pending_signals) >= self._batch_size:
                await self._flush_batch_async()
        
        return signal.get('signal_id', '')
    
    def _prepare_signal(self, signal: Dict, start_time: float) -> Dict:
        """Prepare signal for storage"""
        if 'signal_id' not in signal:
            signal['signal_id'] = self._generate_signal_id()
        
        if 'timestamp' not in signal:
            signal['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        if 'sha256' not in signal:
            signal['sha256'] = self._calculate_sha256(signal)
        
        # Ensure service tagging fields exist
        if 'service_type' not in signal:
            signal['service_type'] = signal.get('service_type', 'both')
        
        if 'generated_by' not in signal:
            signal['generated_by'] = signal.get('generated_by', 'signal_generator')
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        signal['_storage_latency_ms'] = latency_ms
        
        return signal
    
    def _flush_batch(self):
        """Flush pending signals to database (synchronous)"""
        if not self._pending_signals:
            return
        
        signals_to_insert = self._pending_signals.copy()
        self._pending_signals.clear()
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                for signal in signals_to_insert:
                    try:
                        cursor.execute('''
                            INSERT OR IGNORE INTO signals (
                                signal_id, symbol, action, entry_price, target_price, stop_price,
                                confidence, strategy, asset_type, data_source, timestamp,
                                outcome, exit_price, profit_loss_pct, sha256, order_id, created_at,
                                service_type, executor_id, generated_by, regime, reasoning
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            signal.get('signal_id'),
                            signal.get('symbol'),
                            signal.get('action'),
                            signal.get('entry_price'),
                            signal.get('target_price'),
                            signal.get('stop_price'),
                            signal.get('confidence'),
                            signal.get('strategy', 'weighted_consensus_v6'),
                            signal.get('asset_type', 'stock'),
                            signal.get('data_source', 'weighted_consensus'),
                            signal.get('timestamp'),
                            signal.get('outcome'),
                            signal.get('exit_price'),
                            signal.get('profit_loss_pct'),
                            signal.get('order_id'),
                            signal.get('created_at', datetime.now(timezone.utc).isoformat()),
                            signal.get('service_type', 'both'),
                            signal.get('executor_id'),
                            signal.get('generated_by', 'signal_generator'),
                            signal.get('regime'),
                            signal.get('reasoning')
                        ))
                    except sqlite3.IntegrityError:
                        # Signal already exists, skip
                        logger.debug(f"Signal {signal.get('signal_id')} already exists, skipping")
                    except Exception as e:
                        logger.error(f"Error inserting signal: {e}")
                
                conn.commit()
                logger.debug(f"✅ Batch inserted {len(signals_to_insert)} signals")
        except Exception as e:
            logger.error(f"Error flushing batch: {e}")
            # Re-add signals to queue for retry
            self._pending_signals.extend(signals_to_insert)
    
    async def _flush_batch_async(self):
        """Flush pending signals to database (asynchronous)"""
        # Run synchronous flush in thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._flush_batch)
    
    async def flush_pending_async(self):
        """Flush all pending signals asynchronously"""
        await self._flush_batch_async()
    
    def flush_pending(self):
        """Flush all pending signals synchronously"""
        self._flush_batch()
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM signals")
                total = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM signals WHERE order_id IS NOT NULL AND order_id != ''")
                executed = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM signals WHERE created_at >= datetime('now', '-24 hours')")
                last_24h = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM signals WHERE created_at >= datetime('now', '-1 hour')")
                last_1h = cursor.fetchone()[0]
                
                return {
                    'total_signals': total,
                    'executed_trades': executed,
                    'signals_24h': last_24h,
                    'signals_1h': last_1h
                }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def get_signals_for_executor(self, executor_id: str, limit: int = 100) -> List[Dict]:
        """Get signals for specific executor"""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM signals 
                    WHERE (service_type = ? OR service_type = 'both')
                    AND (executor_id IS NULL OR executor_id = ?)
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (executor_id, executor_id, limit))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting signals for executor {executor_id}: {e}")
            return []

