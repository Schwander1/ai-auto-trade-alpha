"""
Security Utilities
Provides security-related utilities for authentication, authorization, and security checks.
"""
import hashlib
import hmac
import secrets
import re
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.

    Args:
        length: Token length in bytes (default: 32)

    Returns:
        Hex-encoded secure token
    """
    return secrets.token_hex(length)


def hash_value(value: str, algorithm: str = "sha256") -> str:
    """
    Hash a value using specified algorithm.

    Args:
        value: Value to hash
        algorithm: Hash algorithm (sha256, sha512, md5)

    Returns:
        Hex-encoded hash
    """
    if algorithm == "sha256":
        return hashlib.sha256(value.encode()).hexdigest()
    elif algorithm == "sha512":
        return hashlib.sha512(value.encode()).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(value.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def verify_hash(value: str, hash_value: str, algorithm: str = "sha256") -> bool:
    """
    Verify a value against a hash.

    Args:
        value: Value to verify
        hash_value: Hash to compare against
        algorithm: Hash algorithm

    Returns:
        True if hash matches, False otherwise
    """
    computed_hash = hash_value(value, algorithm)
    return hmac.compare_digest(computed_hash, hash_value)


def generate_hmac_signature(message: str, secret: str, algorithm: str = "sha256") -> str:
    """
    Generate HMAC signature for message.

    Args:
        message: Message to sign
        secret: Secret key
        algorithm: Hash algorithm

    Returns:
        Hex-encoded HMAC signature
    """
    if algorithm == "sha256":
        return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    elif algorithm == "sha512":
        return hmac.new(secret.encode(), message.encode(), hashlib.sha512).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def verify_hmac_signature(message: str, signature: str, secret: str, algorithm: str = "sha256") -> bool:
    """
    Verify HMAC signature.

    Args:
        message: Original message
        signature: Signature to verify
        secret: Secret key
        algorithm: Hash algorithm

    Returns:
        True if signature is valid, False otherwise
    """
    expected_signature = generate_hmac_signature(message, secret, algorithm)
    return hmac.compare_digest(expected_signature, signature)


def is_strong_password(password: str, min_length: int = 8) -> tuple[bool, Optional[str]]:
    """
    Check if password meets strength requirements.

    Args:
        password: Password to check
        min_length: Minimum password length

    Returns:
        Tuple of (is_strong, error_message)
    """
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    # Check for common weak passwords
    common_passwords = ["password", "12345678", "qwerty", "abc123"]
    if password.lower() in common_passwords:
        return False, "Password is too common"

    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename
    """
    # Remove path separators
    filename = filename.replace("/", "").replace("\\", "")

    # Remove null bytes
    filename = filename.replace("\x00", "")

    # Remove leading dots
    filename = filename.lstrip(".")

    # Limit length
    if len(filename) > 255:
        filename = filename[:255]

    return filename


def check_rate_limit_key(key: str, max_length: int = 100) -> bool:
    """
    Validate rate limit key format.

    Args:
        key: Rate limit key
        max_length: Maximum key length

    Returns:
        True if key is valid, False otherwise
    """
    if not key or len(key) > max_length:
        return False

    # Only allow alphanumeric, hyphens, underscores, and colons
    if not re.match(r'^[a-zA-Z0-9_\-:]+$', key):
        return False

    return True


def generate_csrf_token() -> str:
    """
    Generate CSRF token.

    Returns:
        Secure CSRF token
    """
    return generate_secure_token(32)


def validate_csrf_token(token: str, expected_token: str) -> bool:
    """
    Validate CSRF token.

    Args:
        token: Token to validate
        expected_token: Expected token value

    Returns:
        True if token is valid, False otherwise
    """
    if not token or not expected_token:
        return False

    return hmac.compare_digest(token, expected_token)


def check_ip_whitelist(ip: str, whitelist: list[str]) -> bool:
    """
    Check if IP address is in whitelist.

    Args:
        ip: IP address to check
        whitelist: List of allowed IP addresses or CIDR blocks

    Returns:
        True if IP is whitelisted, False otherwise
    """
    if not whitelist:
        return True  # No whitelist = allow all

    # Simple IP matching (for exact matches)
    if ip in whitelist:
        return True

    # TODO: Add CIDR block matching if needed
    # For now, only exact matches are supported

    return False


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """
    Mask sensitive data (e.g., API keys, tokens).

    Args:
        data: Data to mask
        mask_char: Character to use for masking
        visible_chars: Number of characters to keep visible at start and end

    Returns:
        Masked data string
    """
    if not data or len(data) <= visible_chars * 2:
        return mask_char * len(data) if data else ""

    visible_start = data[:visible_chars]
    visible_end = data[-visible_chars:]
    masked_middle = mask_char * (len(data) - visible_chars * 2)

    return f"{visible_start}{masked_middle}{visible_end}"
