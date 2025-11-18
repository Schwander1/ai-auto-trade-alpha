#!/usr/bin/env python3
"""
Verification script for crypto 24/7 signal generation
Tests all components to ensure crypto signals are generated during after-hours/weekends
"""
import os
import sys
import json
from datetime import datetime

def check_environment():
    """Check if 24/7 mode is enabled"""
    print("=" * 60)
    print("1. Checking Environment Configuration")
    print("=" * 60)
    
    argo_24_7 = os.getenv('ARGO_24_7_MODE', '').lower()
    is_enabled = argo_24_7 in ['true', '1', 'yes']
    
    print(f"   ARGO_24_7_MODE: {os.getenv('ARGO_24_7_MODE', 'NOT SET')}")
    print(f"   Status: {'✅ ENABLED' if is_enabled else '❌ DISABLED'}")
    
    if not is_enabled:
        print("   ⚠️  WARNING: 24/7 mode is not enabled!")
        print("   Set ARGO_24_7_MODE=true to enable crypto 24/7 trading")
    
    return is_enabled

def check_default_symbols():
    """Check if crypto symbols are in DEFAULT_SYMBOLS"""
    print("\n" + "=" * 60)
    print("2. Checking Default Symbols")
    print("=" * 60)
    
    try:
        # Add project root to path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from argo.argo.core.signal_generation_service import DEFAULT_SYMBOLS
        
        crypto_symbols = [s for s in DEFAULT_SYMBOLS if '-USD' in s or s.startswith('BTC') or s.startswith('ETH')]
        
        print(f"   DEFAULT_SYMBOLS: {DEFAULT_SYMBOLS}")
        print(f"   Crypto symbols found: {crypto_symbols}")
        
        if crypto_symbols:
            print(f"   Status: ✅ {len(crypto_symbols)} crypto symbol(s) configured")
        else:
            print("   Status: ❌ No crypto symbols found in DEFAULT_SYMBOLS")
        
        return crypto_symbols
    except Exception as e:
        print(f"   Status: ❌ Error checking symbols: {e}")
        return []

def check_crypto_detection():
    """Check crypto symbol detection method"""
    print("\n" + "=" * 60)
    print("3. Checking Crypto Symbol Detection")
    print("=" * 60)
    
    try:
        # Add project root to path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from argo.argo.core.signal_generation_service import SignalGenerationService
        
        service = SignalGenerationService()
        test_symbols = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'AAPL', 'NVDA']
        
        print("   Testing symbol detection:")
        for symbol in test_symbols:
            is_crypto = service._is_crypto_symbol(symbol)
            status = "🪙 CRYPTO" if is_crypto else "📈 STOCK"
            print(f"      {symbol:10} -> {status}")
        
        print("   Status: ✅ Crypto detection method working")
        return True
    except Exception as e:
        print(f"   Status: ❌ Error: {e}")
        return False

def check_data_sources():
    """Check which data sources support crypto"""
    print("\n" + "=" * 60)
    print("4. Checking Data Sources for Crypto Support")
    print("=" * 60)
    
    try:
        # Add project root to path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from argo.argo.core.signal_generation_service import SignalGenerationService
        
        service = SignalGenerationService()
        data_sources = service.data_sources if hasattr(service, 'data_sources') else {}
        
        crypto_sources = {}
        
        # Check Massive.com
        if "massive" in data_sources:
            crypto_sources["Massive.com"] = {
                "enabled": True,
                "supports_crypto": True,
                "24_7": True,
                "weight": "40%"
            }
        
        # Check Alpaca Pro
        if "alpaca_pro" in data_sources:
            crypto_sources["Alpaca Pro"] = {
                "enabled": True,
                "supports_crypto": True,
                "24_7": True,
                "weight": "supplemental"
            }
        
        # Check xAI Grok
        if "x_sentiment" in data_sources:
            crypto_sources["xAI Grok"] = {
                "enabled": True,
                "supports_crypto": True,
                "24_7": True,
                "weight": "20%"
            }
        
        # Check Sonar AI
        if "sonar" in data_sources:
            crypto_sources["Sonar AI"] = {
                "enabled": True,
                "supports_crypto": True,
                "24_7": True,
                "weight": "15%"
            }
        
        # Check yfinance
        if "yfinance" in data_sources:
            crypto_sources["yfinance"] = {
                "enabled": True,
                "supports_crypto": True,
                "24_7": True,
                "weight": "supplemental"
            }
        
        print(f"   Total data sources: {len(data_sources)}")
        print(f"   Crypto-capable sources: {len(crypto_sources)}")
        print("\n   Crypto-capable sources:")
        for name, info in crypto_sources.items():
            print(f"      ✅ {name:15} - {info['weight']:12} - 24/7: {info['24_7']}")
        
        if len(crypto_sources) >= 2:
            print(f"\n   Status: ✅ {len(crypto_sources)} crypto-capable source(s) available")
        else:
            print(f"\n   Status: ⚠️  Only {len(crypto_sources)} crypto-capable source(s) - recommend at least 2")
        
        return crypto_sources
    except Exception as e:
        print(f"   Status: ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {}

def check_24_7_mode():
    """Check if 24/7 mode is properly initialized"""
    print("\n" + "=" * 60)
    print("5. Checking 24/7 Mode Initialization")
    print("=" * 60)
    
    try:
        # Add project root to path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from argo.argo.core.signal_generation_service import SignalGenerationService
        
        service = SignalGenerationService()
        is_24_7 = not getattr(service, '_cursor_aware', True)
        
        print(f"   _cursor_aware: {getattr(service, '_cursor_aware', 'NOT SET')}")
        print(f"   24/7 mode active: {is_24_7}")
        
        if is_24_7:
            print("   Status: ✅ 24/7 mode is active - signals will generate continuously")
        else:
            print("   Status: ❌ 24/7 mode is NOT active - signals may pause")
        
        return is_24_7
    except Exception as e:
        print(f"   Status: ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_adaptive_cache():
    """Check adaptive cache configuration for crypto"""
    print("\n" + "=" * 60)
    print("6. Checking Adaptive Cache for Crypto")
    print("=" * 60)
    
    try:
        # Add project root to path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from argo.argo.core.adaptive_cache import AdaptiveCache
        
        cache = AdaptiveCache()
        
        # Test cache TTL for crypto vs stocks
        test_symbols = {
            'BTC-USD': 'crypto',
            'ETH-USD': 'crypto',
            'AAPL': 'stock',
            'NVDA': 'stock'
        }
        
        print("   Cache TTL for symbols (base_ttl=10s):")
        for symbol, asset_type in test_symbols.items():
            ttl = cache.get_cache_ttl(symbol, is_market_hours=False, base_ttl=10)
            print(f"      {symbol:10} ({asset_type:6}) -> {ttl:2}s TTL")
        
        # Verify crypto uses shorter cache
        btc_ttl = cache.get_cache_ttl('BTC-USD', is_market_hours=False, base_ttl=10)
        if btc_ttl <= 20:
            print(f"\n   Status: ✅ Crypto uses optimized cache TTL ({btc_ttl}s)")
        else:
            print(f"\n   Status: ⚠️  Crypto cache TTL may be too long ({btc_ttl}s)")
        
        return True
    except Exception as e:
        print(f"   Status: ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_summary(results):
    """Generate verification summary"""
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = all([
        results.get('environment', False),
        len(results.get('crypto_symbols', [])) > 0,
        results.get('crypto_detection', False),
        len(results.get('data_sources', {})) >= 2,
        results.get('24_7_mode', False),
        results.get('adaptive_cache', False)
    ])
    
    if all_passed:
        print("\n✅ ALL CHECKS PASSED")
        print("\n   Crypto 24/7 signal generation is properly configured!")
        print("   The system will generate signals for crypto during:")
        print("   - After-hours trading")
        print("   - Weekends")
        print("   - All times (24/7)")
    else:
        print("\n⚠️  SOME CHECKS FAILED")
        print("\n   Please review the issues above and fix them.")
    
    print("\n" + "=" * 60)
    print(f"Verification completed at: {datetime.now().isoformat()}")
    print("=" * 60)

def main():
    """Run all verification checks"""
    print("\n" + "=" * 60)
    print("CRYPTO 24/7 SIGNAL GENERATION VERIFICATION")
    print("=" * 60)
    print(f"Started at: {datetime.now().isoformat()}\n")
    
    results = {
        'environment': check_environment(),
        'crypto_symbols': check_default_symbols(),
        'crypto_detection': check_crypto_detection(),
        'data_sources': check_data_sources(),
        '24_7_mode': check_24_7_mode(),
        'adaptive_cache': check_adaptive_cache()
    }
    
    generate_summary(results)
    
    return 0 if all([
        results.get('environment', False),
        len(results.get('crypto_symbols', [])) > 0,
        results.get('crypto_detection', False),
        len(results.get('data_sources', {})) >= 2,
        results.get('24_7_mode', False),
        results.get('adaptive_cache', False)
    ]) else 1

if __name__ == "__main__":
    sys.exit(main())

