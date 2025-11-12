"""
Enterprise-Grade Performance Tracking System
Stocks (Alpaca Paper Trading) + Crypto Signals
"""

import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import redis
except ImportError:
    print("Warning: redis not installed, using dict as fallback")
    redis = None


class AssetClass(Enum):
    STOCK = "stock"
    CRYPTO = "crypto"


class SignalType(Enum):
    LONG = "long"
    SHORT = "short"


class TradeOutcome(Enum):
    WIN = "win"
    LOSS = "loss"
    PENDING = "pending"


@dataclass
class Trade:
    """Unified trade tracking"""
    id: str
    signal_id: str
    asset_class: str  # Use string to avoid serialization issues
    symbol: str
    signal_type: str  # Use string to avoid serialization issues
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    entry_timestamp: str  # ISO format string
    exit_timestamp: Optional[str]
    holding_period_hours: Optional[float]
    pnl_dollars: Optional[float]
    pnl_percent: Optional[float]
    outcome: str  # Use string to avoid serialization issues
    confidence: float
    verification_hash: str
    alpaca_order_id: Optional[str] = None
    exchange_order_id: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.utcnow().isoformat()


class UnifiedPerformanceTracker:
    """
    Production-ready performance tracking
    """
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.namespace = "argo:tracking"
        
        # Fallback to dict if Redis not available
        if not self.redis:
            self._memory_store = {}
            self._timeline = []
            print("⚠️  Using in-memory storage (Redis not available)")
    
    def record_signal_entry(
        self,
        signal_id: str,
        asset_class: str,  # "stock" or "crypto"
        symbol: str,
        signal_type: str,  # "long" or "short"
        entry_price: float,
        quantity: float,
        confidence: float,
        alpaca_order_id: Optional[str] = None,
        exchange_order_id: Optional[str] = None
    ) -> Trade:
        """Record signal entry"""
        
        trade_id = f"trade_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        trade = Trade(
            id=trade_id,
            signal_id=signal_id,
            asset_class=asset_class,
            symbol=symbol,
            signal_type=signal_type,
            entry_price=entry_price,
            exit_price=None,
            quantity=quantity,
            entry_timestamp=datetime.utcnow().isoformat(),
            exit_timestamp=None,
            holding_period_hours=None,
            pnl_dollars=None,
            pnl_percent=None,
            outcome="pending",
            confidence=confidence,
            verification_hash="",
            alpaca_order_id=alpaca_order_id,
            exchange_order_id=exchange_order_id
        )
        
        # Create verification hash
        trade.verification_hash = self._create_hash(trade)
        
        # Store
        self._store_trade(trade)
        
        return trade
    
    def record_signal_exit(
        self,
        trade_id: str,
        exit_price: float
    ) -> Optional[Trade]:
        """Record signal exit"""
        
        trade = self._get_trade(trade_id)
        if not trade:
            print(f"❌ Trade {trade_id} not found")
            return None
        
        # Calculate exit
        exit_time = datetime.utcnow()
        entry_time = datetime.fromisoformat(trade.entry_timestamp)
        
        trade.exit_price = exit_price
        trade.exit_timestamp = exit_time.isoformat()
        trade.holding_period_hours = (exit_time - entry_time).total_seconds() / 3600
        
        # Calculate P&L
        if trade.signal_type == "long":
            trade.pnl_dollars = (exit_price - trade.entry_price) * trade.quantity
            trade.pnl_percent = ((exit_price - trade.entry_price) / trade.entry_price) * 100
        else:  # short
            trade.pnl_dollars = (trade.entry_price - exit_price) * trade.quantity
            trade.pnl_percent = ((trade.entry_price - exit_price) / trade.entry_price) * 100
        
        # Determine outcome
        trade.outcome = "win" if trade.pnl_dollars > 0 else "loss"
        trade.updated_at = datetime.utcnow().isoformat()
        
        # Update storage
        self._store_trade(trade)
        
        return trade
    
    def get_performance_stats(
        self,
        asset_class: Optional[str] = None,
        days: int = 30
    ) -> Dict:
        """Get comprehensive statistics"""
        
        trades = self._get_recent_trades(days=days)
        
        # Filter by asset class if specified
        if asset_class:
            trades = [t for t in trades if t.asset_class == asset_class]
        
        if not trades:
            return {
                'total_trades': 0,
                'message': 'No trades found',
                'period_days': days
            }
        
        completed = [t for t in trades if t.outcome != "pending"]
        
        if not completed:
            return {
                'total_trades': len(trades),
                'pending_trades': len(trades),
                'message': 'All trades pending',
                'period_days': days
            }
        
        wins = [t for t in completed if t.outcome == "win"]
        losses = [t for t in completed if t.outcome == "loss"]
        
        total_pnl = sum(t.pnl_dollars for t in completed if t.pnl_dollars)
        avg_pnl = total_pnl / len(completed) if completed else 0
        
        return {
            # Core metrics
            'total_trades': len(trades),
            'completed_trades': len(completed),
            'pending_trades': len(trades) - len(completed),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate_percent': round((len(wins) / len(completed)) * 100, 2) if completed else 0,
            
            # P&L
            'total_pnl_dollars': round(total_pnl, 2),
            'avg_pnl_per_trade': round(avg_pnl, 2),
            
            # By asset class
            'stocks_count': len([t for t in completed if t.asset_class == "stock"]),
            'crypto_count': len([t for t in completed if t.asset_class == "crypto"]),
            'stocks_win_rate': self._calc_win_rate([t for t in completed if t.asset_class == "stock"]),
            'crypto_win_rate': self._calc_win_rate([t for t in completed if t.asset_class == "crypto"]),
            
            # By signal type
            'long_count': len([t for t in completed if t.signal_type == "long"]),
            'short_count': len([t for t in completed if t.signal_type == "short"]),
            'long_win_rate': self._calc_win_rate([t for t in completed if t.signal_type == "long"]),
            'short_win_rate': self._calc_win_rate([t for t in completed if t.signal_type == "short"]),
            
            # Verification
            'all_verified': all(t.verification_hash for t in completed),
            'master_hash': self._create_master_hash(completed),
            
            # Metadata
            'period_days': days,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def get_recent_trades(self, limit: int = 20) -> List[Dict]:
        """Get recent trades for API"""
        trades = self._get_recent_trades(days=7)
        trades.sort(key=lambda t: t.entry_timestamp, reverse=True)
        
        return [
            {
                'id': t.id,
                'symbol': t.symbol,
                'asset_class': t.asset_class,
                'type': t.signal_type,
                'entry_price': t.entry_price,
                'exit_price': t.exit_price,
                'pnl_dollars': round(t.pnl_dollars, 2) if t.pnl_dollars else None,
                'pnl_percent': round(t.pnl_percent, 2) if t.pnl_percent else None,
                'outcome': t.outcome,
                'confidence': t.confidence,
                'entry_time': t.entry_timestamp,
                'verified': bool(t.verification_hash)
            }
            for t in trades[:limit]
        ]
    
    # Storage methods
    def _store_trade(self, trade: Trade):
        """Store trade"""
        if self.redis:
            key = f"{self.namespace}:trade:{trade.id}"
            self.redis.hset(key, mapping={'data': json.dumps(asdict(trade))})
            self.redis.zadd(
                f"{self.namespace}:timeline",
                {trade.id: datetime.fromisoformat(trade.entry_timestamp).timestamp()}
            )
        else:
            self._memory_store[trade.id] = trade
            self._timeline.append((trade.id, trade.entry_timestamp))
    
    def _get_trade(self, trade_id: str) -> Optional[Trade]:
        """Get single trade"""
        if self.redis:
            key = f"{self.namespace}:trade:{trade_id}"
            data = self.redis.hget(key, 'data')
            if data:
                return Trade(**json.loads(data))
        else:
            return self._memory_store.get(trade_id)
        return None
    
    def _get_recent_trades(self, days: int = 30) -> List[Trade]:
        """Get recent trades"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        if self.redis:
            trade_ids = self.redis.zrangebyscore(
                f"{self.namespace}:timeline",
                cutoff.timestamp(),
                '+inf'
            )
            return [self._get_trade(tid.decode()) for tid in trade_ids if self._get_trade(tid.decode())]
        else:
            return [
                t for t in self._memory_store.values()
                if datetime.fromisoformat(t.entry_timestamp) >= cutoff
            ]
    
    def _calc_win_rate(self, trades: List[Trade]) -> float:
        """Calculate win rate"""
        if not trades:
            return 0.0
        wins = [t for t in trades if t.outcome == "win"]
        return round((len(wins) / len(trades)) * 100, 2)
    
    def _create_hash(self, trade: Trade) -> str:
        """Create verification hash"""
        data = f"{trade.id}{trade.symbol}{trade.entry_price}{trade.entry_timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _create_master_hash(self, trades: List[Trade]) -> str:
        """Create master verification hash"""
        hashes = ''.join(sorted([t.verification_hash for t in trades]))
        return hashlib.sha256(hashes.encode()).hexdigest()[:16]
