"""
Type Utilities and TypedDict Definitions
Provides type-safe data structures for better code quality and IDE support.
"""

from typing import TypedDict, Optional, List, Dict, Any, Union
from datetime import datetime


class SignalResponseDict(TypedDict, total=False):
    """Type-safe signal response dictionary"""

    id: str
    symbol: str
    action: str
    entry_price: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    confidence: float
    type: str
    timestamp: str
    hash: str
    reasoning: Optional[str]


class PaginatedResponseDict(TypedDict, total=False):
    """Type-safe paginated response dictionary"""

    items: List[Any]
    total: int
    limit: int
    offset: int
    has_more: bool


class UserStatsDict(TypedDict, total=False):
    """Type-safe user statistics dictionary"""

    total_users: int
    active_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    users_by_tier: Dict[str, int]


class SignalStatsDict(TypedDict, total=False):
    """Type-safe signal statistics dictionary"""

    signals_today: int
    signals_this_week: int
    signals_this_month: int
    total_signals: int


class AnalyticsResponseDict(TypedDict, total=False):
    """Type-safe analytics response dictionary"""

    total_users: int
    active_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    users_by_tier: Dict[str, int]
    signals_delivered_today: int
    signals_delivered_this_week: int
    signals_delivered_this_month: int
    api_requests_today: int
    api_requests_this_week: int
    error_rate: float


class ErrorResponseDict(TypedDict):
    """Type-safe error response dictionary"""

    error: str
    detail: str
    status_code: int
    timestamp: str


class ValidationErrorDict(TypedDict):
    """Type-safe validation error dictionary"""

    field: str
    message: str
    value: Any


def ensure_type(value: Any, expected_type: type, default: Any = None) -> Any:
    """
    Ensure value is of expected type, return default if not.

    Args:
        value: Value to check
        expected_type: Expected type
        default: Default value if type doesn't match

    Returns:
        Value if type matches, default otherwise

    Example:
        ```python
        count = ensure_type(request_data.get('count'), int, 10)
        ```
    """
    if isinstance(value, expected_type):
        return value
    if default is not None:
        return default
    raise TypeError(f"Expected {expected_type.__name__}, got {type(value).__name__}")


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int"""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """Safely convert value to string"""
    if value is None:
        return default
    return str(value)


def safe_bool(value: Any, default: bool = False) -> bool:
    """Safely convert value to boolean"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    if isinstance(value, (int, float)):
        return bool(value)
    return default
