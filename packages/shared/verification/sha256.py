"""
SHA-256 verification utilities for trading signals
Ensures signal integrity and authenticity

PATENT-PENDING TECHNOLOGY
Patent Application: [Application Number]
Filing Date: [Date]

This code implements patent-pending technology.
Unauthorized use may infringe on pending patent rights.

PATENT CLAIM: SHA-256 Signal Verification
Each trading signal is cryptographically verified using SHA-256 hashing 
to ensure data integrity and tamper detection.
See: docs/PATENT_CLAIM_MAPPING.md for patent details
"""

import hashlib
import json
from typing import Dict, Any, List
from datetime import datetime

from .signal import Signal, SignalVerification


def generate_signal_hash(signal_data: Dict[str, Any]) -> str:
    """
    Generate SHA-256 hash of signal data
    
    Args:
        signal_data: Signal dictionary (without hash field)
    
    Returns:
        Hex-encoded SHA-256 hash
    """
    # Create a deterministic string representation
    # Only include fields that should be part of the hash
    hash_fields = {
        'id': signal_data.get('id'),
        'symbol': signal_data.get('symbol'),
        'action': signal_data.get('action'),
        'entry_price': signal_data.get('entry_price'),
        'stop_loss': signal_data.get('stop_loss'),
        'take_profit': signal_data.get('take_profit'),
        'confidence': signal_data.get('confidence'),
        'timestamp': signal_data.get('timestamp'),
    }
    
    # Convert to JSON string (sorted keys for determinism)
    signal_json = json.dumps(hash_fields, sort_keys=True, default=str)
    
    # Generate SHA-256 hash
    return hashlib.sha256(signal_json.encode('utf-8')).hexdigest()


def verify_signal_hash(signal: Signal) -> SignalVerification:
    """
    Verify signal hash
    
    Args:
        signal: Signal object with hash to verify
    
    Returns:
        SignalVerification object with result
    """
    try:
        # Convert signal to dict and remove hash
        signal_dict = signal.dict(exclude={'hash'})
        
        # Generate expected hash
        expected_hash = generate_signal_hash(signal_dict)
        
        # Compare hashes
        is_valid = expected_hash == signal.hash
        
        return SignalVerification(
            isValid=is_valid,
            verifiedAt=datetime.utcnow(),
            error=None if is_valid else "Hash mismatch"
        )
    except Exception as e:
        return SignalVerification(
            isValid=False,
            verifiedAt=datetime.utcnow(),
            error=str(e)
        )


def verify_signals(signals: List[Signal]) -> List[SignalVerification]:
    """
    Verify multiple signals
    
    Args:
        signals: List of Signal objects to verify
    
    Returns:
        List of SignalVerification objects
    """
    return [verify_signal_hash(signal) for signal in signals]

