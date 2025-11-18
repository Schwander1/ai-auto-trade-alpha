"""
Data Transformation Utilities
Provides utilities for transforming data between different formats and structures.
"""
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import json
import pandas as pd
from sqlalchemy.orm import Base


def transform_signal_to_dict(signal: Any, include_metadata: bool = False) -> Dict[str, Any]:
    """
    Transform Signal model to dictionary.

    Args:
        signal: Signal model instance
        include_metadata: Whether to include metadata fields

    Returns:
        Dictionary representation of signal
    """
    # Handle enum serialization
    action_value = signal.action.value if hasattr(signal.action, 'value') else str(signal.action)
    
    data = {
        "id": f"SIG-{signal.id}",
        "symbol": signal.symbol,
        "action": action_value,
        "entry_price": signal.price,
        "stop_loss": signal.stop_loss,
        "take_profit": signal.target_price,
        "confidence": signal.confidence * 100 if signal.confidence <= 1 else signal.confidence,  # Convert 0-1 to 0-100 for API
        "type": "PREMIUM" if (signal.confidence >= 0.85 if signal.confidence <= 1 else signal.confidence >= 85) else "STANDARD",
        "timestamp": signal.created_at.isoformat() if signal.created_at else None,
        "hash": signal.verification_hash,
        "reasoning": signal.rationale
    }

    if include_metadata:
        data.update({
            "is_active": signal.is_active,
            "created_at": signal.created_at.isoformat() if signal.created_at else None,
            "generation_latency_ms": signal.generation_latency_ms,
            "delivery_latency_ms": signal.delivery_latency_ms
        })

    return data


def transform_user_to_dict(user: Any, include_sensitive: bool = False) -> Dict[str, Any]:
    """
    Transform User model to dictionary.

    Args:
        user: User model instance
        include_sensitive: Whether to include sensitive fields (admin only)

    Returns:
        Dictionary representation of user
    """
    data = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "tier": user.tier.value if hasattr(user.tier, 'value') else str(user.tier),
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }

    if include_sensitive:
        data.update({
            "stripe_customer_id": user.stripe_customer_id,
            "stripe_subscription_id": user.stripe_subscription_id,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        })

    return data


def transform_list_to_paginated(
    items: List[Any],
    total: int,
    limit: int,
    offset: int,
    transform_func: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Transform list of items to paginated format.

    Args:
        items: List of items
        total: Total number of items
        limit: Items per page
        offset: Offset for pagination
        transform_func: Optional function to transform each item

    Returns:
        Paginated dictionary
    """
    if transform_func:
        transformed_items = [transform_func(item) for item in items]
    else:
        transformed_items = items

    return {
        "items": transformed_items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total,
        "page": (offset // limit) + 1 if limit > 0 else 1,
        "total_pages": (total + limit - 1) // limit if limit > 0 else 1
    }


def flatten_dict(data: Dict[str, Any], separator: str = "_", prefix: str = "") -> Dict[str, Any]:
    """
    Flatten nested dictionary.

    Args:
        data: Nested dictionary
        separator: Separator for nested keys
        prefix: Prefix for keys

    Returns:
        Flattened dictionary

    Example:
        ```python
        data = {"user": {"name": "John", "age": 30}}
        flatten_dict(data)  # {"user_name": "John", "user_age": 30}
        ```
    """
    items = []
    for key, value in data.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key

        if isinstance(value, dict):
            items.extend(flatten_dict(value, separator, new_key).items())
        else:
            items.append((new_key, value))

    return dict(items)


def nest_dict(data: Dict[str, Any], separator: str = "_") -> Dict[str, Any]:
    """
    Convert flat dictionary to nested dictionary.

    Args:
        data: Flat dictionary
        separator: Separator used in keys

    Returns:
        Nested dictionary

    Example:
        ```python
        data = {"user_name": "John", "user_age": 30}
        nest_dict(data)  # {"user": {"name": "John", "age": 30}}
        ```
    """
    result = {}
    for key, value in data.items():
        parts = key.split(separator)
        current = result

        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        current[parts[-1]] = value

    return result


def filter_dict(data: Dict[str, Any], allowed_keys: List[str]) -> Dict[str, Any]:
    """
    Filter dictionary to only include allowed keys.

    Args:
        data: Dictionary to filter
        allowed_keys: List of allowed keys

    Returns:
        Filtered dictionary
    """
    return {k: v for k, v in data.items() if k in allowed_keys}


def exclude_dict(data: Dict[str, Any], excluded_keys: List[str]) -> Dict[str, Any]:
    """
    Exclude specified keys from dictionary.

    Args:
        data: Dictionary to filter
        excluded_keys: List of keys to exclude

    Returns:
        Filtered dictionary
    """
    return {k: v for k, v in data.items() if k not in excluded_keys}


def convert_to_csv(data: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    """
    Convert list of dictionaries to CSV string.

    Args:
        data: List of dictionaries
        filename: Optional filename (not used, for API compatibility)

    Returns:
        CSV string
    """
    if not data:
        return ""

    df = pd.DataFrame(data)
    return df.to_csv(index=False)


def convert_to_json(data: Any, indent: int = 2) -> str:
    """
    Convert data to JSON string.

    Args:
        data: Data to convert
        indent: JSON indentation

    Returns:
        JSON string
    """
    return json.dumps(data, indent=indent, default=str)


def normalize_data(data: Any, schema: Optional[Dict[str, Any]] = None) -> Any:
    """
    Normalize data according to schema.

    Args:
        data: Data to normalize
        schema: Optional schema definition

    Returns:
        Normalized data
    """
    if schema is None:
        return data

    # Simple normalization - can be extended
    if isinstance(data, dict):
        normalized = {}
        for key, value in data.items():
            if key in schema:
                normalized[key] = normalize_data(value, schema.get(key))
        return normalized

    return data
