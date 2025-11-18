"""
External Signal Sync API Endpoint
Receives signals from external signal provider via API and stores them in Alpine Analytics database
Maintains separation: External provider sends via API, Alpine stores in its own database
"""
from fastapi import APIRouter, HTTPException, Depends, Header, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import logging

from backend.core.database import get_db
from backend.core.signal_sync_utils import (
    verify_external_api_key,
    verify_signal_hash,
    check_signal_exists,
    create_signal_from_request
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/external-signals", tags=["external-signals"])


class ExternalSignalRequest(BaseModel):
    """Signal data from external signal provider"""
    signal_id: str
    symbol: str
    action: str  # BUY/SELL
    entry_price: float
    target_price: Optional[float] = None
    stop_price: Optional[float] = None
    stop_loss: Optional[float] = None  # Alias for stop_price
    take_profit: Optional[float] = None  # Alias for target_price
    confidence: float  # 0-100
    strategy: Optional[str] = "weighted_consensus_v6"
    asset_type: Optional[str] = "stock"
    data_source: Optional[str] = "weighted_consensus"
    timestamp: str
    sha256: str
    verification_hash: Optional[str] = None  # Alias for sha256
    reasoning: Optional[str] = None
    regime: Optional[str] = None
    consensus_agreement: Optional[float] = None
    sources_count: Optional[int] = None

    @validator('action')
    def validate_action(cls, v: str) -> str:
        if v.upper() not in ['BUY', 'SELL']:
            raise ValueError('action must be BUY or SELL')
        return v.upper()

    @validator('confidence')
    def validate_confidence(cls, v: float) -> float:
        if not 0 <= v <= 100:
            raise ValueError('confidence must be between 0 and 100')
        return v


@router.post("/sync/signal", status_code=201)
async def receive_external_signal(
    signal_data: ExternalSignalRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_external_api_key)
):
    """
    Receive and store signal from external signal provider

    This endpoint maintains separation:
    - External signal provider sends signals via API
    - Alpine Analytics stores in its own database
    - No direct database access between entities

    **Authentication:**
    - Requires X-API-Key header with valid external signal provider API key

    **Example Request:**
    ```bash
    curl -X POST "http://localhost:9001/api/v1/external-signals/sync/signal" \
         -H "X-API-Key: your-external-signal-api-key" \
         -H "Content-Type: application/json" \
         -d '{
           "signal_id": "SIG-123",
           "symbol": "AAPL",
           "action": "BUY",
           "entry_price": 175.50,
           "confidence": 95.5,
           ...
         }'
    ```
    """
    try:
        # Use verification_hash if provided, otherwise use sha256
        verification_hash = signal_data.verification_hash or signal_data.sha256

        # Check if signal already exists (prevent duplicates)
        existing = check_signal_exists(verification_hash, db)
        if existing:
            logger.debug(f"Signal {verification_hash[:8]} already exists, skipping")
            return {
                "status": "duplicate",
                "message": "Signal already exists",
                "signal_id": existing.id
            }

        # Verify SHA-256 hash matches signal data
        if not verify_signal_hash(signal_data, verification_hash):
            logger.warning(f"Hash verification failed for signal {signal_data.signal_id}")
            raise HTTPException(
                status_code=400,
                detail="Signal hash verification failed"
            )

        # Create signal using shared utility
        signal = create_signal_from_request(signal_data, verification_hash)
        db.add(signal)
        db.commit()
        db.refresh(signal)

        logger.info(f"✅ Signal synced from external provider: {signal_data.symbol} {signal_data.action} ({signal.id})")

        # Broadcast to WebSocket clients (non-blocking)
        try:
            from backend.api.websocket_signals import broadcast_signal_to_websockets
            # Use asyncio.create_task to avoid blocking the response
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(broadcast_signal_to_websockets(signal, db))
                else:
                    loop.run_until_complete(broadcast_signal_to_websockets(signal, db))
            except RuntimeError:
                # No event loop, create new one
                asyncio.run(broadcast_signal_to_websockets(signal, db))
        except Exception as e:
            logger.warning(f"Failed to broadcast signal to WebSocket clients: {e}", exc_info=True)
            # Don't fail the request if WebSocket broadcast fails

        return {
            "status": "success",
            "message": "Signal stored successfully",
            "signal_id": signal.id,
            "alpine_signal_id": signal.id,
            "external_signal_id": signal_data.signal_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error storing signal from external provider: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store signal: {str(e)}"
        )


@router.get("/sync/health")
async def sync_health() -> dict:
    """Health check for external signal sync endpoint"""
    return {
        "status": "healthy",
        "service": "Alpine Analytics - External Signal Sync",
        "endpoint": "/api/v1/external-signals/sync/signal"
    }
