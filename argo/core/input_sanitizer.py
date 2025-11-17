"""Input sanitization utilities for Argo API"""
import re
import html
from typing import Any, Optional
from fastapi import HTTPException


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string input
    
    Args:
        value: String to sanitize
        max_length: Maximum length (truncate if longer)
    
    Returns:
        Sanitized string
    
    Raises:
        HTTPException: If value is invalid
    """
    if not isinstance(value, str):
        raise HTTPException(status_code=400, detail="Value must be a string")
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Remove control characters (except newline, tab, carriage return)
    value = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', value)
    
    # HTML escape to prevent XSS
    value = html.escape(value)
    
    # Trim whitespace
    value = value.strip()
    
    # Truncate if too long
    if max_length and len(value) > max_length:
        value = value[:max_length]
    
    return value


def sanitize_symbol(symbol: str) -> str:
    """
    Sanitize trading symbol
    
    Args:
        symbol: Symbol to sanitize
    
    Returns:
        Sanitized symbol (uppercase, alphanumeric and hyphens only)
    
    Raises:
        HTTPException: If symbol is invalid
    """
    if not isinstance(symbol, str):
        raise HTTPException(status_code=400, detail="Symbol must be a string")
    
    # Convert to uppercase
    symbol = symbol.upper().strip()
    
    # Only allow alphanumeric, hyphens, and underscores
    if not re.match(r'^[A-Z0-9_-]+$', symbol):
        raise HTTPException(
            status_code=400,
            detail="Invalid symbol format. Only alphanumeric characters, hyphens, and underscores allowed."
        )
    
    # Limit length
    if len(symbol) > 20:
        raise HTTPException(status_code=400, detail="Symbol too long (max 20 characters)")
    
    return symbol


def sanitize_action(action: str) -> str:
    """
    Sanitize trading action (BUY/SELL)
    
    Args:
        action: Action to sanitize
    
    Returns:
        Sanitized action (uppercase)
    
    Raises:
        HTTPException: If action is invalid
    """
    if not isinstance(action, str):
        raise HTTPException(status_code=400, detail="Action must be a string")
    
    action = action.upper().strip()
    
    if action not in ["BUY", "SELL"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid action. Must be BUY or SELL"
        )
    
    return action


def sanitize_tier(tier: str) -> str:
    """
    Sanitize tier name
    
    Args:
        tier: Tier to sanitize
    
    Returns:
        Sanitized tier (lowercase)
    
    Raises:
        HTTPException: If tier is invalid
    """
    if not isinstance(tier, str):
        raise HTTPException(status_code=400, detail="Tier must be a string")
    
    tier = tier.lower().strip()
    
    valid_tiers = ["starter", "standard", "premium", "professional", "institutional"]
    if tier not in valid_tiers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier. Must be one of: {', '.join(valid_tiers)}"
        )
    
    return tier


def sanitize_integer(value: Any, min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
    """
    Sanitize integer input
    
    Args:
        value: Value to sanitize
        min_value: Minimum allowed value
        max_value: Maximum allowed value
    
    Returns:
        Sanitized integer
    
    Raises:
        HTTPException: If value is invalid
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Value must be an integer")
    
    if min_value is not None and int_value < min_value:
        raise HTTPException(
            status_code=400,
            detail=f"Value must be at least {min_value}"
        )
    
    if max_value is not None and int_value > max_value:
        raise HTTPException(
            status_code=400,
            detail=f"Value must be at most {max_value}"
        )
    
    return int_value


def sanitize_float(value: Any, min_value: Optional[float] = None, max_value: Optional[float] = None) -> float:
    """
    Sanitize float input
    
    Args:
        value: Value to sanitize
        min_value: Minimum allowed value
        max_value: Maximum allowed value
    
    Returns:
        Sanitized float
    
    Raises:
        HTTPException: If value is invalid
    """
    try:
        float_value = float(value)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Value must be a number")
    
    if min_value is not None and float_value < min_value:
        raise HTTPException(
            status_code=400,
            detail=f"Value must be at least {min_value}"
        )
    
    if max_value is not None and float_value > max_value:
        raise HTTPException(
            status_code=400,
            detail=f"Value must be at most {max_value}"
        )
    
    return float_value


def sanitize_path_traversal(path: str) -> str:
    """
    Prevent path traversal attacks
    
    Args:
        path: Path to sanitize
    
    Returns:
        Sanitized path
    
    Raises:
        HTTPException: If path contains traversal sequences
    """
    if not isinstance(path, str):
        raise HTTPException(status_code=400, detail="Path must be a string")
    
    # Check for path traversal sequences
    if '..' in path or path.startswith('/') or '\\' in path:
        raise HTTPException(
            status_code=400,
            detail="Invalid path: path traversal not allowed"
        )
    
    return path

