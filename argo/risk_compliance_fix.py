#!/usr/bin/env python3
"""
Risk Management Compliance Fix
Automatically closes positions to bring portfolio into compliance with risk rules
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from argo.core.paper_trading_engine import PaperTradingEngine
from argo.core.signal_generation_service import SignalGenerationService
import time

def main():
    print('\n' + '='*70)
    print('🔧 RISK COMPLIANCE FIX - AUTOMATIC POSITION ADJUSTMENT')
    print('='*70)
    
    # Initialize
    engine = PaperTradingEngine()
    service = SignalGenerationService()
    
    # Get current state
    account = engine.get_account_details()
    positions = engine.get_positions()
    config = service.trading_config
    
    buying_power = account['buying_power']
    max_position_size_pct = config.get('max_position_size_pct', 15)
    max_correlated_positions = config.get('max_correlated_positions', 3)
    
    # Correlation groups
    correlation_groups = {
        'tech': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMD', 'XLK', 'QQQ'],
        'finance': ['JPM', 'BAC', 'WFC', 'GS', 'XLF'],
        'energy': ['XOM', 'CVX', 'XLE'],
        'consumer': ['AMZN', 'TSLA', 'DIS', 'XLY'],
        'healthcare': ['JNJ', 'PFE', 'XLV'],
        'etf_broad': ['SPY', 'QQQ', 'DIA', 'IWM'],
        'crypto': ['BTC-USD', 'ETH-USD', 'COIN']
    }
    
    actions_taken = []
    
    # 1. Fix position size violations
    print(f'\n💰 FIXING POSITION SIZE VIOLATIONS:')
    print('-' * 70)
    
    for pos in positions:
        position_value = abs(pos['qty']) * pos['current_price']
        position_size_pct = (position_value / buying_power) * 100 if buying_power > 0 else 0
        
        if position_size_pct > max_position_size_pct:
            # Calculate how many shares to close
            max_allowed_value = buying_power * (max_position_size_pct / 100)
            excess_value = position_value - max_allowed_value
            excess_shares = int(excess_value / pos['current_price'])
            
            if excess_shares > 0:
                print(f'\n   {pos["symbol"]}:')
                print(f'      Current: {abs(pos["qty"])} shares ({position_size_pct:.1f}% of BP)')
                print(f'      Target: {abs(pos["qty"]) - excess_shares} shares ({max_position_size_pct}% of BP)')
                print(f'      Closing: {excess_shares} shares...')
                
                # Create sell signal to close partial position
                # For LONG positions, we need to SELL
                # For SHORT positions, we need to BUY
                action = 'SELL' if pos['side'] == 'LONG' else 'BUY'
                
                # Close partial position by creating a signal with the excess quantity
                # We'll need to submit a partial close order
                try:
                    from alpaca.trading.requests import MarketOrderRequest
                    from alpaca.trading.enums import OrderSide, TimeInForce
                    
                    side = OrderSide.SELL if pos['side'] == 'LONG' else OrderSide.BUY
                    order_request = MarketOrderRequest(
                        symbol=pos['symbol'],
                        qty=excess_shares,
                        side=side,
                        time_in_force=TimeInForce.DAY
                    )
                    order = engine.alpaca.submit_order(order_request)
                    
                    print(f'      ✅ Order submitted: {order.id}')
                    actions_taken.append({
                        'symbol': pos['symbol'],
                        'action': 'partial_close',
                        'shares': excess_shares,
                        'order_id': order.id
                    })
                    
                    time.sleep(1)  # Brief pause between orders
                except Exception as e:
                    print(f'      ❌ Error: {e}')
    
    # 2. Fix correlation group violations
    print(f'\n🔗 FIXING CORRELATION GROUP VIOLATIONS:')
    print('-' * 70)
    
    for group_name, symbols in correlation_groups.items():
        group_positions = [p for p in positions if p['symbol'] in symbols]
        
        if len(group_positions) > max_correlated_positions:
            excess_count = len(group_positions) - max_correlated_positions
            print(f'\n   {group_name} group: {len(group_positions)} positions (max: {max_correlated_positions})')
            print(f'      Need to close {excess_count} position(s)')
            
            # Sort by position size (close largest first) or by P&L (close losers first)
            # Let's close positions with worst P&L first
            group_positions_sorted = sorted(group_positions, key=lambda x: x['pnl_pct'])
            
            for i in range(excess_count):
                pos_to_close = group_positions_sorted[i]
                print(f'      Closing: {pos_to_close["symbol"]} ({pos_to_close["side"]}, P&L: {pos_to_close["pnl_pct"]:.2f}%)')
                
                try:
                    action = 'SELL' if pos_to_close['side'] == 'LONG' else 'BUY'
                    signal = {
                        'symbol': pos_to_close['symbol'],
                        'action': action,
                        'entry_price': pos_to_close['current_price'],
                        'confidence': 100.0,
                        'strategy': 'risk_compliance',
                        'asset_type': 'stock',
                        'timestamp': '2024-01-01T00:00:00'
                    }
                    
                    order_id = engine.execute_signal(signal)
                    if order_id:
                        print(f'      ✅ Order submitted: {order_id}')
                        actions_taken.append({
                            'symbol': pos_to_close['symbol'],
                            'action': 'full_close',
                            'reason': f'{group_name} correlation limit',
                            'order_id': order_id
                        })
                        time.sleep(1)
                except Exception as e:
                    print(f'      ❌ Error: {e}')
    
    # Wait for orders to fill
    if actions_taken:
        print(f'\n⏳ Waiting 5 seconds for orders to fill...')
        time.sleep(5)
        
        # Verify final state
        print(f'\n📊 FINAL STATE:')
        final_positions = engine.get_positions()
        final_account = engine.get_account_details()
        
        print(f'   Positions: {len(final_positions)} (was {len(positions)})')
        print(f'   Portfolio Value: ${final_account["portfolio_value"]:,.2f}')
        print(f'   Buying Power: ${final_account["buying_power"]:,.2f}')
        
        # Check if violations are resolved
        violations_remaining = 0
        for pos in final_positions:
            position_value = abs(pos['qty']) * pos['current_price']
            position_size_pct = (position_value / final_account['buying_power']) * 100 if final_account['buying_power'] > 0 else 0
            if position_size_pct > max_position_size_pct:
                violations_remaining += 1
        
        if violations_remaining == 0:
            print(f'\n✅ All position size violations resolved!')
        else:
            print(f'\n⚠️  {violations_remaining} position size violations still remain')
    
    print('\n' + '='*70)
    print('✅ Risk compliance fix complete!')
    print('='*70 + '\n')

if __name__ == '__main__':
    main()

