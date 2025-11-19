#!/usr/bin/env python3
"""
Load monitoring configuration from JSON file
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


def load_monitoring_config(config_path: Optional[str] = None) -> Dict:
    """Load monitoring configuration from JSON file"""
    
    if config_path is None:
        # Try to find config file
        project_root = Path(__file__).parent.parent
        config_paths = [
            project_root / "config" / "short_position_monitoring.json",
            project_root / "short_position_monitoring.json",
        ]
        
        for path in config_paths:
            if path.exists():
                config_path = str(path)
                break
    
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")
            return get_default_config()
    else:
        return get_default_config()


def get_default_config() -> Dict:
    """Get default configuration"""
    return {
        "monitoring": {
            "enabled": True,
            "check_interval_seconds": 300,
            "continuous_mode": False
        },
        "alerting": {
            "enabled": True,
            "thresholds": {
                "execution_rate_min": 50.0,
                "short_loss_threshold": -5.0,
                "max_rejected_orders": 3
            }
        },
        "performance_tracking": {
            "enabled": True,
            "report_frequency": "daily",
            "report_time": "09:00",
            "retention_days": 30
        },
        "logging": {
            "log_directory": "logs",
            "log_retention_days": 30,
            "log_level": "INFO"
        }
    }


if __name__ == "__main__":
    config = load_monitoring_config()
    print(json.dumps(config, indent=2))

