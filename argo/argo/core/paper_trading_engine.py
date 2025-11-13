#!/usr/bin/env python3
"""Alpine Analytics Paper Trading Engine"""
import json
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

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

# Add shared package to path
shared_path = Path(__file__).parent.parent.parent.parent.parent / "packages" / "shared"
if shared_path.exists():
    sys.path.insert(0, str(shared_path))

try:
    from utils.secrets_manager import get_secret
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False

class PaperTradingEngine:
    def __init__(self, config_path=None):
        # Try to get Alpaca credentials from AWS Secrets Manager first
        alpaca_api_key = None
        alpaca_secret_key = None
        alpaca_paper = True
        
        if SECRETS_MANAGER_AVAILABLE:
            try:
                service = "argo"
                alpaca_api_key = get_secret("alpaca-api-key", service=service)
                alpaca_secret_key = get_secret("alpaca-secret-key", service=service)
                paper_mode = get_secret("alpaca-paper", service=service, default="true")
                alpaca_paper = paper_mode.lower() == "true" if paper_mode else True
            except Exception as e:
                logger.warning(f"Failed to get Alpaca credentials from AWS Secrets Manager: {e}")
        
        # Fallback to config.json if AWS Secrets Manager doesn't have the keys
        if not alpaca_api_key or not alpaca_secret_key:
            if config_path is None:
                config_path = os.getenv('ARGO_CONFIG_PATH', '/root/argo-production/config.json')
            
            if os.path.exists(config_path):
                try:
                    with open(config_path) as f:
                        config = json.load(f)
                    alpaca_config = config.get('alpaca', {})
                    alpaca_api_key = alpaca_api_key or alpaca_config.get('api_key') or os.getenv('ALPACA_API_KEY')
                    alpaca_secret_key = alpaca_secret_key or alpaca_config.get('secret_key') or os.getenv('ALPACA_SECRET_KEY')
                    alpaca_paper = alpaca_config.get('paper', True) if alpaca_config else True
                    self.config = config.get('trading', {})
                except Exception as e:
                    logger.warning(f"Failed to load config.json: {e}")
                    self.config = {}
            else:
                # Try environment variables as last resort
                alpaca_api_key = alpaca_api_key or os.getenv('ALPACA_API_KEY')
                alpaca_secret_key = alpaca_secret_key or os.getenv('ALPACA_SECRET_KEY')
                self.config = {}
        
        if ALPACA_AVAILABLE and alpaca_api_key and alpaca_secret_key:
            try:
                self.alpaca = TradingClient(
                    alpaca_api_key,
                    alpaca_secret_key,
                    paper=alpaca_paper
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
