"""Helper functions for signal generation to reduce code duplication"""
from datetime import datetime
import hashlib
import json
from typing import Dict, Any, List


def add_signal_metadata(signal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add timestamp and SHA256 hash to a signal
    
    Args:
        signal: Signal dictionary
    
    Returns:
        Signal with metadata added
    """
    signal["timestamp"] = datetime.utcnow().isoformat()
    signal["sha256"] = hashlib.sha256(
        json.dumps(signal, sort_keys=True).encode()
    ).hexdigest()[:16]
    return signal


def add_metadata_to_signals(signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Add metadata to a list of signals
    
    Args:
        signals: List of signal dictionaries
    
    Returns:
        List of signals with metadata added
    """
    return [add_signal_metadata(signal) for signal in signals]


def format_signal_response(
    signals: List[Dict[str, Any]],
    asset_type: str = None,
    additional_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Format signal list into API response format
    
    Args:
        signals: List of signals
        asset_type: Optional asset type (crypto/stocks)
        additional_data: Optional additional response data
    
    Returns:
        Formatted response dictionary
    """
    response = {
        "success": True,
        "count": len(signals),
        "signals": signals
    }
    
    if asset_type:
        response["asset_type"] = asset_type
        if asset_type == "crypto":
            response["trading_24_7"] = True
        elif asset_type == "stocks":
            response["market_hours"] = "9:30 AM - 4:00 PM ET"
    
    if additional_data:
        response.update(additional_data)
    
    return response


# Default signal data (can be moved to database or config)
DEFAULT_CRYPTO_SIGNALS = [
    {"symbol": "BTC-USD", "action": "BUY", "confidence": 96.5, "entry": 67500, "target": 70200, "stop": 66150, "position": "LONG", "reasoning": "Breakout above $67K resistance, institutional buying surge"},
    {"symbol": "ETH-USD", "action": "BUY", "confidence": 94.2, "entry": 3250, "target": 3380, "stop": 3185, "position": "LONG", "reasoning": "ETF inflows accelerating, breaking $3.2K"},
    {"symbol": "SOL-USD", "action": "SELL", "confidence": 91.8, "entry": 145.20, "target": 138.50, "stop": 148.90, "position": "SHORT", "reasoning": "RSI overbought 78, bearish divergence"},
    {"symbol": "AVAX-USD", "action": "BUY", "confidence": 88.5, "entry": 42.30, "target": 45.80, "stop": 41.10, "position": "LONG", "reasoning": "Network upgrade incoming, volume spike"},
    {"symbol": "LINK-USD", "action": "BUY", "confidence": 89.7, "entry": 16.80, "target": 18.20, "stop": 16.30, "position": "LONG", "reasoning": "SWIFT partnership confirmed"}
]

DEFAULT_STOCK_SIGNALS = [
    {"symbol": "AAPL", "action": "BUY", "confidence": 97.2, "entry": 175.50, "target": 184.25, "stop": 171.00, "position": "LONG", "reasoning": "Earnings +12%, iPhone 16 sales exceeding"},
    {"symbol": "NVDA", "action": "BUY", "confidence": 95.8, "entry": 495.10, "target": 520.00, "stop": 485.00, "position": "LONG", "reasoning": "Blackwell chips sold out, AI boom"},
    {"symbol": "TSLA", "action": "SELL", "confidence": 93.1, "entry": 242.30, "target": 230.50, "stop": 248.00, "position": "SHORT", "reasoning": "Q4 deliveries miss, China competition"},
    {"symbol": "MSFT", "action": "BUY", "confidence": 92.4, "entry": 378.20, "target": 395.00, "stop": 370.00, "position": "LONG", "reasoning": "Azure +28%, Copilot momentum"},
    {"symbol": "GOOGL", "action": "BUY", "confidence": 90.3, "entry": 142.80, "target": 150.00, "stop": 139.50, "position": "LONG", "reasoning": "AI search gaining share"}
]

