"""
Smart Signal Queue System
Queues signals that can't execute immediately and executes them when conditions are met
"""
import sqlite3
import json
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger("SignalQueue")

class QueueStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    EXECUTING = "executing"
    EXECUTED = "executed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class ExecutionCondition(str, Enum):
    NEEDS_BUYING_POWER = "needs_buying_power"
    NEEDS_POSITION = "needs_position"
    NEEDS_BUYING_POWER_FOR_SHORT = "needs_buying_power_for_short"
    MARKET_HOURS = "market_hours"
    RISK_LIMIT = "risk_limit"

@dataclass
class QueuedSignal:
    """Represents a signal in the execution queue"""
    signal_id: str
    symbol: str
    action: str
    entry_price: float
    target_price: float
    stop_price: float
    confidence: float
    timestamp: str
    conditions: List[Dict]  # List of conditions that must be met
    priority: float  # Based on confidence and time
    status: QueueStatus
    queued_at: str
    expires_at: Optional[str] = None
    executor_id: Optional[str] = None
    retry_count: int = 0
    last_checked: Optional[str] = None

class SignalQueue:
    """Smart signal queue that tracks execution conditions"""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            # Use same database as signal tracker
            import os
            if os.path.exists("/root/argo-production"):
                BASE_DIR = Path("/root/argo-production")
            elif os.path.exists("/root/argo-production-green"):
                BASE_DIR = Path("/root/argo-production-green")
            else:
                BASE_DIR = Path(__file__).parent.parent.parent.parent
            db_path = BASE_DIR / "data" / "signals_unified.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self._monitoring_task = None
        self._running = False

    def _init_database(self):
        """Initialize queue database table"""
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id TEXT UNIQUE NOT NULL,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                entry_price REAL NOT NULL,
                target_price REAL NOT NULL,
                stop_price REAL NOT NULL,
                confidence REAL NOT NULL,
                timestamp TEXT NOT NULL,
                conditions TEXT NOT NULL,  -- JSON array of conditions
                priority REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                queued_at TEXT NOT NULL,
                expires_at TEXT,
                executor_id TEXT,
                retry_count INTEGER DEFAULT 0,
                last_checked TEXT,
                executed_at TEXT,
                execution_error TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_queue_status ON signal_queue(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_queue_priority ON signal_queue(priority DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_queue_expires ON signal_queue(expires_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_queue_symbol ON signal_queue(symbol)')

        conn.commit()
        conn.close()
        logger.info("✅ Signal queue database initialized")

    def queue_signal(self, signal: Dict, conditions: List[Dict], executor_id: Optional[str] = None, rejection_error: Optional[str] = None) -> str:
        """
        Queue a signal that can't execute immediately

        Args:
            signal: Signal dictionary
            conditions: List of conditions that must be met for execution
            executor_id: Target executor (None for any)
            rejection_error: Error message from rejection (optional)

        Returns:
            Queue entry ID
        """
        signal_id = signal.get('signal_id') or signal.get('id')
        if not signal_id:
            # Generate signal ID if not present
            signal_id = f"{signal.get('symbol', 'UNKNOWN')}_{datetime.now().isoformat()}"

        # Calculate priority (higher confidence + more recent = higher priority)
        confidence = signal.get('confidence', 0)
        time_factor = 1.0  # Signals are fresh
        priority = confidence * time_factor

        # Set expiration (24 hours default)
        expires_at = (datetime.now() + timedelta(hours=24)).isoformat()

        queued_signal = QueuedSignal(
            signal_id=signal_id,
            symbol=signal.get('symbol', 'UNKNOWN'),
            action=signal.get('action', signal.get('direction', 'UNKNOWN')),
            entry_price=signal.get('entry_price', signal.get('price', 0)),
            target_price=signal.get('target_price', signal.get('take_profit', 0)),
            stop_price=signal.get('stop_price', signal.get('stop_loss', 0)),
            confidence=confidence,
            timestamp=signal.get('timestamp', datetime.now().isoformat()),
            conditions=conditions,
            priority=priority,
            status=QueueStatus.PENDING,
            queued_at=datetime.now().isoformat(),
            expires_at=expires_at,
            executor_id=executor_id
        )

        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO signal_queue (
                    signal_id, symbol, action, entry_price, target_price, stop_price,
                    confidence, timestamp, conditions, priority, status, queued_at,
                    expires_at, executor_id, execution_error
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                queued_signal.signal_id,
                queued_signal.symbol,
                queued_signal.action,
                queued_signal.entry_price,
                queued_signal.target_price,
                queued_signal.stop_price,
                queued_signal.confidence,
                queued_signal.timestamp,
                json.dumps(queued_signal.conditions),
                queued_signal.priority,
                queued_signal.status.value,
                queued_signal.queued_at,
                queued_signal.expires_at,
                queued_signal.executor_id,
                rejection_error
            ))
            conn.commit()
            logger.info(f"✅ Queued signal {signal_id} with {len(conditions)} conditions")
            return queued_signal.signal_id
        except Exception as e:
            logger.error(f"❌ Error queueing signal: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def check_conditions(self, queued_signal: QueuedSignal, account_state: Dict) -> Tuple[bool, List[str]]:
        """
        Check if all conditions are met for a queued signal

        Returns:
            (can_execute, unmet_conditions)
        """
        unmet_conditions = []

        for condition in queued_signal.conditions:
            condition_type = condition.get('type')
            required_value = condition.get('value')

            if condition_type == ExecutionCondition.NEEDS_BUYING_POWER:
                buying_power = account_state.get('buying_power', 0)
                if buying_power < required_value:
                    unmet_conditions.append(f"Need ${required_value} buying power, have ${buying_power}")

            elif condition_type == ExecutionCondition.NEEDS_POSITION:
                symbol = condition.get('symbol', queued_signal.symbol)
                positions = account_state.get('positions', [])
                has_position = any(p.get('symbol') == symbol for p in positions)
                if not has_position:
                    unmet_conditions.append(f"Need position in {symbol}")

            elif condition_type == ExecutionCondition.NEEDS_BUYING_POWER_FOR_SHORT:
                buying_power = account_state.get('buying_power', 0)
                if buying_power < required_value:
                    unmet_conditions.append(f"Need ${required_value} buying power for short, have ${buying_power}")

        return len(unmet_conditions) == 0, unmet_conditions

    def get_ready_signals(self, limit: int = 10) -> List[QueuedSignal]:
        """Get signals that are ready to execute (sorted by priority)"""
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM signal_queue
            WHERE status = 'ready'
            ORDER BY priority DESC, queued_at ASC
            LIMIT ?
        ''', (limit,))

        signals = []
        for row in cursor.fetchall():
            signals.append(self._row_to_queued_signal(row))

        conn.close()
        return signals

    def _row_to_queued_signal(self, row) -> QueuedSignal:
        """Convert database row to QueuedSignal"""
        return QueuedSignal(
            signal_id=row['signal_id'],
            symbol=row['symbol'],
            action=row['action'],
            entry_price=row['entry_price'],
            target_price=row['target_price'],
            stop_price=row['stop_price'],
            confidence=row['confidence'],
            timestamp=row['timestamp'],
            conditions=json.loads(row['conditions'] or '[]'),
            priority=row['priority'],
            status=QueueStatus(row['status']),
            queued_at=row['queued_at'],
            expires_at=row['expires_at'] if row['expires_at'] else None,
            executor_id=row['executor_id'] if row['executor_id'] else None,
            retry_count=row['retry_count'] or 0,
            last_checked=row['last_checked'] if row['last_checked'] else None
        )

    async def start_monitoring(self, check_interval: int = 30):
        """Start background monitoring task"""
        self._running = True
        logger.info(f"🔄 Starting signal queue monitoring (check every {check_interval}s)")

        while self._running:
            try:
                await self._check_queue()
                await asyncio.sleep(check_interval)
            except Exception as e:
                logger.error(f"❌ Error in queue monitoring: {e}")
                await asyncio.sleep(check_interval)

    async def _check_queue(self):
        """Check queue and update signal statuses"""
        # Get account states
        account_states = await self._get_account_states()

        # Get pending signals
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM signal_queue
            WHERE status = 'pending' AND (expires_at IS NULL OR expires_at > datetime('now'))
            ORDER BY priority DESC
        ''')

        updated_count = 0
        for row in cursor.fetchall():
            queued_signal = self._row_to_queued_signal(row)

            # Check each executor
            for executor_id, account_state in account_states.items():
                can_execute, unmet = self.check_conditions(queued_signal, account_state)

                if can_execute:
                    # Mark as ready
                    cursor.execute('''
                        UPDATE signal_queue
                        SET status = 'ready', last_checked = datetime('now')
                        WHERE signal_id = ?
                    ''', (queued_signal.signal_id,))
                    updated_count += 1
                    logger.info(f"✅ Signal {queued_signal.signal_id} is ready for execution")
                    break

        conn.commit()
        conn.close()

        if updated_count > 0:
            logger.info(f"📊 Updated {updated_count} signals to ready status")

    async def _get_account_states(self) -> Dict[str, Dict]:
        """Get current account states for all executors"""
        import httpx

        account_states = {}
        executors = [
            ('argo', 8000),
            ('prop_firm', 8001)
        ]

        async with httpx.AsyncClient(timeout=5.0) as client:
            for executor_id, port in executors:
                try:
                    response = await client.get(f'http://localhost:{port}/api/v1/trading/status')
                    if response.status_code == 200:
                        data = response.json()
                        account = data.get('account', {})
                        account_states[executor_id] = {
                            'buying_power': account.get('buying_power', 0),
                            'cash': account.get('cash', 0),
                            'portfolio_value': account.get('portfolio_value', 0),
                            'positions': []  # Would need to fetch separately
                        }
                except Exception as e:
                    logger.debug(f"Could not get account state for {executor_id}: {e}")

        return account_states

    def stop_monitoring(self):
        """Stop background monitoring"""
        self._running = False
        logger.info("🛑 Stopped signal queue monitoring")

    def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics"""
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        cursor = conn.cursor()

        stats: Dict[str, int] = {}
        for status in QueueStatus:
            cursor.execute('SELECT COUNT(*) FROM signal_queue WHERE status = ?', (status.value,))
            stats[status.value] = cursor.fetchone()[0] or 0

        conn.close()
        return stats
