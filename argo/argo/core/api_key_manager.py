#!/usr/bin/env python3
"""
Unified API Key Management
Centralized API key resolution with clear precedence and validation
"""
import os
import logging
from typing import Optional, Dict, Callable, List
from argo.core.config_loader import ConfigLoader

logger = logging.getLogger(__name__)

class APIKeyManager:
    """Unified API key manager with precedence: AWS Secrets > Env > Config"""
    
    def __init__(self, get_secret_func: Optional[Callable] = None):
        self.get_secret = get_secret_func
        self.config_keys = ConfigLoader.load_api_keys()
    
    def resolve_key(
        self,
        source_name: str,
        secret_keys: List[str],
        env_keys: List[str],
        config_key: str,
        validator: Optional[Callable] = None
    ) -> Optional[str]:
        """
        Resolve API key with precedence:
        1. AWS Secrets Manager (if available)
        2. Environment variables
        3. Config.json
        
        Args:
            source_name: Name of the data source
            secret_keys: List of secret keys to try in AWS Secrets Manager
            env_keys: List of environment variable names to try
            config_key: Key name in config.json
            validator: Optional validation function
        
        Returns:
            API key string or None if not found
        """
        # Try AWS Secrets Manager first
        if self.get_secret:
            for secret_key in secret_keys:
                try:
                    api_key = self.get_secret(secret_key, service="argo")
                    if api_key:
                        if validator:
                            api_key = validator(api_key, source_name)
                        if api_key:
                            logger.debug(f"{source_name} API key found in AWS Secrets Manager: {secret_key}")
                            return api_key
                except Exception as e:
                    logger.debug(f"Error checking AWS secret {secret_key}: {e}")
        
        # Try environment variables
        for env_key in env_keys:
            api_key = os.getenv(env_key)
            if api_key:
                if validator:
                    api_key = validator(api_key, source_name)
                if api_key:
                    logger.debug(f"{source_name} API key found in environment variable: {env_key}")
                    return api_key
        
        # Try config.json (with special handling for Massive to prefer config)
        if config_key and config_key in self.config_keys:
            api_key = self.config_keys[config_key]
            if api_key:
                if validator:
                    api_key = validator(api_key, source_name)
                if api_key:
                    logger.info(f"✅ {source_name} API key found in config.json")
                    return api_key
        
        logger.warning(f"⚠️  {source_name} API key not found in any source")
        return None
    
    def resolve_key_prefer_config(
        self,
        source_name: str,
        config_key: str,
        secret_keys: List[str],
        env_keys: List[str],
        validator: Optional[Callable] = None
    ) -> Optional[str]:
        """
        Resolve API key with config.json preferred (for sources like Massive)
        Precedence: Config.json > AWS Secrets > Env
        """
        # Try config.json first
        if config_key and config_key in self.config_keys:
            api_key = self.config_keys[config_key]
            if api_key:
                if validator:
                    api_key = validator(api_key, source_name)
                if api_key:
                    logger.info(f"✅ {source_name} API key found in config.json (preferred)")
                    return api_key
        
        # Fallback to standard resolution
        return self.resolve_key(source_name, secret_keys, env_keys, config_key, validator)

