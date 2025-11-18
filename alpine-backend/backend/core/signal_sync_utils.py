"""
Shared utilities for signal synchronization endpoints
Used by both argo_sync.py and external_signal_sync.py
"""
from fastapi import HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional, Any
from datetime import datetime
import hashlib
import hmac
import json
import logging

from backend.core.config import settings
from backend.models.signal import Signal, SignalAction

logger = logging.getLogger(__name__)


def verify_external_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> bool:
    """
    Verify external signal provider API key for secure signal sync
    Uses HMAC or API key authentication

    Shared utility function for both argo_sync and external_signal_sync endpoints
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


def verify_signal_hash(signal_data: Any, verification_hash: str) -> bool:
    """
    Verify SHA-256 hash matches signal data

    Args:
        signal_data: ExternalSignalRequest object
        verification_hash: Expected hash value

    Returns:
        True if hash matches, False otherwise
    """
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
    hash_string = json.dumps(hash_fields, sort_keys=True, default=str)
    expected_hash = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()

    return verification_hash == expected_hash


def normalize_confidence(confidence: float) -> float:
    """
    Normalize confidence from 0-100 to 0-1 if needed

    Args:
        confidence: Confidence value (0-100 or 0-1)

    Returns:
        Normalized confidence (0-1)
    """
    if confidence > 1:
        return confidence / 100.0
    return confidence


def parse_signal_timestamp(timestamp_str: str) -> datetime:
    """
    Parse timestamp string to datetime object with fallback

    Args:
        timestamp_str: ISO format timestamp string

    Returns:
        datetime object (UTC)
    """
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except Exception:
        return datetime.utcnow()


def create_signal_from_request(signal_data: Any, verification_hash: str) -> Signal:
    """
    Create Signal model instance from ExternalSignalRequest

    Args:
        signal_data: ExternalSignalRequest object
        verification_hash: Verification hash for the signal

    Returns:
        Signal model instance (not yet committed)
    """
    # Normalize confidence
    confidence = normalize_confidence(signal_data.confidence)

    # Convert action string to enum
    try:
        action_enum = SignalAction[signal_data.action.upper()]
    except (KeyError, AttributeError):
        raise ValueError(f"Invalid action: {signal_data.action}. Must be BUY or SELL")
    
    # Create signal in Alpine database
    signal = Signal(
        symbol=signal_data.symbol,
        action=action_enum,
        price=signal_data.entry_price,
        confidence=confidence,
        target_price=signal_data.target_price or signal_data.take_profit,
        stop_loss=signal_data.stop_price or signal_data.stop_loss,
        rationale=signal_data.reasoning or f"Weighted Consensus v6.0 - {signal_data.strategy}",
        verification_hash=verification_hash,
        is_active=True
    )

    return signal


def check_signal_exists(verification_hash: str, db: Session) -> Optional[Signal]:
    """
    Check if signal with given verification hash already exists

    Args:
        verification_hash: Signal verification hash
        db: Database session

    Returns:
        Existing Signal if found, None otherwise
    """
    return db.query(Signal).filter(
        Signal.verification_hash == verification_hash
    ).first()
