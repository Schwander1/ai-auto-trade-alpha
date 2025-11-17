#!/usr/bin/env python3
"""
Configuration Validation Script
Validates configuration files for production readiness

Usage:
    python scripts/validate_config.py [config_path]
"""
import sys
import argparse
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.core.config_validator import ConfigValidator, validate_config_file

def main():
    parser = argparse.ArgumentParser(description='Validate configuration file')
    parser.add_argument('config_path', nargs='?', default=None, help='Path to config.json file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    # Find config file
    if args.config_path:
        config_path = Path(args.config_path)
    else:
        # Try common locations
        possible_paths = [
            Path(__file__).parent.parent / "config.json",
            Path("/root/argo-production/config.json"),
            Path("/root/argo-production-prop-firm/config.json"),
        ]

        config_path = None
        for path in possible_paths:
            if path.exists():
                config_path = path
                break

        if not config_path:
            print("❌ Configuration file not found")
            print("   Please specify config_path or ensure config.json exists in standard locations")
            sys.exit(1)

    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)

    # Validate
    try:
        with open(config_path) as f:
            config = json.load(f)

        validator = ConfigValidator()
        is_valid = validator.validate_config(config, config_path)

        if args.json:
            report = validator.get_validation_report()
            print(json.dumps(report, indent=2))
        else:
            if is_valid:
                print(f"✅ Configuration is valid: {config_path}")
                if validator.warnings:
                    print(f"\n⚠️  {len(validator.warnings)} warning(s) found")
            else:
                print(f"❌ Configuration validation failed: {config_path}")
                print(f"   {len(validator.errors)} error(s) found")
                sys.exit(1)

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {config_path}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error validating {config_path}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
