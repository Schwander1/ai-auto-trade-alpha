"""
Configuration Management Utilities
Provides utilities for managing configuration, environment variables, and settings.
"""
import os
from typing import Optional, Dict, Any, List
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


def load_config_from_file(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(path, 'r') as f:
        return json.load(f)


def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get environment variable with validation.

    Args:
        key: Environment variable key
        default: Default value if not set
        required: Whether variable is required

    Returns:
        Environment variable value

    Raises:
        ValueError: If required variable is not set
    """
    value = os.getenv(key, default)

    if required and value is None:
        raise ValueError(f"Required environment variable not set: {key}")

    return value


def get_env_bool(key: str, default: bool = False) -> bool:
    """
    Get boolean environment variable.

    Args:
        key: Environment variable key
        default: Default value

    Returns:
        Boolean value
    """
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')


def get_env_int(key: str, default: int = 0) -> int:
    """
    Get integer environment variable.

    Args:
        key: Environment variable key
        default: Default value

    Returns:
        Integer value
    """
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        logger.warning(f"Invalid integer value for {key}, using default: {default}")
        return default


def get_env_float(key: str, default: float = 0.0) -> float:
    """
    Get float environment variable.

    Args:
        key: Environment variable key
        default: Default value

    Returns:
        Float value
    """
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        logger.warning(f"Invalid float value for {key}, using default: {default}")
        return default


def get_env_list(key: str, separator: str = ",", default: Optional[List[str]] = None) -> List[str]:
    """
    Get list from environment variable (comma-separated).

    Args:
        key: Environment variable key
        separator: Separator character
        default: Default list value

    Returns:
        List of strings
    """
    value = os.getenv(key)
    if value is None:
        return default or []

    return [item.strip() for item in value.split(separator) if item.strip()]


def validate_config(config: Dict[str, Any], required_keys: List[str]) -> bool:
    """
    Validate configuration has required keys.

    Args:
        config: Configuration dictionary
        required_keys: List of required keys

    Returns:
        True if all required keys are present

    Raises:
        ValueError: If required keys are missing
    """
    missing_keys = [key for key in required_keys if key not in config or config[key] is None]

    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")

    return True


def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple configuration dictionaries (later configs override earlier ones).

    Args:
        *configs: Configuration dictionaries to merge

    Returns:
        Merged configuration dictionary
    """
    merged = {}
    for config in configs:
        merged.update(config)
    return merged


def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get configuration value using dot notation path.

    Args:
        config: Configuration dictionary
        key_path: Dot-separated key path (e.g., "database.host")
        default: Default value if key not found

    Returns:
        Configuration value or default

    Example:
        ```python
        config = {"database": {"host": "localhost", "port": 5432}}
        get_config_value(config, "database.host")  # "localhost"
        get_config_value(config, "database.ssl", False)  # False
        ```
    """
    keys = key_path.split(".")
    value = config

    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default

    return value


def set_config_value(config: Dict[str, Any], key_path: str, value: Any) -> None:
    """
    Set configuration value using dot notation path.

    Args:
        config: Configuration dictionary
        key_path: Dot-separated key path
        value: Value to set

    Example:
        ```python
        config = {}
        set_config_value(config, "database.host", "localhost")
        # config = {"database": {"host": "localhost"}}
        ```
    """
    keys = key_path.split(".")
    current = config

    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    current[keys[-1]] = value
