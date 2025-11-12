"""Input sanitization utilities"""
import re
import html
from typing import Any, Optional
from pydantic import BaseModel


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string input
    
    Args:
        value: String to sanitize
        max_length: Maximum length (truncate if longer)
    
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)
    
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


def sanitize_email(email: str) -> str:
    """
    Sanitize email address
    
    Args:
        email: Email to sanitize
    
    Returns:
        Sanitized email
    """
    if not isinstance(email, str):
        raise ValueError("Email must be a string")
    
    # Remove whitespace and convert to lowercase
    email = email.strip().lower()
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    
    # Limit length
    if len(email) > 254:  # RFC 5321 limit
        raise ValueError("Email address too long")
    
    return email


def sanitize_symbol(symbol: str) -> str:
    """
    Sanitize trading symbol
    
    Args:
        symbol: Symbol to sanitize
    
    Returns:
        Sanitized symbol (uppercase, alphanumeric and hyphens only)
    """
    if not isinstance(symbol, str):
        raise ValueError("Symbol must be a string")
    
    # Convert to uppercase
    symbol = symbol.upper().strip()
    
    # Only allow alphanumeric, hyphens, and underscores
    if not re.match(r'^[A-Z0-9_-]+$', symbol):
        raise ValueError("Invalid symbol format. Only alphanumeric characters, hyphens, and underscores allowed.")
    
    # Limit length
    if len(symbol) > 20:
        raise ValueError("Symbol too long")
    
    return symbol


def sanitize_action(action: str) -> str:
    """
    Sanitize trading action (BUY/SELL)
    
    Args:
        action: Action to sanitize
    
    Returns:
        Sanitized action (BUY or SELL)
    """
    if not isinstance(action, str):
        raise ValueError("Action must be a string")
    
    action = action.upper().strip()
    
    if action not in ["BUY", "SELL"]:
        raise ValueError("Invalid action. Must be BUY or SELL")
    
    return action


def sanitize_tier(tier: str) -> str:
    """
    Sanitize user tier
    
    Args:
        tier: Tier to sanitize
    
    Returns:
        Sanitized tier (lowercase)
    """
    if not isinstance(tier, str):
        raise ValueError("Tier must be a string")
    
    tier = tier.lower().strip()
    
    valid_tiers = ["starter", "pro", "elite"]
    if tier not in valid_tiers:
        raise ValueError(f"Invalid tier. Must be one of: {', '.join(valid_tiers)}")
    
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
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValueError("Invalid integer value")
    
    if min_value is not None and int_value < min_value:
        raise ValueError(f"Value must be at least {min_value}")
    
    if max_value is not None and int_value > max_value:
        raise ValueError(f"Value must be at most {max_value}")
    
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
    """
    try:
        float_value = float(value)
    except (ValueError, TypeError):
        raise ValueError("Invalid float value")
    
    if min_value is not None and float_value < min_value:
        raise ValueError(f"Value must be at least {min_value}")
    
    if max_value is not None and float_value > max_value:
        raise ValueError(f"Value must be at most {max_value}")
    
    # Check for NaN or Infinity
    if not (float('-inf') < float_value < float('inf')):
        raise ValueError("Value must be a finite number")
    
    return float_value


def sanitize_path_traversal(path: str) -> str:
    """
    Prevent path traversal attacks
    
    Args:
        path: Path to sanitize
    
    Returns:
        Sanitized path
    """
    if not isinstance(path, str):
        raise ValueError("Path must be a string")
    
    # Remove path traversal sequences
    path = path.replace('..', '').replace('//', '/')
    
    # Remove leading slashes
    path = path.lstrip('/')
    
    # Only allow alphanumeric, hyphens, underscores, dots, and slashes
    if not re.match(r'^[a-zA-Z0-9._/-]+$', path):
        raise ValueError("Invalid path format")
    
    return path

