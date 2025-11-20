"""
Data Source Factory
Provides unified API key resolution and data source initialization utilities
"""
from typing import Dict, Optional, Callable, List
import os
import logging

logger = logging.getLogger(__name__)


class DataSourceFactory:
    """Factory for initializing data sources with unified API key resolution"""

    def __init__(self, get_secret: Optional[Callable], config_api_keys: Dict):
        """
        Initialize factory with secrets manager and config API keys

        Args:
            get_secret: Function to get secrets from AWS Secrets Manager
            config_api_keys: Dictionary of API keys from config.json
        """
        self.get_secret = get_secret
        self.config_api_keys = config_api_keys

    def resolve_api_key(
        self,
        source_name: str,
        secret_keys: List[str],
        env_keys: List[str],
        config_key: str,
        validator: Optional[Callable[[str, str], Optional[str]]] = None,
    ) -> Optional[str]:
        """
        Resolve API key from multiple sources (AWS Secrets → env → config)

        Priority order:
        1. AWS Secrets Manager
        2. Environment variables
        3. config.json

        Args:
            source_name: Name of the data source (for logging)
            secret_keys: List of secret keys to try in AWS Secrets Manager
            env_keys: List of environment variable names to try
            config_key: Key name in config_api_keys dictionary
            validator: Optional function to validate the API key format

        Returns:
            API key if found, None otherwise
        """
        # Try AWS Secrets Manager first
        if self.get_secret:
            for secret_key in secret_keys:
                try:
                    api_key = self.get_secret(secret_key, service="argo")
                    if api_key:
                        logger.debug(
                            f"{source_name} API key found in AWS Secrets Manager"
                        )
                        return api_key
                except Exception as e:
                    logger.debug(
                        f"Failed to get {source_name} key from Secrets Manager: {e}"
                    )

        # Try environment variables
        for env_key in env_keys:
            api_key = os.getenv(env_key)
            if api_key:
                logger.debug(
                    f"{source_name} API key found in environment variable {env_key}"
                )
                return api_key

        # Try config.json
        if config_key and config_key in self.config_api_keys:
            api_key = self.config_api_keys[config_key]
            if api_key:
                if validator:
                    api_key = validator(api_key, source_name)
                if api_key:
                    logger.info(f"✅ {source_name} API key found in config.json")
                    return api_key

        logger.debug(f"{source_name} API key not found in any source")
        return None

    def init_source_safely(
        self, source_name: str, init_func: Callable, *args, **kwargs
    ) -> bool:
        """
        Initialize a data source with error handling

        Args:
            source_name: Name of the data source (for logging)
            init_func: Function to initialize the data source
            *args: Positional arguments for init_func
            **kwargs: Keyword arguments for init_func

        Returns:
            True if initialization succeeded, False otherwise
        """
        try:
            init_func(*args, **kwargs)
            logger.info(f"✅ {source_name} data source initialized")
            return True
        except Exception as e:
            logger.warning(
                f"⚠️  {source_name} init error: {e}", exc_info=True
            )
            return False
