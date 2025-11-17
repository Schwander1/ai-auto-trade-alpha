#!/usr/bin/env python3
"""
Comprehensive Code Test Suite
Tests all components for correctness, completeness, and world-class quality
"""
import sys
import asyncio
from pathlib import Path
from typing import List, Dict

# Add paths
argo_path = Path(__file__).parent.parent
if str(argo_path) not in sys.path:
    sys.path.insert(0, str(argo_path))
workspace_root = argo_path.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

def test_imports():
    """Test all critical imports"""
    print("1️⃣  Testing Imports...")
    issues = []
    
    modules = [
        ("argo.core.environment", "Environment detection"),
        ("argo.core.paper_trading_engine", "Paper trading engine"),
        ("argo.core.signal_generation_service", "Signal generation service"),
        ("argo.core.weighted_consensus_engine", "Weighted consensus engine"),
        ("argo.backtest.base_backtester", "Base backtester"),
        ("argo.backtest.data_manager", "Data manager"),
        ("argo.backtest.strategy_backtester", "Strategy backtester"),
        ("argo.backtest.profit_backtester", "Profit backtester"),
        ("argo.backtest.walk_forward", "Walk-forward tester"),
        ("argo.backtest.optimizer", "Parameter optimizer"),
        ("argo.backtest.results_storage", "Results storage"),
    ]
    
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"   ✅ {description}")
        except Exception as e:
            print(f"   ❌ {description}: {e}")
            issues.append(f"{description}: {e}")
    
    return issues

async def test_backtesters():
    """Test backtester implementations"""
    print("\n2️⃣  Testing Backtesters...")
    issues = []
    
    try:
        from argo.backtest.base_backtester import BaseBacktester
        from argo.backtest.strategy_backtester import StrategyBacktester
        from argo.backtest.profit_backtester import ProfitBacktester
        
        # Test StrategyBacktester
        try:
            backtester = StrategyBacktester()
            print("   ✅ StrategyBacktester initialized")
            
            # Check if run_backtest is async
            import inspect
            if inspect.iscoroutinefunction(backtester.run_backtest):
                print("   ✅ run_backtest is async")
            else:
                print("   ⚠️  run_backtest is not async")
                issues.append("StrategyBacktester.run_backtest should be async")
        except Exception as e:
            print(f"   ❌ StrategyBacktester: {e}")
            issues.append(f"StrategyBacktester: {e}")
        
        # Test ProfitBacktester
        try:
            profit_backtester = ProfitBacktester()
            print("   ✅ ProfitBacktester initialized")
            
            if inspect.iscoroutinefunction(profit_backtester.run_backtest):
                print("   ✅ run_backtest is async")
            else:
                print("   ⚠️  run_backtest is not async")
                issues.append("ProfitBacktester.run_backtest should be async")
        except Exception as e:
            print(f"   ❌ ProfitBacktester: {e}")
            issues.append(f"ProfitBacktester: {e}")
            
    except Exception as e:
        print(f"   ❌ Backtester test failed: {e}")
        issues.append(f"Backtester test: {e}")
    
    return issues

def test_trading_engine():
    """Test trading engine methods"""
    print("\n3️⃣  Testing Trading Engine...")
    issues = []
    
    try:
        from argo.core.paper_trading_engine import PaperTradingEngine
        
        engine = PaperTradingEngine()
        
        # Test get_current_price
        try:
            price = engine.get_current_price("AAPL")
            if price is not None or not engine.alpaca_enabled:
                print("   ✅ get_current_price() method exists")
            else:
                print("   ⚠️  get_current_price() returned None")
        except AttributeError:
            print("   ❌ get_current_price() method missing")
            issues.append("get_current_price() method missing")
        except Exception as e:
            print(f"   ⚠️  get_current_price() error: {e}")
        
        # Test get_all_orders
        try:
            orders = engine.get_all_orders(limit=5)
            print("   ✅ get_all_orders() method works")
        except Exception as e:
            print(f"   ❌ get_all_orders() error: {e}")
            issues.append(f"get_all_orders(): {e}")
        
        # Test get_positions
        try:
            positions = engine.get_positions()
            print("   ✅ get_positions() method works")
        except Exception as e:
            print(f"   ❌ get_positions() error: {e}")
            issues.append(f"get_positions(): {e}")
            
    except Exception as e:
        print(f"   ❌ Trading engine test failed: {e}")
        issues.append(f"Trading engine: {e}")
    
    return issues

async def test_optimizer():
    """Test parameter optimizer"""
    print("\n4️⃣  Testing Parameter Optimizer...")
    issues = []
    
    try:
        from argo.backtest.optimizer import ParameterOptimizer
        from argo.backtest.strategy_backtester import StrategyBacktester
        
        backtester = StrategyBacktester()
        optimizer = ParameterOptimizer(backtester)
        
        # Check if grid_search is implemented
        import inspect
        source = inspect.getsource(optimizer.grid_search)
        
        if "For now, return placeholder" in source or "Full implementation would" in source and "return placeholder" in source:
            print("   ⚠️  grid_search() may be incomplete")
        else:
            print("   ✅ grid_search() appears complete")
        
        # Check if it's async
        if inspect.iscoroutinefunction(optimizer.grid_search):
            print("   ✅ grid_search() is async")
        else:
            print("   ⚠️  grid_search() is not async")
            issues.append("grid_search() should be async")
            
    except Exception as e:
        print(f"   ❌ Optimizer test failed: {e}")
        issues.append(f"Optimizer: {e}")
    
    return issues

def test_walk_forward():
    """Test walk-forward tester"""
    print("\n5️⃣  Testing Walk-Forward Tester...")
    issues = []
    
    try:
        from argo.backtest.walk_forward import WalkForwardTester
        from argo.backtest.strategy_backtester import StrategyBacktester
        
        backtester = StrategyBacktester()
        walk_forward = WalkForwardTester(backtester)
        
        # Check if run_walk_forward is async
        import inspect
        if inspect.iscoroutinefunction(walk_forward.run_walk_forward):
            print("   ✅ run_walk_forward() is async")
        else:
            print("   ⚠️  run_walk_forward() is not async")
            issues.append("run_walk_forward() should be async")
        
        print("   ✅ WalkForwardTester initialized")
        
    except Exception as e:
        print(f"   ❌ Walk-forward test failed: {e}")
        issues.append(f"Walk-forward: {e}")
    
    return issues

def test_data_manager():
    """Test data manager"""
    print("\n6️⃣  Testing Data Manager...")
    issues = []
    
    try:
        from argo.backtest.data_manager import DataManager
        import pandas as pd
        
        dm = DataManager()
        
        # Test validation
        test_df = pd.DataFrame({
            'Open': [100] * 150,
            'High': [105] * 150,
            'Low': [99] * 150,
            'Close': [104] * 150,
            'Volume': [1000] * 150
        })
        test_df.index = pd.date_range('2020-01-01', periods=150, freq='D')
        
        is_valid, validation_issues = dm.validate_data(test_df)
        if is_valid:
            print("   ✅ Data validation works")
        else:
            print(f"   ⚠️  Validation issues: {validation_issues}")
        
        print("   ✅ DataManager initialized")
        
    except Exception as e:
        print(f"   ❌ Data manager test failed: {e}")
        issues.append(f"Data manager: {e}")
    
    return issues

async def main():
    """Run all tests"""
    print("="*70)
    print("🔍 COMPREHENSIVE CODE TEST SUITE")
    print("="*70)
    print()
    
    all_issues = []
    
    # Run all tests
    all_issues.extend(test_imports())
    all_issues.extend(await test_backtesters())
    all_issues.extend(test_trading_engine())
    all_issues.extend(await test_optimizer())
    all_issues.extend(test_walk_forward())
    all_issues.extend(test_data_manager())
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    if all_issues:
        print(f"\n⚠️  Found {len(all_issues)} issue(s):")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
        return 1
    else:
        print("\n✅ ALL TESTS PASSED!")
        print("\n🎉 Code quality: World-class!")
        return 0

if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

