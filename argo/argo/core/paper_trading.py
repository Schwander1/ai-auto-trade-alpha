#!/usr/bin/env python3
"""Alpine Analytics - Paper Trading Execution"""
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PaperTrading")

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    logger.warning("⚠️  Alpaca SDK not available")

def execute_paper_trade(signal, dry_run=False):
    """
    Execute paper trade based on signal
    
    Args:
        signal (dict): Trading signal from generator
        dry_run (bool): If True, simulate without actual order
    
    Returns:
        dict: Order details or None if failed
    """
    if not ALPACA_AVAILABLE:
        logger.error("❌ Alpaca SDK not available")
        return None
    
    try:
        # Load config
        with open('/root/argo-production/config.json') as f:
            config = json.load(f)
        
        # Initialize Alpaca client
        client = TradingClient(
            'PKVFBDORPHOCX5NEOVEZNDTWVT',
            'ErscqTCdo21raoiFFyDzASzHpfgWB8L7xWVWKFukVa6b',
            paper=True
        )
        
        # Get account info
        account = client.get_account()
        buying_power = float(account.buying_power)
        
        # Calculate position size (10% of buying power)
        position_size_pct = config['trading'].get('position_size', 10)
        position_value = buying_power * (position_size_pct / 100)
        
        # Calculate shares
        shares = int(position_value / signal['entry_price'])
        
        if shares <= 0:
            logger.warning(f"⚠️  Insufficient buying power for {signal['symbol']}")
            return None
        
        if dry_run:
            logger.info(f"🔷 DRY RUN: Would {signal['action']} {shares} shares of {signal['symbol']} @ ${signal['entry_price']:.2f}")
            return {'dry_run': True, 'shares': shares}
        
        # Create order
        order_side = OrderSide.BUY if signal['action'] == 'LONG' else OrderSide.SELL
        
        order_request = MarketOrderRequest(
            symbol=signal['symbol'],
            qty=shares,
            side=order_side,
            time_in_force=TimeInForce.DAY
        )
        
        order = client.submit_order(order_request)
        
        logger.info(f"✅ Order placed: {signal['action']} {shares} {signal['symbol']} @ ${signal['entry_price']:.2f}")
        logger.info(f"   Order ID: {order.id}")
        
        return {
            'order_id': str(order.id),
            'symbol': signal['symbol'],
            'action': signal['action'],
            'shares': shares,
            'entry_price': signal['entry_price'],
            'status': str(order.status)
        }
        
    except Exception as e:
        logger.error(f"❌ Error executing trade for {signal['symbol']}: {e}")
        return None

if __name__ == "__main__":
    # Test with dummy signal
    test_signal = {
        'symbol': 'AAPL',
        'action': 'LONG',
        'entry_price': 225.50,
        'confidence': 92.5
    }
    execute_paper_trade(test_signal, dry_run=True)
