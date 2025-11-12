"""
Performance tracking API endpoints
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Optional
from pydantic import BaseModel
import redis

from argo.tracking import UnifiedPerformanceTracker

router = APIRouter(prefix="/api/performance", tags=["performance"])

# Initialize tracker
try:
    redis_client = redis.Redis(host='redis', port=6379, password='ArgoSecure2025!', decode_responses=False)
    tracker = UnifiedPerformanceTracker(redis_client)
except Exception as e:
    tracker = UnifiedPerformanceTracker()


# Pydantic models for request bodies
class TradeEntry(BaseModel):
    signal_id: str
    asset_class: str
    symbol: str
    signal_type: str
    entry_price: float
    quantity: float = 1.0
    confidence: float = 90.0
    alpaca_order_id: Optional[str] = None
    exchange_order_id: Optional[str] = None


class TradeExit(BaseModel):
    exit_price: float


@router.get("/stats")
async def get_stats(asset_class: Optional[str] = None, days: int = 30):
    """Get performance statistics"""
    try:
        stats = tracker.get_performance_stats(asset_class=asset_class, days=days)
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades/recent")
async def get_recent_trades(limit: int = 20):
    """Get recent trades"""
    try:
        trades = tracker.get_recent_trades(limit=limit)
        return {"success": True, "count": len(trades), "data": trades}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trades/entry")
async def record_entry(trade: TradeEntry):
    """Record trade entry"""
    try:
        recorded_trade = tracker.record_signal_entry(
            signal_id=trade.signal_id,
            asset_class=trade.asset_class,
            symbol=trade.symbol,
            signal_type=trade.signal_type,
            entry_price=trade.entry_price,
            quantity=trade.quantity,
            confidence=trade.confidence,
            alpaca_order_id=trade.alpaca_order_id,
            exchange_order_id=trade.exchange_order_id
        )
        return {
            "success": True,
            "trade_id": recorded_trade.id,
            "message": "Trade entry recorded",
            "verification_hash": recorded_trade.verification_hash
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trades/{trade_id}/exit")
async def record_exit(trade_id: str, exit_data: TradeExit):
    """Record trade exit"""
    try:
        trade = tracker.record_signal_exit(trade_id=trade_id, exit_price=exit_data.exit_price)
        if not trade:
            raise HTTPException(status_code=404, detail="Trade not found")
        
        return {
            "success": True,
            "trade_id": trade.id,
            "outcome": trade.outcome,
            "pnl_dollars": trade.pnl_dollars,
            "pnl_percent": trade.pnl_percent,
            "message": "Trade exit recorded"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Export tracker
__all__ = ['router', 'tracker']
