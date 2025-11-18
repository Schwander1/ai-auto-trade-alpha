#!/usr/bin/env python3
"""
Feature Flag System
Enables gradual rollout and instant rollback of optimizations
Compliance: Rule 31 (Feature Flags)
"""
import os
import json
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class FeatureFlags:
    """Feature flag manager with config file support"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Use same config path detection as ConfigLoader
            from argo.core.config_loader import ConfigLoader
            detected_path = ConfigLoader.find_config_file()
            if detected_path:
                config_path = detected_path
            else:
                config_path = os.getenv('ARGO_CONFIG_PATH', 'argo/config.json')
        
        self.config_path = Path(config_path)
        self.flags: Dict[str, bool] = {}
        self._load_flags()
    
    def _load_flags(self):
        """Load feature flags from config file"""
        try:
            if self.config_path.exists():
                with open(self.config_path) as f:
                    config = json.load(f)
                    self.flags = config.get('feature_flags', {})
            else:
                # Default flags (all disabled)
                self.flags = {
                    'optimized_weights': False,
                    'regime_based_weights': False,
                    'confidence_threshold_88': False,
                    'incremental_confidence': False,
                    'async_batch_db': False,
                    'request_coalescing': False,
                    'frontend_swr': False,
                    'distributed_tracing': False
                }
                self._save_flags()
        except Exception as e:
            logger.error(f"Error loading feature flags: {e}")
            self.flags = {}
    
    def _save_flags(self):
        """Save feature flags to config file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            
            config['feature_flags'] = self.flags
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving feature flags: {e}")
    
    def enable_regime_based_weights(self):
        """Enable regime-based weights feature"""
        self.flags["regime_based_weights"] = True
        logger.info("✅ Regime-based weights enabled")
    
    def is_enabled(self, flag_name: str) -> bool:
        """Check if feature flag is enabled"""
        return self.flags.get(flag_name, False)
    
    def enable(self, flag_name: str):
        """Enable a feature flag"""
        self.flags[flag_name] = True
        self._save_flags()
        logger.info(f"✅ Feature flag enabled: {flag_name}")
    
    def disable(self, flag_name: str):
        """Disable a feature flag"""
        self.flags[flag_name] = False
        self._save_flags()
        logger.warning(f"⚠️  Feature flag disabled: {flag_name}")
    
    def get_all_flags(self) -> Dict[str, bool]:
        """Get all feature flags"""
        return self.flags.copy()

# Global instance
_feature_flags_instance: Optional[FeatureFlags] = None

def get_feature_flags() -> FeatureFlags:
    """Get global feature flags instance"""
    global _feature_flags_instance
    if _feature_flags_instance is None:
        _feature_flags_instance = FeatureFlags()
    return _feature_flags_instance

