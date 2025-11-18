#!/usr/bin/env python3
"""
Auto-Fix Common Preparation Issues
Automatically fixes common issues found during preparation checks
"""
import sys
import json
import os
from pathlib import Path

# Add paths
argo_path = Path(__file__).parent.parent
if str(argo_path) not in sys.path:
    sys.path.insert(0, str(argo_path))

def create_data_directory():
    """Create data directory if it doesn't exist"""
    data_dir = argo_path / "data"
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created data directory: {data_dir}")
        return True
    return False

def create_logs_directory():
    """Create logs directory if it doesn't exist"""
    logs_dir = argo_path / "logs"
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created logs directory: {logs_dir}")
        return True
    return False

def check_database_file():
    """Ensure database file can be created"""
    data_dir = argo_path / "data"
    if not data_dir.exists():
        create_data_directory()
    
    db_file = data_dir / "signals.db"
    if not db_file.exists():
        # Database will be created on first use, just ensure directory is writable
        if os.access(data_dir, os.W_OK):
            print(f"✅ Database directory is writable: {data_dir}")
            return True
        else:
            print(f"⚠️  Database directory is not writable: {data_dir}")
            return False
    return True

def verify_config_structure():
    """Verify and suggest config structure fixes"""
    config_paths = [
        argo_path / "config.json",
        Path("config.json"),
    ]
    
    config_path = None
    for path in config_paths:
        if path.exists():
            config_path = path
            break
    
    if not config_path:
        print("⚠️  config.json not found - cannot auto-fix")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        fixes_applied = []
        
        # Ensure trading section exists
        if "trading" not in config:
            config["trading"] = {
                "min_confidence": 75.0,
                "position_size_pct": 10.0,
                "max_position_size_pct": 15.0,
                "stop_loss": 0.03,
                "profit_target": 0.05,
                "auto_execute": False
            }
            fixes_applied.append("Added trading section with defaults")
        
        # Ensure data directory exists in config if needed
        if fixes_applied:
            # Backup original
            backup_path = config_path.with_suffix('.json.backup')
            if not backup_path.exists():
                import shutil
                shutil.copy(config_path, backup_path)
                print(f"✅ Created backup: {backup_path}")
            
            # Write updated config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Applied {len(fixes_applied)} config fix(es):")
            for fix in fixes_applied:
                print(f"   - {fix}")
            return True
        
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Config file has JSON errors: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Could not verify config: {e}")
        return False

def main():
    """Run auto-fixes"""
    print("🔧 AUTO-FIX PREPARATION ISSUES")
    print("=" * 60)
    print()
    
    fixes_applied = 0
    
    # Fix 1: Create directories
    print("1. Checking directories...")
    if create_data_directory():
        fixes_applied += 1
    if create_logs_directory():
        fixes_applied += 1
    print()
    
    # Fix 2: Check database
    print("2. Checking database...")
    if check_database_file():
        fixes_applied += 1
    print()
    
    # Fix 3: Verify config
    print("3. Verifying configuration...")
    if verify_config_structure():
        fixes_applied += 1
    print()
    
    # Summary
    print("=" * 60)
    print(f"✅ Applied {fixes_applied} fix(es)")
    print()
    print("💡 Next steps:")
    print("   1. Run preparation check: python3 scripts/pre_trading_preparation.py")
    print("   2. Review any remaining warnings")
    print("   3. Configure Alpaca credentials if needed")
    print()

if __name__ == '__main__':
    main()

