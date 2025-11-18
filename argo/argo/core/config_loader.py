#!/usr/bin/env python3
"""
Unified Configuration Loader
Centralized configuration management with clear precedence
"""
import json
import os
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Unified configuration loader with environment-based precedence"""
    
    # Configuration paths in order of precedence (highest to lowest)
    # Note: Current working directory is checked first (before these paths)
    CONFIG_PATHS = {
        'production': [
            '/root/argo-production-prop-firm/config.json',  # Prop firm service
            '/root/argo-production-green/config.json',      # Regular trading (green)
            '/root/argo-production-blue/config.json',       # Regular trading (blue)
            '/root/argo-production/config.json',            # Legacy
        ],
        'development': [
            'config.json',  # Local development
        ]
    }
    
    @staticmethod
    def detect_environment() -> str:
        """Detect current environment"""
        # Check for production paths
        for path in ConfigLoader.CONFIG_PATHS['production']:
            if os.path.exists(path):
                return 'production'
        return 'development'
    
    @staticmethod
    def find_config_file() -> Optional[str]:
        """Find the appropriate config file based on environment"""
        # Check environment variable first (highest priority)
        config_path = os.getenv('ARGO_CONFIG_PATH')
        if config_path and os.path.exists(config_path):
            logger.debug(f"Found config file from ARGO_CONFIG_PATH: {config_path}")
            return config_path
        
        # Check current working directory first (for services running from their deployment directory)
        # This ensures prop firm service loads its own config
        cwd = Path.cwd()
        cwd_config = cwd / 'config.json'
        if cwd_config.exists():
            logger.debug(f"Found config file in current working directory: {cwd_config}")
            return str(cwd_config)
        
        env = ConfigLoader.detect_environment()
        paths = ConfigLoader.CONFIG_PATHS.get(env, ConfigLoader.CONFIG_PATHS['development'])
        
        for path in paths:
            if os.path.exists(path):
                logger.debug(f"Found config file: {path} (environment: {env})")
                return path
        
        # Fallback: try relative path
        relative_path = Path(__file__).parent.parent.parent / 'config.json'
        if relative_path.exists():
            logger.debug(f"Found config file: {relative_path} (relative path)")
            return str(relative_path)
        
        logger.warning("⚠️  No config.json found in any expected path")
        return None
    
    @staticmethod
    def load_config() -> Tuple[Dict, Optional[str]]:
        """Load configuration from appropriate file"""
        config_path = ConfigLoader.find_config_file()
        
        if not config_path:
            return {}, None
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"✅ Loaded config from: {config_path}")
            return config, config_path
        except Exception as e:
            logger.error(f"❌ Error loading config from {config_path}: {e}")
            return {}, None
    
    @staticmethod
    def load_api_keys() -> Dict[str, str]:
        """Load API keys from config.json"""
        config, _ = ConfigLoader.load_config()
        
        api_keys = {
            'massive': config.get('massive', {}).get('api_key'),
            'alpha_vantage': config.get('alpha_vantage', {}).get('api_key'),
            'xai': config.get('xai', {}).get('api_key') or config.get('x_api', {}).get('bearer_token'),
            'sonar': config.get('sonar', {}).get('api_key')
        }
        
        # Filter out None values
        return {k: v for k, v in api_keys.items() if v}

