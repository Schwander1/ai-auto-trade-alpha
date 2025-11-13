#!/usr/bin/env python3
"""Alpine Analytics - Enterprise Signal Tracker v4.1"""
import json, hashlib, sqlite3, logging, threading, time
from datetime import datetime
from pathlib import Path

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
            self._init_database()
            self._initialized = True
            logger.info("✅ Signal Tracker initialized")
    
    def _init_database(self):
        conn = sqlite3.connect(str(self.db_file))
        cursor = conn.cursor()
        
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
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_symbol ON signals(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON signals(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_outcome ON signals(outcome)')
        
        conn.commit()
        conn.close()
    
    def _generate_signal_id(self):
        timestamp = datetime.utcnow().isoformat()
        combined = f"{timestamp}:{threading.current_thread().ident}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def _calculate_sha256(self, signal):
        hashable = {k: signal[k] for k in ['signal_id', 'symbol', 'action', 'entry_price', 
                    'target_price', 'stop_price', 'confidence', 'strategy', 'timestamp'] if k in signal}
        return hashlib.sha256(json.dumps(hashable, sort_keys=True).encode()).hexdigest()
    
    def log_signal(self, signal):
        """
        Log signal with latency tracking and server timestamp
        
        PATENT CLAIM: Real-time delivery tracking (<500ms)
        """
        start_time = time.time()
        
        with self._lock:
            if 'signal_id' not in signal:
                signal['signal_id'] = self._generate_signal_id()
            if 'timestamp' not in signal:
                signal['timestamp'] = datetime.utcnow().isoformat()
            
            # Add server timestamp for latency calculation
            signal['server_timestamp'] = start_time
            
            signal['sha256'] = self._calculate_sha256(signal)
            
            # Calculate generation latency
            generation_latency_ms = int((time.time() - start_time) * 1000)
            signal['generation_latency_ms'] = generation_latency_ms
            
            # Record Prometheus metric if available
            try:
                from argo.core.metrics import signal_generation_latency
                signal_generation_latency.observe(time.time() - start_time)
            except (ImportError, AttributeError):
                pass  # Metrics not available
            
            conn = sqlite3.connect(str(self.db_file))
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
            finally:
                conn.close()
            
            with self.signals_log.open('a') as f:
                f.write(json.dumps(signal, sort_keys=True) + '\n')
            
            # Sync to Alpine Backend PostgreSQL
            try:
                from argo.core.alpine_sync import get_alpine_sync
                alpine_sync = get_alpine_sync()
                if alpine_sync.enabled:
                    alpine_sync.sync_signal(signal)
            except Exception as e:
                logger.debug(f"Alpine sync error (non-critical): {e}")
            
            return signal['signal_id']
    
    def get_stats(self):
        conn = sqlite3.connect(str(self.db_file))
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
        
        conn.close()
        
        return {
            'total_signals': total,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 2),
            'average_return': round(avg_return or 0, 2),
            'last_updated': datetime.utcnow().isoformat()
        }
