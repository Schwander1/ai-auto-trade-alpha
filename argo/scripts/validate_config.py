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
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from argo.core.config_validator import ConfigValidator, validate_config_file
except ImportError as e:
    logger.error(f"Could not import config_validator: {e}")
    print(f"❌ Error: Could not import required modules: {e}")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Validate configuration file')
    parser.add_argument('config_path', nargs='?', default=None, help='Path to config.json file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

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
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {config_path}: {e}")
            print(f"❌ Invalid JSON in {config_path}: {e}")
            sys.exit(1)
        except PermissionError as e:
            logger.error(f"Permission denied reading {config_path}: {e}")
            print(f"❌ Permission denied reading {config_path}: {e}")
            sys.exit(1)

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
                    if args.verbose:
                        for warning in validator.warnings:
                            print(f"   ⚠️  {warning}")
            else:
                print(f"❌ Configuration validation failed: {config_path}")
                print(f"   {len(validator.errors)} error(s) found")
                if args.verbose:
                    for error in validator.errors:
                        print(f"   ❌ {error}")
                sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("Validation interrupted by user")
        print("\n⚠️  Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error validating {config_path}: {e}", exc_info=True)
        print(f"❌ Error validating {config_path}: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
