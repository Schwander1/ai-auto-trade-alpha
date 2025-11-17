#!/usr/bin/env python3
"""
Test Single Backtest with Detailed Logging
"""
import sys
import asyncio
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.backtest.enhanced_backtester import EnhancedBacktester

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_backtest():
    """Test a single backtest with detailed logging"""
    print("\n" + "="*80)
    print("🧪 TESTING SINGLE BACKTEST")
    print("="*80)
    
    backtester = EnhancedBacktester()
    
    print("\n📊 Running backtest for AAPL...")
    metrics = await backtester.run_backtest('AAPL', min_confidence=55.0)
    
    if metrics:
        print("\n✅ Backtest completed!")
        print(f"   Total trades: {metrics.total_trades}")
        print(f"   Win rate: {metrics.win_rate_pct:.2f}%")
        print(f"   Total return: {metrics.total_return_pct:.2f}%")
        print(f"   Sharpe ratio: {metrics.sharpe_ratio:.2f}")
        
        if metrics.total_trades == 0:
            print("\n⚠️  WARNING: No trades generated!")
            print("   Checking backtester state...")
            print(f"   Positions: {backtester.positions}")
            print(f"   Trades list: {len(backtester.trades)} trades")
    else:
        print("\n❌ Backtest returned None!")

if __name__ == "__main__":
    asyncio.run(test_backtest())

