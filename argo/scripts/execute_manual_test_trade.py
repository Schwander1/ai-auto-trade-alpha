#!/usr/bin/env python3
"""
Manual Test Trade Execution
Creates a simple test signal and executes it to verify trading works
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime, timezone

# Add paths
argo_path = Path(__file__).parent.parent
if str(argo_path) not in sys.path:
    sys.path.insert(0, str(argo_path))
workspace_root = argo_path.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from argo.core.paper_trading_engine import PaperTradingEngine
from argo.core.environment import detect_environment

async def execute_manual_test_trade():
    """Execute a manual test trade with a simple signal"""
    
    print('\n' + '='*70)
    print('🧪 MANUAL TEST TRADE EXECUTION')
    print('='*70)
    
    # Detect environment
    environment = detect_environment()
    print(f'\n🌍 Environment: {environment.upper()}')
    
    # Initialize trading engine
    print('\n📊 Initializing trading engine...')
    trading_engine = PaperTradingEngine()
    
    if not trading_engine.alpaca_enabled:
        print('❌ ERROR: Alpaca not connected. Cannot execute test trade.')
        return False
    
    # Get account details
    account = trading_engine.get_account_details()
    print(f'✅ Connected to: {trading_engine.account_name}')
    print(f'   Portfolio: ${account["portfolio_value"]:,.2f}')
    print(f'   Buying Power: ${account["buying_power"]:,.2f}')
    
    # Check existing positions
    print('\n📊 Checking existing positions...')
    positions = trading_engine.get_positions()
    print(f'   Current positions: {len(positions)}')
    for pos in positions[:3]:  # Show first 3
        print(f'   - {pos["symbol"]}: {pos["side"]} {pos["qty"]} @ ${pos["entry_price"]:.2f}')
    
    # Create a simple test signal
    # Use crypto for 24/7 trading (market hours don't matter)
    # Alpaca uses different crypto symbol format - try both
    test_symbol = None
    current_price = None
    
    # Try crypto symbols (24/7 trading)
    crypto_symbols = ["BTCUSD", "BTC/USD", "BTC-USD", "ETHUSD", "ETH/USD", "ETH-USD"]
    for symbol in crypto_symbols:
        print(f'\n💰 Getting current price for {symbol}...')
        price = trading_engine.get_current_price(symbol)
        if price:
            test_symbol = symbol
            current_price = price
            break
    
    # If crypto doesn't work, try stocks (may fail if market closed)
    if not current_price:
        print('   Crypto not available, trying stocks (may fail if market closed)...')
        stock_symbols = ["SPY", "QQQ", "AAPL", "MSFT"]
        for symbol in stock_symbols:
            print(f'   Trying {symbol}...')
            price = trading_engine.get_current_price(symbol)
            if price:
                test_symbol = symbol
                current_price = price
                break
    
    if not current_price:
        print('❌ Could not get current price. Cannot execute test trade.')
        return False
    
    print(f'   Current price: ${current_price:.2f}')
    
    # Create a minimal test signal (BUY order)
    # Use very small position size (1% of buying power)
    buying_power = float(account.get("buying_power", 100000))
    position_size_pct = 0.01  # 1% for testing
    position_value = buying_power * position_size_pct
    qty = int(position_value / current_price)
    
    # For crypto, ensure we have at least a small position
    # For expensive assets like BTC, use a smaller percentage
    if test_symbol.endswith('-USD') and current_price > 50000:
        # Use even smaller position for expensive crypto
        position_size_pct = 0.005  # 0.5% for expensive crypto
        position_value = buying_power * position_size_pct
        qty = int(position_value / current_price)
    
    if qty < 1:
        # For very expensive assets, ensure minimum 1 share
        qty = 1  # Minimum 1 share/coin
        print(f'   ⚠️  Adjusted qty to minimum: {qty} (price too high for calculated position size)')
    
    print(f'\n📝 Creating test signal:')
    print(f'   Symbol: {test_symbol}')
    print(f'   Action: BUY')
    print(f'   Quantity: {qty} shares')
    print(f'   Entry Price: ${current_price:.2f}')
    print(f'   Position Value: ${qty * current_price:.2f}')
    
    # Create signal dict
    test_signal = {
        'symbol': test_symbol,
        'action': 'BUY',
        'entry_price': current_price,
        'confidence': 100.0,  # High confidence for test
        'strategy': 'manual_test',
        'asset_type': 'crypto' if test_symbol.endswith('-USD') else 'stock',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'stop_price': current_price * 0.97,  # 3% stop loss
        'target_price': current_price * 1.05,  # 5% take profit
        'qty': qty  # Specify quantity
    }
    
    # Check if we already have a position
    existing_position = next((p for p in positions if p['symbol'] == test_symbol), None)
    if existing_position:
        print(f'\n⚠️  Position already exists for {test_symbol}')
        print(f'   Current: {existing_position["side"]} {existing_position["qty"]} @ ${existing_position["entry_price"]:.2f}')
        print('   Test trade will close this position instead')
        test_signal['action'] = 'SELL' if existing_position['side'] == 'LONG' else 'BUY'
    
    # Execute the test trade
    print(f'\n🚀 Executing test trade...')
    try:
        order_id = trading_engine.execute_signal(test_signal)
        
        if not order_id:
            print('❌ Test trade execution failed - no order ID returned')
            return False
        
        print(f'✅ Test trade executed successfully!')
        print(f'   Order ID: {order_id}')
        
        # Wait a moment for order to process
        await asyncio.sleep(2)
        
        # Verify order status
        print('\n🔍 Verifying order status...')
        order_status = trading_engine.get_order_status(order_id)
        
        if order_status:
            print(f'   Status: {order_status.get("status", "unknown")}')
            print(f'   Side: {order_status.get("side", "unknown")}')
            print(f'   Symbol: {order_status.get("symbol", "unknown")}')
            print(f'   Quantity: {order_status.get("qty", 0)}')
            print(f'   Filled Qty: {order_status.get("filled_qty", 0)}')
            if order_status.get("filled_avg_price"):
                print(f'   Filled Price: ${order_status["filled_avg_price"]:.2f}')
            if order_status.get("limit_price"):
                print(f'   Limit Price: ${order_status["limit_price"]:.2f}')
        else:
            print('   ⚠️  Order status not yet available')
        
        # Check position
        print('\n📊 Checking position...')
        await asyncio.sleep(1)  # Give it a moment
        positions = trading_engine.get_positions()
        test_position = next((p for p in positions if p['symbol'] == test_symbol), None)
        
        if test_position:
            print(f'✅ Position confirmed:')
            print(f'   Symbol: {test_position["symbol"]}')
            print(f'   Side: {test_position["side"]}')
            print(f'   Quantity: {test_position["qty"]}')
            print(f'   Entry Price: ${test_position["entry_price"]:.2f}')
            if test_position.get("current_price"):
                print(f'   Current Price: ${test_position["current_price"]:.2f}')
            if test_position.get("pnl_pct"):
                print(f'   P&L: {test_position["pnl_pct"]:.2f}%')
        else:
            print(f'   ⚠️  Position not yet visible (may be pending or order was a close)')
        
        # Get updated account
        print('\n💰 Updated account status:')
        account = trading_engine.get_account_details()
        print(f'   Portfolio: ${account["portfolio_value"]:,.2f}')
        print(f'   Buying Power: ${account["buying_power"]:,.2f}')
        
        return True
        
    except Exception as e:
        print(f'❌ Error executing test trade: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = asyncio.run(execute_manual_test_trade())
    
    if success:
        print('\n' + '='*70)
        print('✅ MANUAL TEST TRADE COMPLETED SUCCESSFULLY')
        print('='*70)
        print('\n📝 Trading system is working correctly!')
        print('   You can now enable full automated trading.')
        print('='*70 + '\n')
    else:
        print('\n' + '='*70)
        print('❌ MANUAL TEST TRADE FAILED')
        print('='*70)
        print('\n⚠️  Please review the errors above.')
        print('='*70 + '\n')
    
    sys.exit(0 if success else 1)

