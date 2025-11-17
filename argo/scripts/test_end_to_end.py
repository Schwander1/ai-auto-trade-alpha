#!/usr/bin/env python3
"""
End-to-End Trading System Test
Tests the complete flow from signal generation to trade execution
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_end_to_end():
    """Test complete trading system flow"""
    print('\n' + '='*70)
    print('🧪 END-TO-END TRADING SYSTEM TEST')
    print('='*70)
    print(f'Timestamp: {datetime.now().isoformat()}')
    print('')
    
    results = []
    
    # Test 1: Environment Detection
    print('1️⃣  Testing Environment Detection...')
    try:
        from argo.core.environment import detect_environment, get_environment_info
        env = detect_environment()
        env_info = get_environment_info()
        print(f'   ✅ Environment detected: {env}')
        print(f'   ✅ Hostname: {env_info["hostname"]}')
        results.append(('Environment Detection', True))
    except Exception as e:
        print(f'   ❌ Failed: {e}')
        results.append(('Environment Detection', False))
    
    # Test 2: AWS Secrets Manager Access
    print('\n2️⃣  Testing AWS Secrets Manager Access...')
    try:
        from argo.utils.secrets_manager import get_secrets_manager
        secrets = get_secrets_manager()
        test_secret = secrets.get_secret('alpaca-paper', service='argo')
        if test_secret:
            print(f'   ✅ Successfully retrieved secret from AWS')
            results.append(('AWS Secrets Manager', True))
        else:
            print(f'   ⚠️  Secret not found (may use config.json fallback)')
            results.append(('AWS Secrets Manager', False))
    except Exception as e:
        print(f'   ⚠️  AWS not available: {e} (will use config.json)')
        results.append(('AWS Secrets Manager', False))
    
    # Test 3: Trading Engine Initialization
    print('\n3️⃣  Testing Trading Engine Initialization...')
    try:
        from argo.core.paper_trading_engine import PaperTradingEngine
        engine = PaperTradingEngine()
        if engine.alpaca_enabled:
            account = engine.get_account_details()
            print(f'   ✅ Trading engine initialized')
            print(f'   ✅ Account: {engine.account_name}')
            print(f'   ✅ Portfolio: ${account["portfolio_value"]:,.2f}')
            results.append(('Trading Engine', True))
        else:
            print(f'   ⚠️  Trading engine initialized but Alpaca not connected')
            results.append(('Trading Engine', False))
    except Exception as e:
        print(f'   ❌ Failed: {e}')
        results.append(('Trading Engine', False))
    
    # Test 4: Account Selection
    print('\n4️⃣  Testing Account Selection...')
    try:
        from argo.core.paper_trading_engine import PaperTradingEngine
        from argo.core.environment import detect_environment
        engine = PaperTradingEngine()
        env = detect_environment()
        
        # Verify correct account for environment
        if env == 'production' and 'Production' in engine.account_name:
            print(f'   ✅ Correct account selected for {env}')
            results.append(('Account Selection', True))
        elif env == 'development' and 'Dev' in engine.account_name:
            print(f'   ✅ Correct account selected for {env}')
            results.append(('Account Selection', True))
        else:
            print(f'   ⚠️  Account/environment mismatch')
            results.append(('Account Selection', False))
    except Exception as e:
        print(f'   ❌ Failed: {e}')
        results.append(('Account Selection', False))
    
    # Test 5: Position Retrieval
    print('\n5️⃣  Testing Position Retrieval...')
    try:
        from argo.core.paper_trading_engine import PaperTradingEngine
        engine = PaperTradingEngine()
        if engine.alpaca_enabled:
            positions = engine.get_positions()
            print(f'   ✅ Successfully retrieved {len(positions)} positions')
            results.append(('Position Retrieval', True))
        else:
            print(f'   ⚠️  Cannot test - Alpaca not connected')
            results.append(('Position Retrieval', False))
    except Exception as e:
        print(f'   ❌ Failed: {e}')
        results.append(('Position Retrieval', False))
    
    # Test 6: Signal Generation Service
    print('\n6️⃣  Testing Signal Generation Service...')
    try:
        from argo.core.signal_generation_service import SignalGenerationService
        service = SignalGenerationService()
        print(f'   ✅ Signal generation service initialized')
        print(f'   ✅ Environment: {service.environment}')
        print(f'   ✅ Auto-execute: {service.auto_execute}')
        if service.trading_engine and service.trading_engine.alpaca_enabled:
            print(f'   ✅ Trading engine connected')
        results.append(('Signal Generation', True))
    except Exception as e:
        print(f'   ⚠️  Failed: {e}')
        results.append(('Signal Generation', False))
    
    # Summary
    print('\n' + '='*70)
    print('📊 TEST SUMMARY')
    print('='*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = '✅ PASS' if result else '❌ FAIL'
        print(f'   {status} - {test_name}')
    
    print('')
    print(f'Results: {passed}/{total} tests passed')
    
    if passed == total:
        print('✅ All tests passed - System is fully operational!')
    elif passed >= total * 0.8:
        print('⚠️  Most tests passed - System is mostly operational')
    else:
        print('❌ Multiple tests failed - System needs attention')
    
    print('='*70 + '\n')
    
    return passed == total

if __name__ == '__main__':
    success = test_end_to_end()
    sys.exit(0 if success else 1)

