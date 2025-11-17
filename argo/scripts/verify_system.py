#!/usr/bin/env python3
"""
Complete System Verification Script
Verifies all components are working correctly
"""
import sys
import asyncio
from pathlib import Path

# Add paths - ensure argo is in path
argo_path = Path(__file__).parent.parent
if str(argo_path) not in sys.path:
    sys.path.insert(0, str(argo_path))
# Also add workspace root for shared packages
workspace_root = argo_path.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

def verify_imports():
    """Verify all critical imports work"""
    print("🔍 Verifying imports...")
    issues = []
    
    try:
        from argo.core.environment import detect_environment, get_environment_info
        print("  ✅ Environment detection")
    except Exception as e:
        issues.append(f"Environment detection: {e}")
        print(f"  ❌ Environment detection: {e}")
    
    try:
        from argo.core.paper_trading_engine import PaperTradingEngine
        print("  ✅ Paper trading engine")
    except Exception as e:
        issues.append(f"Paper trading engine: {e}")
        print(f"  ❌ Paper trading engine: {e}")
    
    try:
        from argo.core.signal_generation_service import SignalGenerationService
        print("  ✅ Signal generation service")
    except Exception as e:
        issues.append(f"Signal generation service: {e}")
        print(f"  ❌ Signal generation service: {e}")
    
    try:
        from argo.core.weighted_consensus_engine import WeightedConsensusEngine
        print("  ✅ Weighted consensus engine")
    except Exception as e:
        issues.append(f"Weighted consensus engine: {e}")
        print(f"  ❌ Weighted consensus engine: {e}")
    
    return len(issues) == 0, issues

def verify_dependencies():
    """Verify all dependencies are installed"""
    print("\n🔍 Verifying dependencies...")
    required = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'yfinance': 'yfinance',
        'alpaca': 'alpaca.trading.client',
        'fastapi': 'fastapi',
        'sqlalchemy': 'sqlalchemy',
        'requests': 'requests'
    }
    
    issues = []
    for name, module in required.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError as e:
            issues.append(f"{name}: {e}")
            print(f"  ❌ {name}: {e}")
    
    return len(issues) == 0, issues

async def verify_system():
    """Verify system components"""
    print("\n🔍 Verifying system components...")
    issues = []
    
    try:
        from argo.core.environment import detect_environment
        env = detect_environment()
        print(f"  ✅ Environment: {env}")
    except Exception as e:
        issues.append(f"Environment: {e}")
        print(f"  ❌ Environment: {e}")
    
    try:
        from argo.core.paper_trading_engine import PaperTradingEngine
        engine = PaperTradingEngine()
        if engine.alpaca_enabled:
            account = engine.get_account_details()
            print(f"  ✅ Trading engine: Connected to {engine.account_name}")
            print(f"     Portfolio: ${account['portfolio_value']:,.2f}")
        else:
            print("  ⚠️  Trading engine: Simulation mode (Alpaca not connected)")
    except Exception as e:
        issues.append(f"Trading engine: {e}")
        print(f"  ❌ Trading engine: {e}")
    
    try:
        from argo.core.signal_generation_service import SignalGenerationService
        service = SignalGenerationService()
        print(f"  ✅ Signal service: Initialized")
        print(f"     Auto-execute: {service.auto_execute}")
        print(f"     Environment: {service.environment}")
    except Exception as e:
        issues.append(f"Signal service: {e}")
        print(f"  ❌ Signal service: {e}")
    
    return len(issues) == 0, issues

def main():
    """Main verification"""
    print("="*70)
    print("🔍 COMPLETE SYSTEM VERIFICATION")
    print("="*70)
    
    all_ok = True
    all_issues = []
    
    # Verify imports
    ok, issues = verify_imports()
    all_ok = all_ok and ok
    all_issues.extend(issues)
    
    # Verify dependencies
    ok, issues = verify_dependencies()
    all_ok = all_ok and ok
    all_issues.extend(issues)
    
    # Verify system
    ok, issues = asyncio.run(verify_system())
    all_ok = all_ok and ok
    all_issues.extend(issues)
    
    # Summary
    print("\n" + "="*70)
    print("📊 VERIFICATION SUMMARY")
    print("="*70)
    
    if all_ok:
        print("✅ ALL VERIFICATIONS PASSED!")
        print("\n🎉 System is fully operational and ready for use!")
        return 0
    else:
        print("❌ SOME VERIFICATIONS FAILED")
        print("\n⚠️  Issues found:")
        for issue in all_issues:
            print(f"   - {issue}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

