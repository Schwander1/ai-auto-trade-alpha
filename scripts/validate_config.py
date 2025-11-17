#!/usr/bin/env python3
"""
Config validation script for Argo Trading Engine
Validates config.json structure and values before deployment
"""

import json
import sys
import os
from pathlib import Path


def validate_config(config_path):
    """Validate config.json structure and values"""
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading config file: {e}")
        return False
    
    errors = []
    warnings = []
    
    # Validate Massive API key
    massive_config = config.get('massive', {})
    massive_key = massive_config.get('api_key', '')
    if not massive_key:
        errors.append("Missing massive.api_key")
    elif len(massive_key) != 32:
        errors.append(f"Invalid massive.api_key length: {len(massive_key)} (expected 32)")
        warnings.append(f"Massive API key should be 32 characters, got {len(massive_key)}")
    
    # Validate Alpha Vantage API key
    alpha_vantage_config = config.get('alpha_vantage', {})
    alpha_vantage_key = alpha_vantage_config.get('api_key', '')
    if not alpha_vantage_key:
        errors.append("Missing alpha_vantage.api_key")
    
    # Validate X API bearer token
    x_api_config = config.get('x_api', {})
    x_api_token = x_api_config.get('bearer_token', '')
    if not x_api_token:
        errors.append("Missing x_api.bearer_token")
    
    # Validate Sonar API key
    sonar_config = config.get('sonar', {})
    sonar_key = sonar_config.get('api_key', '')
    if not sonar_key:
        errors.append("Missing sonar.api_key")
    
    # Validate XAI API key
    xai_config = config.get('xai', {})
    xai_key = xai_config.get('api_key', '')
    if not xai_key:
        errors.append("Missing xai.api_key")
    
    # Validate Alpaca configuration
    alpaca_config = config.get('alpaca', {})
    if not alpaca_config:
        errors.append("Missing alpaca configuration")
    else:
        prod_config = alpaca_config.get('production', {})
        if not prod_config:
            errors.append("Missing alpaca.production configuration")
        else:
            if not prod_config.get('api_key'):
                errors.append("Missing alpaca.production.api_key")
            if not prod_config.get('secret_key'):
                errors.append("Missing alpaca.production.secret_key")
    
    # Validate strategy configuration
    strategy_config = config.get('strategy', {})
    if not strategy_config:
        errors.append("Missing strategy configuration")
    else:
        weights = [
            strategy_config.get('weight_massive', 0),
            strategy_config.get('weight_alpha_vantage', 0),
            strategy_config.get('weight_x_sentiment', 0),
            strategy_config.get('weight_sonar', 0)
        ]
        total_weight = sum(weights)
        if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
            warnings.append(f"Strategy weights sum to {total_weight:.2f} (expected 1.0)")
    
    # Validate trading configuration
    trading_config = config.get('trading', {})
    if not trading_config:
        errors.append("Missing trading configuration")
    else:
        min_confidence = trading_config.get('min_confidence', 0)
        if min_confidence < 0 or min_confidence > 100:
            errors.append(f"Invalid min_confidence: {min_confidence} (must be 0-100)")
    
    # Print results
    if warnings:
        print("⚠️  Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if errors:
        print("❌ Config validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ Config validation passed")
    return True


if __name__ == "__main__":
    # Default to argo/config.json if no argument provided
    config_path = sys.argv[1] if len(sys.argv) > 1 else "argo/config.json"
    
    # Resolve path relative to script directory
    script_dir = Path(__file__).parent.parent
    config_path = script_dir / config_path
    
    success = validate_config(str(config_path))
    sys.exit(0 if success else 1)


