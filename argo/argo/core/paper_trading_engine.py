#!/usr/bin/env python3
"""Alpine Analytics Paper Trading Engine"""
import json
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlpinePaperTrading")

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopLossRequest, TakeProfitRequest
    from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass
    ALPACA_AVAILABLE = True
except Exception as e:
    ALPACA_AVAILABLE = False
    logger.warning(f"Alpaca SDK not available - using simulation mode: {e}")
    # Fallback enum definitions when Alpaca is not available
    from enum import Enum
    class OrderSide(Enum):
        BUY = "buy"
        SELL = "sell"
    class TimeInForce(Enum):
        DAY = "day"
        GTC = "gtc"
    class OrderClass(Enum):
        SIMPLE = "simple"
        BRACKET = "bracket"

# Use Argo-specific secrets manager
try:
    from argo.utils.secrets_manager import get_secret
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False

class PaperTradingEngine:
    def __init__(self, config_path=None):
        self._init_environment()
        self._init_config(config_path)
        credentials = self._resolve_credentials(config_path)
        self._init_alpaca_client(credentials)
    
    def _init_environment(self):
        """Initialize environment detection"""
        from argo.core.environment import detect_environment, get_environment_info
        self.environment = detect_environment()
        env_info = get_environment_info()
        logger.info(f"🌍 Environment detected: {self.environment}")
        logger.debug(f"   Environment details: {env_info}")
    
    def _init_config(self, config_path):
        """Initialize configuration"""
        self.config = {}
        self.full_config = {}
        config_path = self._find_config_path(config_path)
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    self.full_config = json.load(f)
                    self.config = self.full_config.get('trading', {})
                    
                    # Check for prop firm mode
                    prop_firm_config = self.full_config.get('prop_firm', {})
                    self.prop_firm_enabled = prop_firm_config.get('enabled', False)
                    self.prop_firm_config = prop_firm_config if self.prop_firm_enabled else None
                    
                    if self.prop_firm_enabled:
                        logger.info("🏢 PROP FIRM MODE ENABLED")
                        risk_limits = prop_firm_config.get('risk_limits', {})
                        logger.info(f"   Max Drawdown: {risk_limits.get('max_drawdown_pct', 2.0)}%")
                        logger.info(f"   Daily Loss Limit: {risk_limits.get('daily_loss_limit_pct', 4.5)}%")
                        logger.info(f"   Max Position Size: {risk_limits.get('max_position_size_pct', 3.0)}%")
                        logger.info(f"   Min Confidence: {risk_limits.get('min_confidence', 82.0)}%")
                        logger.info(f"   Max Positions: {risk_limits.get('max_positions', 3)}")
            except Exception as e:
                logger.warning(f"Failed to load config.json: {e}")
                self.prop_firm_enabled = False
                self.prop_firm_config = None
    
    def _find_config_path(self, config_path):
        """Find config.json path"""
        if config_path:
            return config_path
        
        # Check environment variable first
        env_path = os.getenv('ARGO_CONFIG_PATH')
        if env_path and os.path.exists(env_path):
            return env_path
        
        # Check current working directory first (for prop firm service)
        cwd_config = Path.cwd() / 'config.json'
        if cwd_config.exists():
            return str(cwd_config)
        
        # Check production paths
        for prod_path in [
            '/root/argo-production-prop-firm/config.json',  # Prop firm service
            '/root/argo-production-green/config.json',
            '/root/argo-production-blue/config.json',
            '/root/argo-production/config.json'
        ]:
            if os.path.exists(prod_path):
                return prod_path
        
        # Check dev path
        dev_path = Path(__file__).parent.parent.parent / 'config.json'
        if dev_path.exists():
            return str(dev_path)
        
        # Fallback to workspace root
        workspace_path = Path(__file__).parent.parent.parent.parent / 'config.json'
        if workspace_path.exists():
            return str(workspace_path)
        
        return '/root/argo-production/config.json'
    
    def _resolve_credentials(self, config_path) -> Dict[str, Optional[str]]:
        """Resolve Alpaca credentials from multiple sources"""
        credentials = {
            'api_key': None,
            'secret_key': None,
            'paper': True,
            'account_name': None
        }
        
        # Try AWS Secrets Manager first
        secrets_manager_creds = {}
        if SECRETS_MANAGER_AVAILABLE:
            secrets_manager_creds = self._get_credentials_from_secrets_manager()
            # Validate AWS Secrets Manager credentials before using them
            if secrets_manager_creds.get('api_key') and secrets_manager_creds.get('secret_key'):
                # Test if credentials work
                if self._validate_credentials(secrets_manager_creds['api_key'], secrets_manager_creds['secret_key'], secrets_manager_creds.get('paper', True)):
                    credentials.update(secrets_manager_creds)
                    logger.info("✅ Using credentials from AWS Secrets Manager")
                else:
                    logger.warning("⚠️  AWS Secrets Manager credentials failed validation, falling back to config.json")
                    secrets_manager_creds = {}  # Clear invalid credentials
        
        # Fallback to config.json
        if not credentials['api_key'] or not credentials['secret_key']:
            config_path = self._find_config_path(config_path)
            config_creds = self._get_credentials_from_config(config_path)
            credentials['api_key'] = credentials['api_key'] or config_creds['api_key']
            credentials['secret_key'] = credentials['secret_key'] or config_creds['secret_key']
            credentials['account_name'] = credentials['account_name'] or config_creds['account_name']
            credentials['paper'] = config_creds.get('paper', credentials['paper'])
        
        # Final fallback to environment variables
        credentials['api_key'] = credentials['api_key'] or os.getenv('ALPACA_API_KEY')
        credentials['secret_key'] = credentials['secret_key'] or os.getenv('ALPACA_SECRET_KEY')
        credentials['account_name'] = credentials['account_name'] or f"{self.environment.title()} Account"
        
        return credentials
    
    def _validate_credentials(self, api_key: str, secret_key: str, paper: bool = True) -> bool:
        """Validate Alpaca credentials by attempting a connection"""
        try:
            if ALPACA_AVAILABLE:
                client = TradingClient(api_key, secret_key, paper=paper)
                account = client.get_account()
                return account is not None
        except Exception as e:
            logger.debug(f"Credential validation failed: {e}")
            return False
        return False
    
    def _get_credentials_from_secrets_manager(self) -> Dict[str, Optional[str]]:
        """Get credentials from AWS Secrets Manager"""
        credentials = {'api_key': None, 'secret_key': None, 'paper': True}
        
        try:
            service = "argo"
            if self.environment == "development":
                credentials['api_key'] = get_secret("alpaca-api-key-dev", service=service) or \
                                       get_secret("alpaca-api-key", service=service)
                credentials['secret_key'] = get_secret("alpaca-secret-key-dev", service=service) or \
                                          get_secret("alpaca-secret-key", service=service)
            else:  # production
                credentials['api_key'] = get_secret("alpaca-api-key-production", service=service) or \
                                       get_secret("alpaca-api-key", service=service)
                credentials['secret_key'] = get_secret("alpaca-secret-key-production", service=service) or \
                                          get_secret("alpaca-secret-key", service=service)
            
            paper_mode = get_secret("alpaca-paper", service=service, default="true")
            credentials['paper'] = paper_mode.lower() == "true" if paper_mode else True
        except Exception as e:
            logger.warning(f"Failed to get Alpaca credentials from AWS Secrets Manager: {e}")
        
        return credentials
    
    def _get_credentials_from_config(self, config_path: Optional[str]) -> Dict[str, Optional[str]]:
        """Get credentials from config.json"""
        credentials = {'api_key': None, 'secret_key': None, 'account_name': None, 'paper': True}
        
        if not config_path or not os.path.exists(config_path):
            return credentials
        
        try:
            with open(config_path) as f:
                config = json.load(f)
                alpaca_config = config.get('alpaca', {})
                
                # Update trading config if not already loaded
                if not self.config:
                    self.config = config.get('trading', {})
                
                # PROP FIRM: Check if prop firm mode is enabled and use prop firm account
                prop_firm_config = config.get('prop_firm', {})
                prop_firm_enabled = prop_firm_config.get('enabled', False)
                prop_firm_account_name = prop_firm_config.get('account', 'prop_firm_test')
                
                if prop_firm_enabled and prop_firm_account_name in alpaca_config:
                    # Use prop firm test account
                    prop_firm_account = alpaca_config[prop_firm_account_name]
                    api_key = prop_firm_account.get('api_key')
                    secret_key = prop_firm_account.get('secret_key')
                    
                    if not api_key or not secret_key:
                        logger.error(f"❌ Prop firm account '{prop_firm_account_name}' missing credentials")
                        # Fall through to standard account selection
                    else:
                        credentials.update({
                            'api_key': api_key,
                            'secret_key': secret_key,
                            'account_name': prop_firm_account.get('account_name', 'Prop Firm Test Account'),
                            'paper': prop_firm_account.get('paper', True)
                        })
                        logger.info(f"🏢 PROP FIRM MODE: Using {credentials['account_name']}")
                        logger.info(f"   Account: {prop_firm_account_name}")
                        return credentials
                
                # Standard account selection (dev/production)
                if isinstance(alpaca_config, dict):
                    if self.environment == "production" and "production" in alpaca_config:
                        env_config = alpaca_config["production"]
                        credentials.update({
                            'api_key': env_config.get('api_key'),
                            'secret_key': env_config.get('secret_key'),
                            'account_name': env_config.get('account_name', 'Production Trading Account')
                        })
                        logger.info(f"📊 Using Production paper account: {credentials['account_name']}")
                    elif self.environment == "development" and "dev" in alpaca_config:
                        env_config = alpaca_config["dev"]
                        credentials.update({
                            'api_key': env_config.get('api_key'),
                            'secret_key': env_config.get('secret_key'),
                            'account_name': env_config.get('account_name', 'Dev Trading Account')
                        })
                        logger.info(f"📊 Using Dev paper account: {credentials['account_name']}")
                    else:
                        # Fallback to legacy structure
                        credentials['api_key'] = alpaca_config.get('api_key')
                        credentials['secret_key'] = alpaca_config.get('secret_key')
                        logger.info("📊 Using legacy/default Alpaca account")
                    
                    credentials['paper'] = alpaca_config.get('paper', True)
        except Exception as e:
            logger.warning(f"Failed to load credentials from config.json: {e}")
        
        return credentials
    
    def _init_alpaca_client(self, credentials: Dict):
        """Initialize Alpaca trading client"""
        if not (ALPACA_AVAILABLE and credentials['api_key'] and credentials['secret_key']):
            logger.warning("Alpaca not configured - simulation mode")
            self.alpaca_enabled = False
            self._order_tracker = {}
            self._retry_attempts = 3
            self._retry_delay = 1
            return
        
        try:
            self.alpaca = TradingClient(
                credentials['api_key'],
                credentials['secret_key'],
                paper=credentials['paper']
            )
            account = self.alpaca.get_account()
            self.account_name = credentials['account_name']
            logger.info(f"✅ Alpaca connected ({self.environment}) | Account: {self.account_name}")
            logger.info(f"   Portfolio: ${float(account.portfolio_value):,.2f} | Buying Power: ${float(account.buying_power):,.2f}")
            self.alpaca_enabled = True
            self._order_tracker = {}
            self._retry_attempts = self.config.get('max_retry_attempts', 3)
            self._retry_delay = self.config.get('retry_delay_seconds', 1)
        except Exception as e:
            logger.error(f"Alpaca connection failed: {e}")
            self.alpaca_enabled = False
    
    def is_market_open(self):
        """Check if market is currently open"""
        if not self.alpaca_enabled:
            return True  # Assume open for simulation
        try:
            clock = self.alpaca.get_clock()
            return clock.is_open
        except Exception as e:
            logger.warning(f"Could not check market status: {e}")
            return True  # Default to open if check fails
    
    def get_asset_volatility(self, symbol, days=20):
        """Calculate asset volatility (ATR-based) for position sizing"""
        try:
            from alpaca.data.historical import StockHistoricalDataClient
            from alpaca.data.requests import StockBarsRequest
            from alpaca.data.timeframe import TimeFrame
            from datetime import datetime, timedelta
            
            # Use yfinance as fallback for volatility calculation
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=f"{days}d")
            
            if hist.empty or len(hist) < 2:
                return 0.02  # Default 2% volatility
            
            # Calculate ATR (Average True Range) approximation
            high_low = (hist['High'] - hist['Low']).mean()
            high_close = (hist['High'] - hist['Close'].shift()).abs().mean()
            low_close = (hist['Low'] - hist['Close'].shift()).abs().mean()
            
            tr = max(high_low, high_close, low_close)
            atr_pct = (tr / hist['Close'].mean()) if hist['Close'].mean() > 0 else 0.02
            
            return max(0.01, min(0.10, atr_pct))  # Clamp between 1% and 10%
        except Exception as e:
            logger.debug(f"Could not calculate volatility for {symbol}: {e}")
            return 0.02  # Default 2% volatility
    
    def execute_signal(self, signal, retry_count=0):
        """Execute signal with retry logic"""
        if self.alpaca_enabled:
            try:
                return self._execute_live(signal)
            except Exception as e:
                if retry_count < self._retry_attempts:
                    logger.warning(f"Retry {retry_count + 1}/{self._retry_attempts} for {signal.get('symbol')}: {e}")
                    import time
                    time.sleep(self._retry_delay * (retry_count + 1))  # Exponential backoff
                    return self.execute_signal(signal, retry_count + 1)
                else:
                    logger.error(f"Max retries exceeded for {signal.get('symbol')}: {e}")
                    return None
        return self._execute_sim(signal)
    
    def _execute_live(self, signal):
        """Execute live trade through Alpaca"""
        try:
            symbol, action = signal['symbol'], signal['action']
            
            if not self._is_trade_allowed(symbol):
                return None
            
            account = self.alpaca.get_account()
            order_details = self._prepare_order_details(signal, account, action)
            if not order_details:
                return None
            
            order = self._submit_main_order(order_details)
            if not order:
                return None
            
            self._track_order(order, signal, order_details)
            
            if order_details.get('place_bracket'):
                self._place_bracket_orders(symbol, order_details, order.id)
            
            self._log_order_execution(order_details, account, action)
            
            return order.id
            
        except Exception as e:
            logger.error(f"Order failed for {signal.get('symbol', 'unknown')}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def _is_trade_allowed(self, symbol: str) -> bool:
        """Check if trade is allowed (market hours, etc.)"""
        if not self.is_market_open() and not symbol.endswith('-USD'):
            logger.warning(f"⏭️  Market is closed - skipping {symbol}")
            return False
        return True
    
    def _prepare_order_details(self, signal: Dict, account, action: str) -> Optional[Dict]:
        """Prepare order details including quantity and side"""
        entry_price = signal.get('entry_price', 100)
        confidence = signal.get('confidence', 75)
        stop_price = signal.get('stop_price')
        target_price = signal.get('target_price')
        
        # PROP FIRM: Enforce max stop loss limit
        if hasattr(self, 'prop_firm_enabled') and self.prop_firm_enabled and self.prop_firm_config:
            max_stop_loss_pct = self.prop_firm_config.get('risk_limits', {}).get('max_stop_loss_pct', 1.5)
            if stop_price:
                if action == 'BUY':
                    stop_loss_pct = ((entry_price - stop_price) / entry_price) * 100
                else:  # SELL
                    stop_loss_pct = ((stop_price - entry_price) / entry_price) * 100
                
                if stop_loss_pct > max_stop_loss_pct:
                    # Adjust stop loss to max allowed
                    if action == 'BUY':
                        stop_price = entry_price * (1 - max_stop_loss_pct / 100)
                    else:  # SELL
                        stop_price = entry_price * (1 + max_stop_loss_pct / 100)
                    logger.warning(f"⚠️  Prop firm: Stop loss adjusted to {max_stop_loss_pct}% limit (was {stop_loss_pct:.2f}%)")
        
        if action == 'SELL':
            return self._prepare_sell_order_details(signal, account, entry_price, stop_price, target_price)
        else:
            return self._prepare_buy_order_details(signal, account, entry_price, confidence, stop_price, target_price)
    
    def _prepare_sell_order_details(self, signal: Dict, account, entry_price: float, 
                                     stop_price: Optional[float], target_price: Optional[float]) -> Optional[Dict]:
        """Prepare details for SELL order (close position or new short)"""
        symbol = signal['symbol']
        positions = self.get_positions()
        existing_position = next((p for p in positions if p['symbol'] == symbol), None)
        
        if existing_position:
            qty = abs(int(existing_position['qty']))
            side = OrderSide.SELL if existing_position['side'] == 'LONG' else OrderSide.BUY
            logger.info(f"🔄 Closing position: {existing_position['side']} {qty} {symbol}")
            return {
                'symbol': symbol,
                'qty': qty,
                'side': side,
                'entry_price': entry_price,
                'is_closing': True,
                'place_bracket': False
            }
        else:
            qty, side = self._calculate_position_size(signal, account, entry_price)
            return {
                'symbol': symbol,
                'qty': qty,
                'side': OrderSide.SELL,
                'entry_price': entry_price,
                'stop_price': stop_price,
                'target_price': target_price,
                'is_closing': False,
                'place_bracket': True
            }
    
    def _prepare_buy_order_details(self, signal: Dict, account, entry_price: float, 
                                    confidence: float, stop_price: Optional[float], 
                                    target_price: Optional[float]) -> Optional[Dict]:
        """Prepare details for BUY order"""
        signal_qty = signal.get('qty') or signal.get('filled_qty')
        if signal_qty and signal_qty > 0:
            logger.info(f"📝 Using qty from signal: {int(signal_qty)} (test/manual trade)")
            return {
                'symbol': signal['symbol'],
                'qty': int(signal_qty),
                'side': OrderSide.BUY,
                'entry_price': entry_price,
                'is_closing': False,
                'place_bracket': False
            }
        
        qty, side = self._calculate_position_size(signal, account, entry_price)
        return {
            'symbol': signal['symbol'],
            'qty': qty,
            'side': OrderSide.BUY,
            'entry_price': entry_price,
            'stop_price': stop_price,
            'target_price': target_price,
            'is_closing': False,
            'place_bracket': True
        }
    
    def _calculate_position_size(self, signal: Dict, account, entry_price: float) -> Tuple[int, OrderSide]:
        """Calculate position size based on confidence, volatility, and config"""
        # PROP FIRM: Use prop firm limits if enabled
        if hasattr(self, 'prop_firm_enabled') and self.prop_firm_enabled and self.prop_firm_config:
            risk_limits = self.prop_firm_config.get('risk_limits', {})
            base_position_size_pct = risk_limits.get('max_position_size_pct', 3.0)
            max_position_size_pct = base_position_size_pct  # Prop firm: fixed size
            min_confidence = risk_limits.get('min_confidence', 82.0)
            confidence = signal.get('confidence', 75)
            
            # Prop firm: Reject if confidence too low
            if confidence < min_confidence:
                logger.warning(f"⚠️  Prop firm: Confidence {confidence:.2f}% < {min_confidence}% minimum")
                return 0, OrderSide.BUY
            
            # Prop firm: Fixed position size (no scaling)
            position_size_pct = base_position_size_pct
        else:
            # Standard mode: Dynamic position sizing
            base_position_size_pct = self.config.get('position_size_pct', 10)
            max_position_size_pct = self.config.get('max_position_size_pct', 15)
            confidence = signal.get('confidence', 75)
            
            # Apply volatility adjustment
            volatility = self.get_asset_volatility(signal['symbol'])
            avg_volatility = 0.02
            volatility_multiplier = min(avg_volatility / volatility if volatility > 0 else 1.0, 1.5)
            
            # Scale by confidence
            if confidence >= 75:
                confidence_multiplier = 1.0 + ((confidence - 75) / 25) * 0.5
                position_size_pct = min(base_position_size_pct * confidence_multiplier * volatility_multiplier, max_position_size_pct)
            else:
                position_size_pct = base_position_size_pct * 0.75 * volatility_multiplier
        
        buying_power = float(account.buying_power)
        position_value = buying_power * (position_size_pct / 100)
        qty = int(position_value / entry_price)
        
        side = OrderSide.BUY if signal['action'] == 'BUY' else OrderSide.SELL
        
        return qty, side
    
    def _submit_main_order(self, order_details: Dict):
        """Submit the main order (market or limit)"""
        use_limit_orders = self.config.get('use_limit_orders', False)
        limit_offset_pct = self.config.get('limit_order_offset_pct', 0.001)
        
        if order_details['qty'] == 0:
            logger.warning(f"⚠️  Calculated qty is 0 for {order_details['symbol']} (price: ${order_details['entry_price']:.2f})")
            return None
        
        if use_limit_orders and not order_details.get('is_closing'):
            limit_price = self._calculate_limit_price(
                order_details['entry_price'], 
                order_details['side'], 
                limit_offset_pct
            )
            order_request = LimitOrderRequest(
                symbol=order_details['symbol'],
                qty=order_details['qty'],
                side=order_details['side'],
                limit_price=limit_price,
                time_in_force=TimeInForce.DAY
            )
        else:
            order_request = MarketOrderRequest(
                symbol=order_details['symbol'],
                qty=order_details['qty'],
                side=order_details['side'],
                time_in_force=TimeInForce.DAY
            )
        
        return self.alpaca.submit_order(order_request)
    
    def _calculate_limit_price(self, entry_price: float, side: OrderSide, offset_pct: float) -> float:
        """Calculate limit price with offset"""
        if side == OrderSide.BUY:
            return entry_price * (1 + offset_pct)
        else:
            return entry_price * (1 - offset_pct)
    
    def _place_bracket_orders(self, symbol: str, order_details: Dict, main_order_id: str):
        """Place stop loss and take profit orders"""
        qty = order_details['qty']
        stop_price = order_details.get('stop_price')
        target_price = order_details.get('target_price')
        side = order_details['side']
        
        if not (stop_price and target_price):
            return
        
        try:
            stop_side = OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY
            stop_order = StopLossRequest(
                symbol=symbol,
                qty=qty,
                stop_price=stop_price,
                time_in_force=TimeInForce.GTC
            )
            stop_order_result = self.alpaca.submit_order(stop_order)
            logger.info(f"🛡️  Stop loss order placed: {stop_order_result.id} @ ${stop_price:.2f}")
            
            profit_order = TakeProfitRequest(
                symbol=symbol,
                qty=qty,
                limit_price=target_price,
                time_in_force=TimeInForce.GTC
            )
            profit_order_result = self.alpaca.submit_order(profit_order)
            logger.info(f"🎯 Take profit order placed: {profit_order_result.id} @ ${target_price:.2f}")
            
            if main_order_id in self._order_tracker:
                self._order_tracker[main_order_id]['stop_order_id'] = stop_order_result.id
                self._order_tracker[main_order_id]['profit_order_id'] = profit_order_result.id
        except Exception as e:
            logger.warning(f"Could not place stop loss/take profit orders: {e}")
    
    def _track_order(self, order, signal: Dict, order_details: Dict):
        """Track order in internal tracker"""
        self._order_tracker[order.id] = {
            'symbol': order_details['symbol'],
            'side': order_details['side'].value,
            'qty': order_details['qty'],
            'entry_price': order_details['entry_price'],
            'signal': signal,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _log_order_execution(self, order_details: Dict, account, action: str):
        """Log order execution details"""
        symbol = order_details['symbol']
        qty = order_details['qty']
        entry_price = order_details['entry_price']
        side = order_details['side']
        
        if order_details.get('is_closing'):
            logger.info(f"✅ {side.value} {qty} {symbol} @ ${entry_price:.2f} (closing position)")
        else:
            position_value = qty * entry_price
            position_size_pct = (position_value / float(account.buying_power)) * 100 if action == 'BUY' else 0
            order_type = "LIMIT" if self.config.get('use_limit_orders', False) else "MARKET"
            logger.info(f"✅ {order_type} {side.value} {qty} {symbol} @ ${entry_price:.2f} (${position_value:,.2f}, {position_size_pct:.1f}% of buying power)")
    
    def _execute_sim(self, signal):
        logger.info(f"✅ SIM: {signal['action']} {signal['symbol']} @ ${signal.get('entry_price', 0):.2f}")
        return f"SIM_{int(datetime.utcnow().timestamp())}"
    
    def get_order_status(self, order_id):
        """Get order status and verify execution"""
        if not self.alpaca_enabled:
            return None
        try:
            order = self.alpaca.get_order_by_id(order_id)
            return {
                'id': order.id,
                'symbol': order.symbol,
                'status': str(order.status),
                'side': str(order.side),
                'qty': float(order.qty),
                'filled_qty': float(order.filled_qty) if order.filled_qty else 0,
                'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else None,
                'order_type': str(order.order_type),
                'time_in_force': str(order.time_in_force),
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'updated_at': order.updated_at.isoformat() if order.updated_at else None
            }
        except Exception as e:
            logger.error(f"Error getting order status for {order_id}: {e}")
            return None
    
    def get_all_orders(self, status='all', limit=50):
        """Get all orders with optional status filter"""
        if not self.alpaca_enabled:
            return []
        try:
            from alpaca.trading.requests import GetOrdersRequest
            
            # Build filter request
            filter_request = GetOrdersRequest(limit=limit)
            if status != 'all':
                # Map status string to OrderStatus enum if needed
                filter_request.status = status
            
            orders = self.alpaca.get_orders(filter=filter_request)
            return [self.get_order_status(order.id) for order in orders]
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for a symbol
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Current price or None if unavailable
        """
        if not self.alpaca_enabled:
            # Fallback to yfinance for simulation mode
            try:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="1d", interval="1m")
                if not data.empty:
                    return float(data['Close'].iloc[-1])
            except Exception as e:
                logger.debug(f"Error fetching price for {symbol}: {e}")
            return None
        
        try:
            # Use Alpaca to get latest quote
            from alpaca.data.historical import StockHistoricalDataClient
            from alpaca.data.requests import StockLatestQuoteRequest
            
            # For now, use a simple approach - get latest trade
            # In production, you'd use the Alpaca data API
            try:
                # Try to get from positions first (if we have one)
                positions = self.get_positions()
                for pos in positions:
                    if pos['symbol'] == symbol:
                        return pos.get('current_price')
            except:
                pass
            
            # Fallback to yfinance
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return float(data['Close'].iloc[-1])
            
            return None
        except Exception as e:
            logger.warning(f"Error getting current price for {symbol}: {e}")
            return None
    
    def get_positions(self):
        if not self.alpaca_enabled:
            return []
        try:
            positions = self.alpaca.get_all_positions()
            result = []
            for p in positions:
                # Handle side - convert enum to string
                side_str = str(p.side) if hasattr(p, 'side') else 'LONG'
                if 'LONG' in side_str.upper():
                    side_str = 'LONG'
                elif 'SHORT' in side_str.upper():
                    side_str = 'SHORT'
                
                # Get stop loss and take profit from order tracker if available
                stop_price = None
                target_price = None
                for order_id, order_data in self._order_tracker.items():
                    if order_data.get('symbol') == p.symbol:
                        signal = order_data.get('signal', {})
                        stop_price = signal.get('stop_price')
                        target_price = signal.get('target_price')
                        break
                
                result.append({
                    'symbol': p.symbol,
                    'qty': float(p.qty) if isinstance(p.qty, (int, float)) else float(str(p.qty)),
                    'side': side_str,
                    'entry_price': float(p.avg_entry_price) if isinstance(p.avg_entry_price, (int, float)) else float(str(p.avg_entry_price)),
                    'current_price': float(p.current_price) if isinstance(p.current_price, (int, float)) else float(str(p.current_price)),
                    'pnl_pct': float(p.unrealized_plpc) * 100 if isinstance(p.unrealized_plpc, (int, float)) else float(str(p.unrealized_plpc)) * 100,
                    'stop_price': stop_price,
                    'target_price': target_price
                })
            return result
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def get_account_details(self):
        """Get detailed account information"""
        if not self.alpaca_enabled:
            return None
        try:
            account = self.alpaca.get_account()
            return {
                'account_number': account.account_number,
                'status': account.status,
                'currency': account.currency,
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'equity': float(account.equity),
                'last_equity': float(account.last_equity),
                'day_trading_buying_power': float(account.daytrading_buying_power),
                'pattern_day_trader': account.pattern_day_trader,
                'trading_blocked': account.trading_blocked,
                'transfers_blocked': account.transfers_blocked,
                'account_blocked': account.account_blocked,
                'created_at': account.created_at.isoformat() if account.created_at else None
            }
        except Exception as e:
            logger.error(f"Error getting account details: {e}")
            return None

if __name__ == "__main__":
    # Use dev config path if it exists
    dev_config_path = Path(__file__).parent.parent.parent.parent / 'config.json'
    config_path = str(dev_config_path) if dev_config_path.exists() else None
    
    engine = PaperTradingEngine(config_path=config_path)
    
    if engine.alpaca_enabled:
        print("\n" + "="*60)
        print("📊 ALPACA PORTFOLIO STATUS")
        print("="*60)
        
        # Get account details
        account = engine.get_account_details()
        if account:
            print(f"\n💰 Account Information:")
            print(f"   Account Number: {account['account_number']}")
            print(f"   Status: {account['status']}")
            print(f"   Currency: {account['currency']}")
            print(f"\n💵 Portfolio Value: ${account['portfolio_value']:,.2f}")
            print(f"   Cash: ${account['cash']:,.2f}")
            print(f"   Equity: ${account['equity']:,.2f}")
            print(f"   Buying Power: ${account['buying_power']:,.2f}")
            print(f"   Day Trading Buying Power: ${account['day_trading_buying_power']:,.2f}")
            
            # Calculate daily P&L
            daily_pnl = account['equity'] - account['last_equity']
            daily_pnl_pct = (daily_pnl / account['last_equity'] * 100) if account['last_equity'] > 0 else 0
            print(f"\n📈 Daily P&L: ${daily_pnl:,.2f} ({daily_pnl_pct:+.2f}%)")
            
            print(f"\n🚦 Account Flags:")
            print(f"   Pattern Day Trader: {account['pattern_day_trader']}")
            print(f"   Trading Blocked: {account['trading_blocked']}")
            print(f"   Transfers Blocked: {account['transfers_blocked']}")
            print(f"   Account Blocked: {account['account_blocked']}")
        
        # Get positions
        positions = engine.get_positions()
        print(f"\n📊 Current Positions: {len(positions)}")
        if positions:
            print(f"\n{'Symbol':<10} {'Side':<6} {'Qty':<8} {'Entry':<10} {'Current':<10} {'P&L %':<10}")
            print("-" * 60)
            for pos in positions:
                pnl_sign = "+" if pos['pnl_pct'] >= 0 else ""
                print(f"{pos['symbol']:<10} {pos['side']:<6} {pos['qty']:<8} "
                      f"${pos['entry_price']:<9.2f} ${pos['current_price']:<9.2f} "
                      f"{pnl_sign}{pos['pnl_pct']:<9.2f}%")
        else:
            print("   No open positions")
        
        print("\n" + "="*60 + "\n")
    else:
        print("❌ Alpaca not connected - cannot retrieve portfolio information")
        print("   Check your config.json file and Alpaca credentials")
