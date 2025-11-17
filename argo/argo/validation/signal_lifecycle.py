"""
Signal Lifecycle Tracking
Tracks signals from generation through execution or skip
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import redis
except ImportError:
    redis = None


class SignalStatus(Enum):
    """Signal lifecycle status"""
    GENERATED = "generated"
    EXECUTED = "executed"
    SKIPPED = "skipped"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class SignalLifecycle:
    """Tracks signal through its lifecycle"""
    signal_id: str
    symbol: str
    action: str
    entry_price: float
    confidence: float
    regime: Optional[str]
    status: str
    generated_at: str
    executed_at: Optional[str] = None
    skipped_at: Optional[str] = None
    skip_reason: Optional[str] = None
    trade_id: Optional[str] = None
    expired_at: Optional[str] = None
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()


class SignalLifecycleTracker:
    """
    Tracks signal lifecycle from generation to execution or skip
    """
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.namespace = "argo:lifecycle"
        
        if not self.redis:
            self._memory_store = {}
            print("⚠️  Using in-memory storage for signal lifecycle (Redis not available)")
    
    def record_signal_generated(
        self,
        signal_id: str,
        symbol: str,
        action: str,
        entry_price: float,
        confidence: float,
        regime: Optional[str] = None
    ) -> SignalLifecycle:
        """Record signal generation"""
        lifecycle = SignalLifecycle(
            signal_id=signal_id,
            symbol=symbol,
            action=action,
            entry_price=entry_price,
            confidence=confidence,
            regime=regime,
            status=SignalStatus.GENERATED.value,
            generated_at=datetime.utcnow().isoformat()
        )
        
        self._store_lifecycle(lifecycle)
        return lifecycle
    
    def record_signal_executed(
        self,
        signal_id: str,
        trade_id: str
    ) -> Optional[SignalLifecycle]:
        """Record signal execution"""
        lifecycle = self._get_lifecycle(signal_id)
        if not lifecycle:
            return None
        
        lifecycle.status = SignalStatus.EXECUTED.value
        lifecycle.executed_at = datetime.utcnow().isoformat()
        lifecycle.trade_id = trade_id
        
        self._store_lifecycle(lifecycle)
        return lifecycle
    
    def record_signal_skipped(
        self,
        signal_id: str,
        reason: str
    ) -> Optional[SignalLifecycle]:
        """Record signal skip"""
        lifecycle = self._get_lifecycle(signal_id)
        if not lifecycle:
            # Create new lifecycle if signal wasn't tracked
            lifecycle = SignalLifecycle(
                signal_id=signal_id,
                symbol="unknown",
                action="unknown",
                entry_price=0.0,
                confidence=0.0,
                regime=None,
                status=SignalStatus.SKIPPED.value,
                generated_at=datetime.utcnow().isoformat()
            )
        
        lifecycle.status = SignalStatus.SKIPPED.value
        lifecycle.skipped_at = datetime.utcnow().isoformat()
        lifecycle.skip_reason = reason
        
        self._store_lifecycle(lifecycle)
        return lifecycle
    
    def record_signal_expired(
        self,
        signal_id: str
    ) -> Optional[SignalLifecycle]:
        """Record signal expiration"""
        lifecycle = self._get_lifecycle(signal_id)
        if not lifecycle:
            return None
        
        lifecycle.status = SignalStatus.EXPIRED.value
        lifecycle.expired_at = datetime.utcnow().isoformat()
        
        self._store_lifecycle(lifecycle)
        return lifecycle
    
    def get_conversion_stats(
        self,
        period_days: int = 30
    ) -> Dict:
        """Get signal-to-trade conversion statistics"""
        lifecycles = self._get_recent_lifecycles(days=period_days)
        
        total_generated = len(lifecycles)
        executed = len([l for l in lifecycles if l.status == SignalStatus.EXECUTED.value])
        skipped = len([l for l in lifecycles if l.status == SignalStatus.SKIPPED.value])
        expired = len([l for l in lifecycles if l.status == SignalStatus.EXPIRED.value])
        
        conversion_rate = (executed / total_generated * 100) if total_generated > 0 else 0
        
        # Group skip reasons
        skip_reasons = {}
        for lifecycle in lifecycles:
            if lifecycle.skip_reason:
                skip_reasons[lifecycle.skip_reason] = skip_reasons.get(lifecycle.skip_reason, 0) + 1
        
        return {
            "total_signals": total_generated,
            "executed": executed,
            "skipped": skipped,
            "expired": expired,
            "conversion_rate": round(conversion_rate, 2),
            "skip_reasons": skip_reasons,
            "period_days": period_days
        }
    
    def _store_lifecycle(self, lifecycle: SignalLifecycle):
        """Store lifecycle"""
        if self.redis:
            key = f"{self.namespace}:signal:{lifecycle.signal_id}"
            self.redis.hset(key, mapping={'data': json.dumps(asdict(lifecycle))})
            self.redis.zadd(
                f"{self.namespace}:timeline",
                {lifecycle.signal_id: datetime.fromisoformat(lifecycle.generated_at).timestamp()}
            )
        else:
            self._memory_store[lifecycle.signal_id] = lifecycle
    
    def _get_lifecycle(self, signal_id: str) -> Optional[SignalLifecycle]:
        """Get lifecycle by signal ID"""
        if self.redis:
            key = f"{self.namespace}:signal:{signal_id}"
            data = self.redis.hget(key, 'data')
            if data:
                return SignalLifecycle(**json.loads(data))
        else:
            return self._memory_store.get(signal_id)
        return None
    
    def _get_recent_lifecycles(self, days: int = 30) -> List[SignalLifecycle]:
        """Get recent lifecycles"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        if self.redis:
            signal_ids = self.redis.zrangebyscore(
                f"{self.namespace}:timeline",
                cutoff.timestamp(),
                '+inf'
            )
            return [self._get_lifecycle(sid.decode()) for sid in signal_ids if self._get_lifecycle(sid.decode())]
        else:
            return [
                l for l in self._memory_store.values()
                if datetime.fromisoformat(l.generated_at) >= cutoff
            ]

