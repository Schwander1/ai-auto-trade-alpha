"""
Validation Utilities
Provides request validation, data sanitization, and validation helpers.
"""
from typing import Any, Optional, List, Dict, Callable
from pydantic import BaseModel, ValidationError, validator
from fastapi import HTTPException, status
import re
import logging

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of validation operation"""
    def __init__(self, is_valid: bool, errors: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []

    def __bool__(self):
        return self.is_valid


def validate_email(email: str) -> ValidationResult:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        ValidationResult with validation status and errors
    """
    if not email or not isinstance(email, str):
        return ValidationResult(False, ["Email is required and must be a string"])

    email = email.strip().lower()

    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return ValidationResult(False, ["Invalid email format"])

    if len(email) > 254:  # RFC 5321 limit
        return ValidationResult(False, ["Email address too long (max 254 characters)"])

    return ValidationResult(True)


def validate_symbol(symbol: str) -> ValidationResult:
    """
    Validate trading symbol format.

    Args:
        symbol: Trading symbol to validate

    Returns:
        ValidationResult with validation status and errors
    """
    if not symbol or not isinstance(symbol, str):
        return ValidationResult(False, ["Symbol is required and must be a string"])

    symbol = symbol.strip().upper()

    # Valid symbol format: 1-10 alphanumeric characters, may include hyphens
    if not re.match(r'^[A-Z0-9-]{1,10}$', symbol):
        return ValidationResult(False, ["Invalid symbol format (1-10 alphanumeric characters, hyphens allowed)"])

    return ValidationResult(True)


def validate_pagination_params(limit: int, offset: int, max_limit: int = 500) -> ValidationResult:
    """
    Validate pagination parameters.

    Args:
        limit: Number of items per page
        offset: Number of items to skip
        max_limit: Maximum allowed limit

    Returns:
        ValidationResult with validation status and errors
    """
    errors = []

    if not isinstance(limit, int) or limit < 1:
        errors.append("Limit must be a positive integer")
    elif limit > max_limit:
        errors.append(f"Limit cannot exceed {max_limit}")

    if not isinstance(offset, int) or offset < 0:
        errors.append("Offset must be a non-negative integer")

    if errors:
        return ValidationResult(False, errors)

    return ValidationResult(True)


def validate_confidence(confidence: float, min_confidence: float = 0.0, max_confidence: float = 100.0) -> ValidationResult:
    """
    Validate confidence score.

    Args:
        confidence: Confidence score to validate
        min_confidence: Minimum allowed confidence
        max_confidence: Maximum allowed confidence

    Returns:
        ValidationResult with validation status and errors
    """
    if not isinstance(confidence, (int, float)):
        return ValidationResult(False, ["Confidence must be a number"])

    if confidence < min_confidence or confidence > max_confidence:
        return ValidationResult(
            False,
            [f"Confidence must be between {min_confidence} and {max_confidence}"]
        )

    return ValidationResult(True)


def validate_price(price: float, min_price: float = 0.0) -> ValidationResult:
    """
    Validate price value.

    Args:
        price: Price to validate
        min_price: Minimum allowed price

    Returns:
        ValidationResult with validation status and errors
    """
    if not isinstance(price, (int, float)):
        return ValidationResult(False, ["Price must be a number"])

    if price < min_price:
        return ValidationResult(False, [f"Price must be at least {min_price}"])

    if price > 1e10:  # Reasonable upper limit
        return ValidationResult(False, ["Price is unreasonably high"])

    return ValidationResult(True)


def validate_date_range(start_date: Any, end_date: Any) -> ValidationResult:
    """
    Validate date range.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        ValidationResult with validation status and errors
    """
    from datetime import datetime

    errors = []

    if not isinstance(start_date, datetime):
        errors.append("Start date must be a datetime object")

    if not isinstance(end_date, datetime):
        errors.append("End date must be a datetime object")

    if errors:
        return ValidationResult(False, errors)

    if start_date > end_date:
        return ValidationResult(False, ["Start date must be before end date"])

    # Check for reasonable date range (e.g., not more than 10 years)
    from datetime import timedelta
    max_range = timedelta(days=3650)  # 10 years
    if end_date - start_date > max_range:
        return ValidationResult(False, ["Date range cannot exceed 10 years"])

    return ValidationResult(True)


def sanitize_string(value: Any, max_length: Optional[int] = None, strip: bool = True) -> str:
    """
    Sanitize string input.

    Args:
        value: Value to sanitize
        max_length: Maximum length (truncate if longer)
        strip: Whether to strip whitespace

    Returns:
        Sanitized string
    """
    if value is None:
        return ""

    result = str(value)

    if strip:
        result = result.strip()

    if max_length and len(result) > max_length:
        result = result[:max_length]

    return result


def sanitize_int(value: Any, default: int = 0, min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
    """
    Sanitize integer input.

    Args:
        value: Value to sanitize
        default: Default value if conversion fails
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Sanitized integer
    """
    try:
        result = int(value) if value is not None else default
    except (ValueError, TypeError):
        result = default

    if min_value is not None and result < min_value:
        result = min_value

    if max_value is not None and result > max_value:
        result = max_value

    return result


def sanitize_float(value: Any, default: float = 0.0, min_value: Optional[float] = None, max_value: Optional[float] = None) -> float:
    """
    Sanitize float input.

    Args:
        value: Value to sanitize
        default: Default value if conversion fails
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Sanitized float
    """
    try:
        result = float(value) if value is not None else default
    except (ValueError, TypeError):
        result = default

    if min_value is not None and result < min_value:
        result = min_value

    if max_value is not None and result > max_value:
        result = max_value

    return result


def validate_request_data(data: Dict[str, Any], required_fields: List[str], validators: Optional[Dict[str, Callable]] = None) -> ValidationResult:
    """
    Validate request data against required fields and custom validators.

    Args:
        data: Request data dictionary
        required_fields: List of required field names
        validators: Dictionary mapping field names to validation functions

    Returns:
        ValidationResult with validation status and errors
    """
    errors = []
    validators = validators or {}

    # Check required fields
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"Field '{field}' is required")

    # Run custom validators
    for field, validator_func in validators.items():
        if field in data:
            result = validator_func(data[field])
            if not result.is_valid:
                errors.extend([f"{field}: {error}" for error in result.errors])

    if errors:
        return ValidationResult(False, errors)

    return ValidationResult(True)


def raise_validation_error(errors: List[str], status_code: int = status.HTTP_400_BAD_REQUEST):
    """
    Raise HTTPException with validation errors.

    Args:
        errors: List of error messages
        status_code: HTTP status code

    Raises:
        HTTPException with validation errors
    """
    detail = "; ".join(errors) if len(errors) > 1 else errors[0] if errors else "Validation failed"
    raise HTTPException(status_code=status_code, detail=detail)
