"""
Shared utility functions
"""

from .logger import (
    StructuredLogger,
    JSONFormatter,
    LogLevel,
    logger,
    debug,
    info,
    warn,
    error,
)

# Import secrets_manager if available
try:
    from .secrets_manager import (
        SecretsManager,
        get_secrets_manager,
        get_secret,
    )
    __all__ = [
        "StructuredLogger",
        "JSONFormatter",
        "LogLevel",
        "logger",
        "debug",
        "info",
        "warn",
        "error",
        "SecretsManager",
        "get_secrets_manager",
        "get_secret",
    ]
except ImportError:
    __all__ = [
        "StructuredLogger",
        "JSONFormatter",
        "LogLevel",
        "logger",
        "debug",
        "info",
        "warn",
        "error",
    ]

