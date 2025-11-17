"""
External Signal Sync API Endpoint
Receives signals from external signal provider via API and stores them in Alpine Analytics database
Maintains separation: External provider sends via API, Alpine stores in its own database
"""
from fastapi import APIRouter, HTTPException, Depends, Header, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import hashlib
import hmac
import logging
import os

from backend.core.database import get_db
from backend.core.config import settings
from backend.models.signal import Signal
import logging

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
    def validate_action(cls, v):
        if v.upper() not in ['BUY', 'SELL']:
            raise ValueError('action must be BUY or SELL')
        return v.upper()
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('confidence must be between 0 and 100')
        return v


def verify_external_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> bool:
    """
    Verify external signal provider API key for secure signal sync
    Uses HMAC or API key authentication
    """
    # Get API key from settings (AWS Secrets Manager or env)
    expected_key = getattr(settings, 'EXTERNAL_SIGNAL_API_KEY', None)
    if not expected_key:
        # Try to get from secrets manager
        try:
            if hasattr(settings, 'secrets') and settings.secrets:
                expected_key = settings.secrets.get_secret("external-signal-api-key", service="alpine-backend")
        except Exception as e:
            logger.debug(f"Could not get external signal API key from secrets: {e}")
    
    # If no key configured, allow but log warning (for development)
    if not expected_key:
        logger.warning("⚠️  External signal API key not configured - allowing requests (development mode)")
        return True  # Allow in development, require in production
    
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing X-API-Key header"
        )
    
    # Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(x_api_key, expected_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return True


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
        existing = db.query(Signal).filter(
            Signal.verification_hash == verification_hash
        ).first()
        
        if existing:
            logger.debug(f"Signal {verification_hash[:8]} already exists, skipping")
            return {
                "status": "duplicate",
                "message": "Signal already exists",
                "signal_id": existing.id
            }
        
        # Verify SHA-256 hash matches signal data
        hash_fields = {
            'signal_id': signal_data.signal_id,
            'symbol': signal_data.symbol,
            'action': signal_data.action,
            'entry_price': signal_data.entry_price,
            'target_price': signal_data.target_price or signal_data.take_profit,
            'stop_price': signal_data.stop_price or signal_data.stop_loss,
            'confidence': signal_data.confidence,
            'strategy': signal_data.strategy,
            'timestamp': signal_data.timestamp
        }
        
        # Calculate expected hash
        import json
        hash_string = json.dumps(hash_fields, sort_keys=True, default=str)
        expected_hash = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
        
        if verification_hash != expected_hash:
            logger.warning(f"Hash verification failed for signal {signal_data.signal_id}")
            raise HTTPException(
                status_code=400,
                detail="Signal hash verification failed"
            )
        
        # Convert confidence from 0-100 to 0-1 if needed
        confidence = signal_data.confidence
        if confidence > 1:
            confidence = confidence / 100.0
        
        # Parse timestamp
        try:
            timestamp = datetime.fromisoformat(signal_data.timestamp.replace('Z', '+00:00'))
        except Exception:
            timestamp = datetime.utcnow()
        
        # Create signal in Alpine database
        signal = Signal(
            symbol=signal_data.symbol,
            action=signal_data.action,
            price=signal_data.entry_price,
            confidence=confidence,
            target_price=signal_data.target_price or signal_data.take_profit,
            stop_loss=signal_data.stop_price or signal_data.stop_loss,
            rationale=signal_data.reasoning or f"Weighted Consensus v6.0 - {signal_data.strategy}",
            verification_hash=verification_hash,
            is_active=True
        )
        
        db.add(signal)
        db.commit()
        db.refresh(signal)
        
        logger.info(f"✅ Signal synced from external provider: {signal_data.symbol} {signal_data.action} ({signal.id})")
        
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
async def sync_health():
    """Health check for external signal sync endpoint"""
    return {
        "status": "healthy",
        "service": "Alpine Analytics - External Signal Sync",
        "endpoint": "/api/v1/external-signals/sync/signal"
    }

