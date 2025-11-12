#!/usr/bin/env python3
"""Alpine Analytics Paper Trading Engine"""
import json, logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlpinePaperTrading")

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    ALPACA_AVAILABLE = True
except:
    ALPACA_AVAILABLE = False
    logger.warning("Alpaca SDK not available - using simulation mode")

class PaperTradingEngine:
    def __init__(self, config_path='/root/argo-production/config.json'):
        with open(config_path) as f:
            config = json.load(f)
        self.config = config.get('trading', {})
        
        if ALPACA_AVAILABLE and config.get('alpaca', {}).get('enabled', True):
            try:
                self.alpaca = TradingClient(
                    config['alpaca']['api_key'],
                    config['alpaca']['secret_key'],
                    paper=config['alpaca'].get('paper', True)
                )
                account = self.alpaca.get_account()
                logger.info(f"✅ Alpaca connected | Portfolio: ${float(account.portfolio_value):,.2f}")
                self.alpaca_enabled = True
            except Exception as e:
                logger.error(f"Alpaca connection failed: {e}")
                self.alpaca_enabled = False
        else:
            logger.warning("Alpaca not configured - simulation mode")
            self.alpaca_enabled = False
    
    def execute_signal(self, signal):
        if self.alpaca_enabled:
            return self._execute_live(signal)
        return self._execute_sim(signal)
    
    def _execute_live(self, signal):
        try:
            symbol, action = signal['symbol'], signal['action']
            account = self.alpaca.get_account()
            
            # Get current price (simplified)
            entry_price = signal.get('entry_price', 100)
            
            # Calculate position size
            position_size_pct = self.config.get('position_size_pct', 10)
            position_value = float(account.buying_power) * (position_size_pct / 100)
            qty = int(position_value / entry_price)
            
            if qty == 0:
                return None
            
            # Submit order
            side = OrderSide.BUY if action == 'BUY' else OrderSide.SELL
            order_request = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                time_in_force=TimeInForce.DAY
            )
            order = self.alpaca.submit_order(order_request)
            
            logger.info(f"✅ {side.value} {qty} {symbol} @ ${entry_price:.2f}")
            return order.id
        except Exception as e:
            logger.error(f"Order failed: {e}")
            return None
    
    def _execute_sim(self, signal):
        logger.info(f"✅ SIM: {signal['action']} {signal['symbol']} @ ${signal.get('entry_price', 0):.2f}")
        return f"SIM_{int(datetime.utcnow().timestamp())}"
    
    def get_positions(self):
        if not self.alpaca_enabled:
            return []
        try:
            return [{
                'symbol': p.symbol,
                'qty': int(p.qty),
                'side': p.side,
                'entry_price': float(p.avg_entry_price),
                'current_price': float(p.current_price),
                'pnl_pct': float(p.unrealized_plpc) * 100
            } for p in self.alpaca.list_positions()]
        except:
            return []

if __name__ == "__main__":
    engine = PaperTradingEngine()
    test_signal = {
        'symbol': 'AAPL', 'action': 'BUY', 'entry_price': 180.50,
        'confidence': 92.5, 'strategy': 'alpine_consensus'
    }
    order_id = engine.execute_signal(test_signal)
    logger.info(f"Test complete: {order_id}")
    logger.info("✅ Alpine Analytics Paper Trading Engine ready!")
