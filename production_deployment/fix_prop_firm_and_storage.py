#!/usr/bin/env python3
"""
Fix prop firm configuration and signal storage issues
"""
import json
import sys
import os

def fix_configs():
    # Fix Argo production config
    argo_config_path = "/root/argo-production-green/config.json"
    if os.path.exists(argo_config_path):
        with open(argo_config_path, 'r') as f:
            config = json.load(f)
        
        # Ensure prop_firm is properly configured (but not enabled for main service)
        if "prop_firm" not in config:
            config["prop_firm"] = {}
        config["prop_firm"]["enabled"] = False  # Main service should not be in prop firm mode
        
        # Ensure trading settings
        if "trading" not in config:
            config["trading"] = {}
        config["trading"]["auto_execute"] = True
        config["trading"]["force_24_7_mode"] = True
        
        with open(argo_config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Updated {argo_config_path}")
    
    # Fix Prop Firm production config
    prop_config_path = "/root/argo-production-prop-firm/config.json"
    if os.path.exists(prop_config_path):
        with open(prop_config_path, 'r') as f:
            config = json.load(f)
        
        # Ensure prop_firm is enabled for prop firm service
        if "prop_firm" not in config:
            config["prop_firm"] = {}
        config["prop_firm"]["enabled"] = True
        config["prop_firm"]["account"] = "prop_firm_test"
        
        # Ensure trading settings
        if "trading" not in config:
            config["trading"] = {}
        config["trading"]["auto_execute"] = True
        config["trading"]["force_24_7_mode"] = True
        
        with open(prop_config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Updated {prop_config_path}")

if __name__ == "__main__":
    fix_configs()

