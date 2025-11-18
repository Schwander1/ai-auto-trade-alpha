#!/usr/bin/env python3
"""Alpine Analytics Paper Trading Engine"""
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlpinePaperTrading")

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.enums import OrderClass, OrderSide, TimeInForce
    from alpaca.trading.requests import (
        LimitOrderRequest,
        MarketOrderRequest,
        StopLossRequest,
        TakeProfitRequest,
    )

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
        # OPTIMIZATION: Initialize caches
        self._volatility_cache = {}  # {symbol: (volatility, timestamp)}
        self._volatility_cache_ttl = 3600  # 1 hour cache
        self._account_cache = None
        self._account_cache_time = None
        self._account_cache_ttl = 30  # 30 second cache for account data
        self._positions_cache = None
        self._positions_cache_time = None
        self._positions_cache_ttl = 10  # 10 second cache for positions
        # OPTIMIZATION: Order tracker cleanup configuration
        self._order_tracker_max_size = 1000  # Max orders to track
        self._order_tracker_cleanup_age = 86400  # Clean up orders older than 24 hours

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
                    self.config = self.full_config.get("trading", {})

                    # Check for prop firm mode
                    prop_firm_config = self.full_config.get("prop_firm", {})
                    self.prop_firm_enabled = prop_firm_config.get("enabled", False)
                    self.prop_firm_config = prop_firm_config if self.prop_firm_enabled else None

                    if self.prop_firm_enabled:
                        logger.info("🏢 PROP FIRM MODE ENABLED")
                        risk_limits = prop_firm_config.get("risk_limits", {})
                        logger.info(f"   Max Drawdown: {risk_limits.get('max_drawdown_pct', 2.0)}%")
                        logger.info(
                            f"   Daily Loss Limit: {risk_limits.get('daily_loss_limit_pct', 4.5)}%"
                        )
                        logger.info(
                            f"   Max Position Size: {risk_limits.get('max_position_size_pct', 3.0)}%"
                        )
                        logger.info(
                            f"   Min Confidence: {risk_limits.get('min_confidence', 82.0)}%"
                        )
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
        env_path = os.getenv("ARGO_CONFIG_PATH")
        if env_path and os.path.exists(env_path):
            return env_path

        # Check current working directory first (for prop firm service)
        cwd_config = Path.cwd() / "config.json"
        if cwd_config.exists():
            return str(cwd_config)

        # Check production paths
        for prod_path in [
            "/root/argo-production-prop-firm/config.json",  # Prop firm service
            "/root/argo-production-green/config.json",
            "/root/argo-production-blue/config.json",
            "/root/argo-production/config.json",
        ]:
            if os.path.exists(prod_path):
                return prod_path

        # Check dev path
        dev_path = Path(__file__).parent.parent.parent / "config.json"
        if dev_path.exists():
            return str(dev_path)

        # Fallback to workspace root
        workspace_path = Path(__file__).parent.parent.parent.parent / "config.json"
        if workspace_path.exists():
            return str(workspace_path)

        return "/root/argo-production/config.json"

    def _resolve_credentials(self, config_path) -> Dict[str, Optional[str]]:
        """Resolve Alpaca credentials from multiple sources"""
        credentials = {"api_key": None, "secret_key": None, "paper": True, "account_name": None}

        # Try AWS Secrets Manager first
        secrets_manager_creds = {}
        if SECRETS_MANAGER_AVAILABLE:
            secrets_manager_creds = self._get_credentials_from_secrets_manager()
            # Validate AWS Secrets Manager credentials before using them
            if secrets_manager_creds.get("api_key") and secrets_manager_creds.get("secret_key"):
                # Test if credentials work
                if self._validate_credentials(
                    secrets_manager_creds["api_key"],
                    secrets_manager_creds["secret_key"],
                    secrets_manager_creds.get("paper", True),
                ):
                    credentials.update(secrets_manager_creds)
                    logger.info("✅ Using credentials from AWS Secrets Manager")
                else:
                    logger.warning(
                        "⚠️  AWS Secrets Manager credentials failed validation, falling back to config.json"
                    )
                    secrets_manager_creds = {}  # Clear invalid credentials

        # Fallback to config.json
        if not credentials["api_key"] or not credentials["secret_key"]:
            config_path = self._find_config_path(config_path)
            config_creds = self._get_credentials_from_config(config_path)
            credentials["api_key"] = credentials["api_key"] or config_creds["api_key"]
            credentials["secret_key"] = credentials["secret_key"] or config_creds["secret_key"]
            credentials["account_name"] = (
                credentials["account_name"] or config_creds["account_name"]
            )
            credentials["paper"] = config_creds.get("paper", credentials["paper"])

        # Final fallback to environment variables
        credentials["api_key"] = credentials["api_key"] or os.getenv("ALPACA_API_KEY")
        credentials["secret_key"] = credentials["secret_key"] or os.getenv("ALPACA_SECRET_KEY")
        credentials["account_name"] = (
            credentials["account_name"] or f"{self.environment.title()} Account"
        )

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
        credentials = {"api_key": None, "secret_key": None, "paper": True}

        try:
            service = "argo"
            if self.environment == "development":
                credentials["api_key"] = get_secret(
                    "alpaca-api-key-dev", service=service
                ) or get_secret("alpaca-api-key", service=service)
                credentials["secret_key"] = get_secret(
                    "alpaca-secret-key-dev", service=service
                ) or get_secret("alpaca-secret-key", service=service)
            else:  # production
                credentials["api_key"] = get_secret(
                    "alpaca-api-key-production", service=service
                ) or get_secret("alpaca-api-key", service=service)
                credentials["secret_key"] = get_secret(
                    "alpaca-secret-key-production", service=service
                ) or get_secret("alpaca-secret-key", service=service)

            paper_mode = get_secret("alpaca-paper", service=service, default="true")
            credentials["paper"] = paper_mode.lower() == "true" if paper_mode else True
        except Exception as e:
            logger.warning(f"Failed to get Alpaca credentials from AWS Secrets Manager: {e}")

        return credentials

    def _get_credentials_from_config(self, config_path: Optional[str]) -> Dict[str, Optional[str]]:
        """Get credentials from config.json"""
        credentials = {"api_key": None, "secret_key": None, "account_name": None, "paper": True}

        if not config_path or not os.path.exists(config_path):
            return credentials

        try:
            with open(config_path) as f:
                config = json.load(f)
                alpaca_config = config.get("alpaca", {})

                # Update trading config if not already loaded
                if not self.config:
                    self.config = config.get("trading", {})

                # PROP FIRM: Check if prop firm mode is enabled and use prop firm account
                prop_firm_config = config.get("prop_firm", {})
                prop_firm_enabled = prop_firm_config.get("enabled", False)
                prop_firm_account_name = prop_firm_config.get("account", "prop_firm_test")

                if prop_firm_enabled and prop_firm_account_name in alpaca_config:
                    # Use prop firm test account
                    prop_firm_account = alpaca_config[prop_firm_account_name]
                    api_key = prop_firm_account.get("api_key")
                    secret_key = prop_firm_account.get("secret_key")

                    if not api_key or not secret_key:
                        logger.error(
                            f"❌ Prop firm account '{prop_firm_account_name}' missing credentials"
                        )
                        # Fall through to standard account selection
                    else:
                        credentials.update(
                            {
                                "api_key": api_key,
                                "secret_key": secret_key,
                                "account_name": prop_firm_account.get(
                                    "account_name", "Prop Firm Test Account"
                                ),
                                "paper": prop_firm_account.get("paper", True),
                            }
                        )
                        logger.info(f"🏢 PROP FIRM MODE: Using {credentials['account_name']}")
                        logger.info(f"   Account: {prop_firm_account_name}")
                        return credentials

                # Standard account selection (dev/production)
                if isinstance(alpaca_config, dict):
                    if self.environment == "production" and "production" in alpaca_config:
                        env_config = alpaca_config["production"]
                        credentials.update(
                            {
                                "api_key": env_config.get("api_key"),
                                "secret_key": env_config.get("secret_key"),
                                "account_name": env_config.get(
                                    "account_name", "Production Trading Account"
                                ),
                            }
                        )
                        logger.info(
                            f"📊 Using Production paper account: {credentials['account_name']}"
                        )
                    elif self.environment == "development" and "dev" in alpaca_config:
                        env_config = alpaca_config["dev"]
                        credentials.update(
                            {
                                "api_key": env_config.get("api_key"),
                                "secret_key": env_config.get("secret_key"),
                                "account_name": env_config.get(
                                    "account_name", "Dev Trading Account"
                                ),
                            }
                        )
                        logger.info(f"📊 Using Dev paper account: {credentials['account_name']}")
                    else:
                        # Fallback to legacy structure
                        credentials["api_key"] = alpaca_config.get("api_key")
                        credentials["secret_key"] = alpaca_config.get("secret_key")
                        logger.info("📊 Using legacy/default Alpaca account")

                    credentials["paper"] = alpaca_config.get("paper", True)
        except Exception as e:
            logger.warning(f"Failed to load credentials from config.json: {e}")

        return credentials

    def _init_alpaca_client(self, credentials: Dict):
        """Initialize Alpaca trading client"""
        if not (ALPACA_AVAILABLE and credentials["api_key"] and credentials["secret_key"]):
            logger.warning("Alpaca not configured - simulation mode")
            self.alpaca_enabled = False
            self._order_tracker = {}
            self._retry_attempts = 3
            self._retry_delay = 1
            return

        try:
            self.alpaca = TradingClient(
                credentials["api_key"], credentials["secret_key"], paper=credentials["paper"]
            )
            account = self.alpaca.get_account()
            self.account_name = credentials["account_name"]
            logger.info(f"✅ Alpaca connected ({self.environment}) | Account: {self.account_name}")
            logger.info(
                f"   Portfolio: ${float(account.portfolio_value):,.2f} | Buying Power: ${float(account.buying_power):,.2f}"
            )
            self.alpaca_enabled = True
            self._order_tracker = {}
            self._retry_attempts = self.config.get("max_retry_attempts", 3)
            self._retry_delay = self.config.get("retry_delay_seconds", 1)
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
        """Calculate asset volatility (ATR-based) for position sizing with caching

        OPTIMIZATION: Caches volatility calculations to reduce yfinance API calls
        """
        # Check cache first
        current_time = time.time()
        if symbol in self._volatility_cache:
            cached_volatility, cache_time = self._volatility_cache[symbol]
            if (current_time - cache_time) < self._volatility_cache_ttl:
                logger.debug(f"Using cached volatility for {symbol}: {cached_volatility:.4f}")
                return cached_volatility

        try:
            from datetime import datetime, timedelta

            # Use yfinance as fallback for volatility calculation
            import yfinance as yf
            from alpaca.data.historical import StockHistoricalDataClient
            from alpaca.data.requests import StockBarsRequest
            from alpaca.data.timeframe import TimeFrame

            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=f"{days}d")

            if hist.empty or len(hist) < 2:
                volatility = 0.02  # Default 2% volatility
            else:
                # Calculate ATR (Average True Range) approximation
                high_low = (hist["High"] - hist["Low"]).mean()
                high_close = (hist["High"] - hist["Close"].shift()).abs().mean()
                low_close = (hist["Low"] - hist["Close"].shift()).abs().mean()

                tr = max(high_low, high_close, low_close)
                atr_pct = (tr / hist["Close"].mean()) if hist["Close"].mean() > 0 else 0.02
                volatility = max(0.01, min(0.10, atr_pct))  # Clamp between 1% and 10%

            # Cache the result
            self._volatility_cache[symbol] = (volatility, current_time)

            # Cleanup old cache entries (keep last 100 symbols)
            if len(self._volatility_cache) > 100:
                # Remove oldest entries
                sorted_cache = sorted(
                    self._volatility_cache.items(), key=lambda x: x[1][1]  # Sort by timestamp
                )
                for old_symbol, _ in sorted_cache[:-100]:
                    del self._volatility_cache[old_symbol]

            return volatility
        except Exception as e:
            logger.debug(f"Could not calculate volatility for {symbol}: {e}")
            # Cache the default value too (with shorter TTL)
            default_volatility = 0.02
            self._volatility_cache[symbol] = (default_volatility, current_time)
            return default_volatility

    def execute_signal(
        self, signal, retry_count=0, existing_positions: Optional[List[Dict]] = None
    ):
        """Execute signal with retry logic and exponential backoff"""
        if self.alpaca_enabled:
            try:
                return self._execute_live(signal, existing_positions)
            except Exception as e:
                error_msg = str(e).lower()
                is_rate_limit = "rate limit" in error_msg or "429" in error_msg

                if retry_count < self._retry_attempts:
                    # OPTIMIZATION: Exponential backoff with longer delay for rate limits
                    if is_rate_limit:
                        # Rate limits: longer backoff (2^retry_count seconds, max 30s)
                        delay = min(2 ** retry_count, 30)
                        logger.warning(
                            f"Rate limit hit for {signal.get('symbol')}, waiting {delay}s before retry {retry_count + 1}/{self._retry_attempts}"
                        )
                    else:
                        # Other errors: standard exponential backoff
                        delay = self._retry_delay * (retry_count + 1)
                        logger.warning(
                            f"Retry {retry_count + 1}/{self._retry_attempts} for {signal.get('symbol')}: {e}"
                        )

                    logger.debug(f"Waiting {delay}s before retry...")
                    time.sleep(delay)
                    return self.execute_signal(signal, retry_count + 1, existing_positions)
                else:
                    logger.error(f"Max retries exceeded for {signal.get('symbol')}: {e}")
                    return None
        return self._execute_sim(signal)

    def _get_cached_account(self):
        """Get account data with caching to reduce API calls"""
        current_time = time.time()

        # Check if cache is valid
        if (
            self._account_cache is not None
            and self._account_cache_time is not None
            and (current_time - self._account_cache_time) < self._account_cache_ttl
        ):
            return self._account_cache

        # Fetch fresh account data
        account = self.alpaca.get_account()
        self._account_cache = account
        self._account_cache_time = current_time

        return account

    def _invalidate_account_cache(self):
        """Invalidate account cache (call after trades)"""
        self._account_cache = None
        self._account_cache_time = None

    def _invalidate_positions_cache(self):
        """Invalidate positions cache (call after trades)"""
        self._positions_cache = None
        self._positions_cache_time = None

    def _check_connection_health(self) -> bool:
        """Check if Alpaca connection is healthy"""
        if not self.alpaca_enabled:
            return False
        try:
            # Quick health check - get account status
            account = self._get_cached_account()
            return account is not None and not account.trading_blocked
        except Exception as e:
            logger.warning(f"Connection health check failed: {e}")
            # Invalidate caches on connection failure
            self._invalidate_account_cache()
            self._invalidate_positions_cache()
            return False

    def _convert_symbol_for_alpaca(self, symbol: str) -> str:
        """Convert symbol format for Alpaca API
        Alpaca uses different formats:
        - Crypto: BTC-USD -> BTCUSD, ETH-USD -> ETHUSD
        - Stocks: No conversion needed
        """
        if '-USD' in symbol:
            # Convert crypto format: BTC-USD -> BTCUSD
            return symbol.replace('-USD', 'USD')
        return symbol

    def _execute_live(self, signal, existing_positions: Optional[List[Dict]] = None):
        """Execute live trade through Alpaca"""
        try:
            symbol, action = signal["symbol"], signal["action"]
            # FIX: Convert symbol format for Alpaca API (crypto symbols need conversion)
            alpaca_symbol = self._convert_symbol_for_alpaca(symbol)

            # FIX: Check connection health before proceeding
            if not self._check_connection_health():
                logger.error(f"❌ Connection health check failed, cannot execute trade for {symbol}")
                return None

            if not self._is_trade_allowed(symbol):
                return None

            # OPTIMIZATION: Use cached account data to avoid multiple API calls
            account = self._get_cached_account()
            if not account:
                logger.error(f"❌ Failed to get account data for {symbol}")
                return None

            order_details = self._prepare_order_details(signal, account, action, existing_positions)
            if not order_details:
                return None

            # FIX: Update symbol in order_details to use Alpaca format
            order_details["symbol"] = alpaca_symbol
            if symbol != alpaca_symbol:
                logger.debug(f"🔄 Converted symbol {symbol} -> {alpaca_symbol} for Alpaca API")

            # FIX: Validate minimum order size (crypto allows fractional, stocks need whole shares)
            is_crypto = '-USD' in symbol
            if is_crypto:
                min_qty = 0.000001  # Crypto minimum
                if order_details["qty"] < min_qty:
                    logger.warning(
                        f"⚠️  Order quantity {order_details['qty']} is below minimum ({min_qty}) for {symbol}"
                    )
                    return None
            else:
                # Stocks require whole shares
                if order_details["qty"] < 1:
                    logger.warning(
                        f"⚠️  Order quantity {order_details['qty']} is below minimum (1 share) for {symbol}"
                    )
                    return None

            order = self._submit_main_order(order_details)
            if not order:
                return None

            self._track_order(order, signal, order_details)

            # OPTIMIZATION: Only check order status if bracket orders are needed
            # This reduces unnecessary API calls when bracket orders aren't required
            bracket_success = True
            if order_details.get("place_bracket"):
                # Verify order was accepted before placing bracket orders
                # Note: For market orders, status might be 'filled' immediately
                # For limit orders, status might be 'new' or 'accepted'
                order_status = self.get_order_status(order.id)
                if order_status:
                    status = order_status.get("status", "").lower()
                    if status in ["rejected", "canceled", "expired"]:
                        logger.error(f"❌ Order {order.id} was {status} for {symbol}")
                        return None
                    elif status == "filled":
                        logger.debug(f"✅ Order {order.id} filled immediately for {symbol}")
                    elif status in ["new", "accepted", "pending_new"]:
                        logger.debug(
                            f"⏳ Order {order.id} {status} for {symbol}, proceeding with bracket orders"
                        )
                    else:
                        logger.debug(f"📊 Order {order.id} status: {status} for {symbol}")

                # FIX: Place bracket orders with error handling
                bracket_success = self._place_bracket_orders(symbol, order_details, order.id)
                if not bracket_success:
                    logger.error(
                        f"❌ Bracket orders failed for {symbol}, main order {order.id} placed without protection"
                    )
                    # Note: We don't cancel the main order here as it may have already filled
                    # Instead, we log the error and track it for manual intervention
                    # FIX: Still return order.id even if brackets failed - order was placed successfully

            # Invalidate caches after trade
            self._invalidate_account_cache()
            self._invalidate_positions_cache()

            self._log_order_execution(order_details, account, action)

            # FIX: Always return order.id if order was placed, even if bracket orders failed
            # The main order was successful, bracket orders are protection but not required
            return order.id

        except Exception as e:
            logger.error(f"Order failed for {signal.get('symbol', 'unknown')}: {e}")
            import traceback

            logger.debug(traceback.format_exc())
            # Invalidate caches on error to ensure fresh data next time
            self._invalidate_account_cache()
            self._invalidate_positions_cache()
            return None

    def _is_trade_allowed(self, symbol: str) -> bool:
        """Check if trade is allowed (market hours, etc.)"""
        if not self.is_market_open() and not symbol.endswith("-USD"):
            logger.warning(f"⏭️  Market is closed - skipping {symbol}")
            return False
        return True

    def _prepare_order_details(
        self, signal: Dict, account, action: str, existing_positions: Optional[List[Dict]] = None
    ) -> Optional[Dict]:
        """Prepare order details including quantity and side"""
        entry_price = signal.get("entry_price", 100)
        confidence = signal.get("confidence", 75)
        stop_price = signal.get("stop_price")
        target_price = signal.get("target_price")

        # PROP FIRM: Enforce max stop loss limit
        if self.prop_firm_enabled and self.prop_firm_config:
            max_stop_loss_pct = self.prop_firm_config.get("risk_limits", {}).get(
                "max_stop_loss_pct", 1.5
            )
            if stop_price:
                if action == "BUY":
                    stop_loss_pct = ((entry_price - stop_price) / entry_price) * 100
                else:  # SELL
                    stop_loss_pct = ((stop_price - entry_price) / entry_price) * 100

                if stop_loss_pct > max_stop_loss_pct:
                    # Adjust stop loss to max allowed
                    if action == "BUY":
                        stop_price = entry_price * (1 - max_stop_loss_pct / 100)
                    else:  # SELL
                        stop_price = entry_price * (1 + max_stop_loss_pct / 100)
                    logger.warning(
                        f"⚠️  Prop firm: Stop loss adjusted to {max_stop_loss_pct}% limit (was {stop_loss_pct:.2f}%)"
                    )

        if action == "SELL":
            return self._prepare_sell_order_details(
                signal, account, entry_price, stop_price, target_price, existing_positions
            )
        else:
            return self._prepare_buy_order_details(
                signal, account, entry_price, confidence, stop_price, target_price, existing_positions
            )

    def _prepare_sell_order_details(
        self,
        signal: Dict,
        account,
        entry_price: float,
        stop_price: Optional[float],
        target_price: Optional[float],
        existing_positions: Optional[List[Dict]] = None,
    ) -> Optional[Dict]:
        """Prepare details for SELL order (close position or new short)"""
        symbol = signal["symbol"]
        # OPTIMIZATION: Use provided positions cache to avoid race condition
        if existing_positions is not None:
            positions = existing_positions
        else:
            positions = self.get_positions()
        existing_position = next((p for p in positions if p["symbol"] == symbol), None)

        if existing_position:
            qty = abs(int(existing_position["qty"]))
            side = OrderSide.SELL if existing_position["side"] == "LONG" else OrderSide.BUY
            logger.info(f"🔄 Closing position: {existing_position['side']} {qty} {symbol}")
            return {
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "entry_price": entry_price,
                "is_closing": True,
                "place_bracket": False,
            }
        else:
            qty, side = self._calculate_position_size(signal, account, entry_price)
            return {
                "symbol": symbol,
                "qty": qty,
                "side": OrderSide.SELL,
                "entry_price": entry_price,
                "stop_price": stop_price,
                "target_price": target_price,
                "is_closing": False,
                "place_bracket": True,
            }

    def _prepare_buy_order_details(
        self,
        signal: Dict,
        account,
        entry_price: float,
        confidence: float,
        stop_price: Optional[float],
        target_price: Optional[float],
        existing_positions: Optional[List[Dict]] = None,
    ) -> Optional[Dict]:
        """Prepare details for BUY order (close SHORT position or new LONG)"""
        symbol = signal["symbol"]
        # OPTIMIZATION: Use provided positions cache to avoid race condition
        if existing_positions is not None:
            positions = existing_positions
        else:
            positions = self.get_positions()
        existing_position = next((p for p in positions if p["symbol"] == symbol), None)

        # FIX: Check if we need to close a SHORT position
        if existing_position and existing_position.get("side", "LONG").upper() == "SHORT":
            qty = abs(int(existing_position["qty"]))
            logger.info(f"🔄 Closing SHORT position: {qty} {symbol}")
            return {
                "symbol": symbol,
                "qty": qty,
                "side": OrderSide.BUY,  # BUY to close SHORT
                "entry_price": entry_price,
                "is_closing": True,
                "place_bracket": False,
            }

        # Handle manual/test trades with specified quantity
        signal_qty = signal.get("qty") or signal.get("filled_qty")
        if signal_qty and signal_qty > 0:
            logger.info(f"📝 Using qty from signal: {int(signal_qty)} (test/manual trade)")
            return {
                "symbol": signal["symbol"],
                "qty": int(signal_qty),
                "side": OrderSide.BUY,
                "entry_price": entry_price,
                "is_closing": False,
                "place_bracket": False,
            }

        # Calculate position size for new LONG position
        qty, side = self._calculate_position_size(signal, account, entry_price)
        return {
            "symbol": signal["symbol"],
            "qty": qty,
            "side": OrderSide.BUY,
            "entry_price": entry_price,
            "stop_price": stop_price,
            "target_price": target_price,
            "is_closing": False,
            "place_bracket": True,
        }

    def _calculate_position_size(
        self, signal: Dict, account, entry_price: float
    ) -> Tuple[int, OrderSide]:
        """Calculate position size based on confidence, volatility, and config

        Returns:
            Tuple of (quantity, side) where quantity is guaranteed >= 1 if valid
        """
        # PROP FIRM: Use prop firm limits if enabled
        # OPTIMIZATION: prop_firm_enabled is initialized in __init__, no need for hasattr
        if self.prop_firm_enabled and self.prop_firm_config:
            risk_limits = self.prop_firm_config.get("risk_limits", {})
            base_position_size_pct = risk_limits.get("max_position_size_pct", 3.0)
            max_position_size_pct = base_position_size_pct  # Prop firm: fixed size
            min_confidence = risk_limits.get("min_confidence", 82.0)
            confidence = signal.get("confidence", 75)

            # Prop firm: Reject if confidence too low
            if confidence < min_confidence:
                logger.warning(
                    f"⚠️  Prop firm: Confidence {confidence:.2f}% < {min_confidence}% minimum"
                )
                return 0, OrderSide.BUY

            # Prop firm: Fixed position size (no scaling)
            position_size_pct = base_position_size_pct
        else:
            # Standard mode: Dynamic position sizing
            base_position_size_pct = self.config.get("position_size_pct", 10)
            max_position_size_pct = self.config.get("max_position_size_pct", 15)
            confidence = signal.get("confidence", 75)

            # OPTIMIZATION: Cache volatility calculation (could be async in future)
            volatility = self.get_asset_volatility(signal["symbol"])
            avg_volatility = 0.02
            volatility_multiplier = min(avg_volatility / volatility if volatility > 0 else 1.0, 1.5)

            # Scale by confidence
            if confidence >= 75:
                confidence_multiplier = 1.0 + ((confidence - 75) / 25) * 0.5
                position_size_pct = min(
                    base_position_size_pct * confidence_multiplier * volatility_multiplier,
                    max_position_size_pct,
                )
            else:
                position_size_pct = base_position_size_pct * 0.75 * volatility_multiplier

        buying_power = float(account.buying_power)
        
        # FIX: Validate buying power is positive
        if buying_power <= 0:
            logger.warning(f"⚠️  Invalid buying power: ${buying_power:,.2f} for {signal['symbol']}")
            return 0, OrderSide.BUY
        
        # OPTIMIZATION: Log position sizing details for debugging
        logger.debug(f"🔍 Position sizing for {signal['symbol']}: buying_power=${buying_power:,.2f}, entry_price=${entry_price:.2f}, position_size_pct={position_size_pct:.3f}%")

        # FIX: Validate entry price is positive
        if entry_price <= 0:
            logger.warning(f"⚠️  Invalid entry price: ${entry_price:.2f}")
            return 0, OrderSide.BUY

        # FIX: For crypto (especially expensive ones like BTC), use smaller position size
        is_crypto = '-USD' in signal['symbol']
        if is_crypto and entry_price > 10000:
            # For expensive crypto (BTC, etc.), ensure we can afford at least minimum quantity
            # Calculate minimum position value needed for minimum qty
            min_qty_value = 0.000001 * entry_price  # Minimum crypto qty * price
            min_position_pct_needed = (min_qty_value / buying_power) * 100
            
            # Use the larger of: calculated position size or minimum needed
            if position_size_pct < min_position_pct_needed:
                position_size_pct = min(min_position_pct_needed, 1.0)  # Cap at 1% for safety
                logger.debug(f"🔧 Adjusted position size to {position_size_pct:.3f}% for expensive crypto {signal['symbol']} (min needed: {min_position_pct_needed:.3f}%)")
        
        position_value = buying_power * (position_size_pct / 100)
        
        # OPTIMIZATION: For very expensive assets, ensure minimum position value
        if is_crypto and entry_price > 10000:
            min_qty_value = 0.000001 * entry_price
            if position_value < min_qty_value:
                # Ensure we can afford minimum qty
                if min_qty_value <= buying_power * 0.95:
                    position_value = min_qty_value
                    logger.debug(f"🔧 Adjusted position value to ${position_value:.2f} to meet minimum qty requirement for {signal['symbol']}")
                else:
                    # Cannot afford minimum - will return 0 later
                    logger.debug(f"⚠️  Cannot afford minimum position value ${min_qty_value:.2f} for {signal['symbol']} with buying power ${buying_power:.2f}")

        # FIX: Ensure position value doesn't exceed available buying power (with 5% buffer)
        max_position_value = buying_power * 0.95  # Leave 5% buffer for fees/margin
        if position_value > max_position_value:
            logger.warning(
                f"⚠️  Position value ${position_value:,.2f} exceeds available buying power "
                f"${max_position_value:,.2f}, capping to available funds"
            )
            position_value = max_position_value
        
        # FIX: Ensure position_value is never zero if we have buying power (for crypto, use minimum qty value)
        if position_value <= 0 and buying_power > 0:
            if is_crypto:
                min_qty_value = 0.000001 * entry_price
                if min_qty_value <= buying_power * 0.95:
                    position_value = min_qty_value
                    logger.debug(f"🔧 Position value was 0, using minimum qty value ${position_value:.2f} for {signal['symbol']}")
                else:
                    logger.warning(f"⚠️  Position value is 0 and cannot afford minimum for {signal['symbol']}")
                    return 0, OrderSide.BUY
            else:
                # For stocks, if position_value is 0, we can't afford even 1 share
                logger.warning(f"⚠️  Position value is 0 for {signal['symbol']} - insufficient buying power")
                return 0, OrderSide.BUY

        # FIX: For crypto, calculate quantity with decimal precision (crypto allows fractional shares)
        if is_crypto:
            # Crypto allows fractional quantities, so use float division
            qty = position_value / entry_price
            # Round to 6 decimal places (standard for crypto)
            qty = round(qty, 6)
        else:
            # Stocks require whole shares
            qty = int(position_value / entry_price)

        # FIX: Ensure minimum order size
        if is_crypto:
            # Crypto minimum is typically 0.000001 (1 satoshi for BTC, 0.000001 ETH)
            min_qty = 0.000001
            if qty < min_qty:
                if position_value > 0:
                    logger.warning(
                        f"⚠️  Calculated qty {qty} < minimum {min_qty} for {signal['symbol']}, "
                        f"adjusting to minimum"
                    )
                    qty = min_qty
                else:
                    logger.warning(
                        f"⚠️  Insufficient funds for {signal['symbol']}: "
                        f"need ${entry_price:.2f} for minimum qty, have ${buying_power:,.2f} buying power"
                    )
                    return 0, OrderSide.BUY
        else:
            # Stocks: minimum 1 share
            if qty < 1:
                if position_value > 0:
                    logger.warning(
                        f"⚠️  Calculated qty {qty} < 1 for {signal['symbol']}, adjusting to 1 share"
                    )
                    qty = 1
                else:
                    logger.warning(
                        f"⚠️  Insufficient funds for {signal['symbol']}: "
                        f"need ${entry_price:.2f} for 1 share, have ${buying_power:,.2f} buying power"
                    )
                    return 0, OrderSide.BUY

        # FIX: Final validation - ensure we can actually afford this quantity
        required_capital = qty * entry_price
        if required_capital > buying_power:
            # Adjust qty to fit within buying power
            if is_crypto:
                # For crypto, use 95% of buying power and ensure minimum qty
                max_affordable_qty = round((buying_power * 0.95) / entry_price, 6)
                min_qty = 0.000001
                
                # If we can afford at least minimum qty, use it
                if max_affordable_qty >= min_qty:
                    qty = max_affordable_qty
                    logger.debug(
                        f"🔧 Adjusted qty to {qty} to fit within buying power for {signal['symbol']} "
                        f"(max affordable: {max_affordable_qty})"
                    )
                else:
                    # Even minimum qty is too expensive - check if we can afford it at all
                    min_capital_needed = min_qty * entry_price
                    if min_capital_needed <= buying_power * 0.95:
                        # We can afford minimum, use it
                        qty = min_qty
                        logger.debug(
                            f"🔧 Using minimum qty {qty} for {signal['symbol']} "
                            f"(cost: ${min_capital_needed:.2f}, available: ${buying_power * 0.95:.2f})"
                        )
                    else:
                        logger.warning(
                            f"⚠️  Cannot afford minimum qty ({min_qty}) of {signal['symbol']}: "
                            f"need ${min_capital_needed:.2f}, have ${buying_power * 0.95:.2f} buying power"
                        )
                        return 0, OrderSide.BUY
            else:
                qty = int(buying_power * 0.95 / entry_price)  # Use 95% to leave buffer
                min_qty = 1
                
                if qty < min_qty:
                    logger.warning(
                        f"⚠️  Cannot afford minimum qty ({min_qty}) of {signal['symbol']} "
                        f"with available buying power ${buying_power:,.2f}"
                    )
                    return 0, OrderSide.BUY
                logger.warning(
                    f"⚠️  Adjusted qty to {qty} to fit within buying power for {signal['symbol']}"
                )

        side = OrderSide.BUY if signal["action"] == "BUY" else OrderSide.SELL

        # OPTIMIZATION: Log final calculated quantity for debugging
        if qty > 0:
            logger.debug(f"✅ Position size calculated for {signal['symbol']}: qty={qty}, side={side.value}, cost=${qty * entry_price:.2f}")
        else:
            logger.warning(f"⚠️  Position size calculation returned 0 for {signal['symbol']}: buying_power=${buying_power:,.2f}, entry_price=${entry_price:.2f}, position_size_pct={position_size_pct:.3f}%")

        return qty, side

    def _submit_main_order(self, order_details: Dict):
        """Submit the main order (market or limit) with enhanced error handling"""
        use_limit_orders = self.config.get("use_limit_orders", False)
        limit_offset_pct = self.config.get("limit_order_offset_pct", 0.001)

        if order_details["qty"] == 0:
            logger.warning(
                f"⚠️  Calculated qty is 0 for {order_details['symbol']} (price: ${order_details['entry_price']:.2f})"
            )
            return None

        try:
            if use_limit_orders and not order_details.get("is_closing"):
                limit_price = self._calculate_limit_price(
                    order_details["entry_price"],
                    order_details["side"],
                    limit_offset_pct,
                    order_details.get("symbol")  # Pass symbol for validation
                )
                order_request = LimitOrderRequest(
                    symbol=order_details["symbol"],
                    qty=order_details["qty"],
                    side=order_details["side"],
                    limit_price=limit_price,
                    time_in_force=TimeInForce.DAY,
                )
            else:
                # FIX: For crypto, qty can be float; for stocks, must be int
                qty = order_details["qty"]
                is_crypto = '-USD' in order_details["symbol"] or 'USD' in order_details["symbol"]
                if not is_crypto:
                    # Ensure stocks use integer quantity
                    qty = int(qty)

                order_request = MarketOrderRequest(
                    symbol=order_details["symbol"],
                    qty=qty,
                    side=order_details["side"],
                    time_in_force=TimeInForce.DAY,
                )

            order = self.alpaca.submit_order(order_request)
            return order

        except Exception as e:
            error_msg = str(e).lower()

            # Handle specific Alpaca API errors
            if "insufficient" in error_msg or "buying power" in error_msg:
                logger.error(
                    f"❌ Insufficient buying power for {order_details['symbol']}: {e}"
                )
                # Invalidate account cache to get fresh data
                self._invalidate_account_cache()
            elif "not found" in error_msg or "422" in error_msg or "asset" in error_msg:
                # FIX: Handle asset not found errors (e.g., wrong symbol format)
                logger.error(
                    f"❌ Asset not found for {order_details['symbol']}: {e}. "
                    f"Check if symbol format is correct for Alpaca API."
                )
                # Don't retry - this is a configuration issue
            elif "rate limit" in error_msg or "429" in error_msg:
                logger.warning(f"⚠️  Rate limit hit for {order_details['symbol']}, will retry: {e}")
                # OPTIMIZATION: Rate limit backoff handled by retry logic in execute_signal
                # The retry mechanism will automatically back off with exponential delay
            elif "connection" in error_msg or "timeout" in error_msg:
                logger.error(f"❌ Connection error submitting order for {order_details['symbol']}: {e}")
                # Invalidate caches on connection error
                self._invalidate_account_cache()
                self._invalidate_positions_cache()
            else:
                logger.error(f"❌ Error submitting order for {order_details['symbol']}: {e}")

            raise  # Re-raise to be handled by retry logic

    def _calculate_limit_price(
        self, entry_price: float, side: OrderSide, offset_pct: float, symbol: str = None
    ) -> float:
        """Calculate limit price with offset and validation

        Args:
            entry_price: Entry price from signal
            side: Order side (BUY/SELL)
            offset_pct: Offset percentage (e.g., 0.001 = 0.1%)
            symbol: Optional symbol for market price validation

        Returns:
            Calculated limit price
        """
        if side == OrderSide.BUY:
            limit_price = entry_price * (1 + offset_pct)
        else:
            limit_price = entry_price * (1 - offset_pct)

        # OPTIMIZATION: Validate limit price against current market price if available
        if symbol:
            try:
                current_price = self.get_current_price(symbol)
                if current_price and current_price > 0:
                    # For BUY: limit should be reasonable (not more than 5% above market)
                    # For SELL: limit should be reasonable (not more than 5% below market)
                    if side == OrderSide.BUY:
                        max_limit = current_price * 1.05  # 5% above market
                        if limit_price > max_limit:
                            logger.warning(
                                f"⚠️  Limit price ${limit_price:.2f} > 5% above market ${current_price:.2f} "
                                f"for {symbol}, capping to ${max_limit:.2f}"
                            )
                            limit_price = max_limit
                    else:  # SELL
                        min_limit = current_price * 0.95  # 5% below market
                        if limit_price < min_limit:
                            logger.warning(
                                f"⚠️  Limit price ${limit_price:.2f} < 5% below market ${current_price:.2f} "
                                f"for {symbol}, capping to ${min_limit:.2f}"
                            )
                            limit_price = min_limit
            except Exception as e:
                logger.debug(f"Could not validate limit price against market for {symbol}: {e}")

        return limit_price

    def _validate_bracket_prices(
        self, symbol: str, entry_price: float, stop_price: float, target_price: float, side: OrderSide
    ) -> Tuple[bool, Optional[str]]:
        """Validate stop loss and take profit prices

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate stop loss price
        if side == OrderSide.BUY:
            # For LONG: stop should be below entry, target above entry
            if stop_price >= entry_price:
                return False, f"Stop loss ${stop_price:.2f} must be below entry ${entry_price:.2f} for LONG"
            if target_price <= entry_price:
                return False, f"Take profit ${target_price:.2f} must be above entry ${entry_price:.2f} for LONG"

            # Check stop loss isn't too far (more than 20% below entry)
            stop_loss_pct = ((entry_price - stop_price) / entry_price) * 100
            if stop_loss_pct > 20:
                return False, f"Stop loss ${stop_price:.2f} is {stop_loss_pct:.1f}% below entry, exceeds 20% limit"
        else:  # SELL/SHORT
            # For SHORT: stop should be above entry, target below entry
            if stop_price <= entry_price:
                return False, f"Stop loss ${stop_price:.2f} must be above entry ${entry_price:.2f} for SHORT"
            if target_price >= entry_price:
                return False, f"Take profit ${target_price:.2f} must be below entry ${entry_price:.2f} for SHORT"

            # Check stop loss isn't too far (more than 20% above entry)
            stop_loss_pct = ((stop_price - entry_price) / entry_price) * 100
            if stop_loss_pct > 20:
                return False, f"Stop loss ${stop_price:.2f} is {stop_loss_pct:.1f}% above entry, exceeds 20% limit"

        # Validate target price is reasonable (not more than 50% away)
        if side == OrderSide.BUY:
            target_pct = ((target_price - entry_price) / entry_price) * 100
        else:
            target_pct = ((entry_price - target_price) / entry_price) * 100

        if target_pct > 50:
            return False, f"Take profit ${target_price:.2f} is {target_pct:.1f}% away, exceeds 50% limit"

        return True, None

    def _place_bracket_orders(self, symbol: str, order_details: Dict, main_order_id: str) -> bool:
        """Place stop loss and take profit orders with validation

        Returns:
            True if both orders placed successfully, False otherwise
        """
        qty = order_details["qty"]
        stop_price = order_details.get("stop_price")
        target_price = order_details.get("target_price")
        side = order_details["side"]
        entry_price = order_details.get("entry_price")

        if not (stop_price and target_price):
            logger.debug(f"No stop/target prices provided for {symbol}, skipping bracket orders")
            return True  # Not an error if bracket orders aren't needed

        # FIX: Validate bracket prices before placing orders
        if entry_price:
            is_valid, error_msg = self._validate_bracket_prices(
                symbol, entry_price, stop_price, target_price, side
            )
            if not is_valid:
                logger.error(f"❌ Invalid bracket prices for {symbol}: {error_msg}")
                return False

        stop_order_id = None
        profit_order_id = None
        stop_order_success = False
        profit_order_success = False

        try:
            # OPTIMIZATION: Place stop loss order with retry logic
            max_retries = 2
            retry_delay = 0.5

            for attempt in range(max_retries):
                try:
                    stop_side = OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY
                    stop_order = StopLossRequest(
                        symbol=symbol, qty=qty, stop_price=stop_price, time_in_force=TimeInForce.GTC
                    )
                    stop_order_result = self.alpaca.submit_order(stop_order)
                    stop_order_id = stop_order_result.id
                    stop_order_success = True
                    logger.info(f"🛡️  Stop loss order placed: {stop_order_id} @ ${stop_price:.2f}")
                    break  # Success, exit retry loop
                except Exception as stop_error:
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️  Stop loss order attempt {attempt + 1}/{max_retries} failed for {symbol}, retrying: {stop_error}")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"❌ Failed to place stop loss for {symbol} after {max_retries} attempts: {stop_error}")

            # OPTIMIZATION: Place take profit order with retry logic
            for attempt in range(max_retries):
                try:
                    profit_order = TakeProfitRequest(
                        symbol=symbol, qty=qty, limit_price=target_price, time_in_force=TimeInForce.GTC
                    )
                    profit_order_result = self.alpaca.submit_order(profit_order)
                    profit_order_id = profit_order_result.id
                    profit_order_success = True
                    logger.info(f"🎯 Take profit order placed: {profit_order_id} @ ${target_price:.2f}")
                    break  # Success, exit retry loop
                except Exception as profit_error:
                    if attempt < max_retries - 1:
                        logger.warning(f"⚠️  Take profit order attempt {attempt + 1}/{max_retries} failed for {symbol}, retrying: {profit_error}")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"❌ Failed to place take profit for {symbol} after {max_retries} attempts: {profit_error}")

            # Track bracket orders (even if only one succeeded)
            if main_order_id in self._order_tracker:
                if stop_order_id:
                    self._order_tracker[main_order_id]["stop_order_id"] = stop_order_id
                if profit_order_id:
                    self._order_tracker[main_order_id]["profit_order_id"] = profit_order_id

                # Track partial failures
                if not (stop_order_success and profit_order_success):
                    error_msg = []
                    if not stop_order_success:
                        error_msg.append("stop_loss_failed")
                    if not profit_order_success:
                        error_msg.append("take_profit_failed")
                    self._order_tracker[main_order_id]["bracket_warnings"] = ", ".join(error_msg)

            # Return True only if both orders succeeded
            if stop_order_success and profit_order_success:
                return True
            elif stop_order_success or profit_order_success:
                logger.warning(
                    f"⚠️  Partial bracket order success for {symbol}: "
                    f"stop_loss={'✓' if stop_order_success else '✗'}, "
                    f"take_profit={'✓' if profit_order_success else '✗'}"
                )
                return False
            else:
                return False

        except Exception as e:
            logger.error(f"❌ Unexpected error placing bracket orders for {symbol}: {e}")
            # Track error in order tracker
            if main_order_id in self._order_tracker:
                if stop_order_id:
                    self._order_tracker[main_order_id]["stop_order_id"] = stop_order_id
                if profit_order_id:
                    self._order_tracker[main_order_id]["profit_order_id"] = profit_order_id
                self._order_tracker[main_order_id]["bracket_error"] = str(e)
            return False

    def _track_order(self, order, signal: Dict, order_details: Dict):
        """Track order in internal tracker with automatic cleanup"""
        # OPTIMIZATION: Cache current time to avoid multiple datetime calls
        current_time = datetime.utcnow()
        current_timestamp = current_time.timestamp()

        self._order_tracker[order.id] = {
            "symbol": order_details["symbol"],
            "side": order_details["side"].value,
            "qty": order_details["qty"],
            "entry_price": order_details["entry_price"],
            "signal": signal,
            "timestamp": current_time.isoformat(),
            "order_timestamp": current_timestamp,  # For cleanup
        }

        # OPTIMIZATION: Cleanup old orders if tracker gets too large
        self._cleanup_order_tracker()

    def _cleanup_order_tracker(self):
        """Clean up old orders from tracker to prevent memory leaks (OPTIMIZED)"""
        current_time = time.time()
        tracker_size = len(self._order_tracker)

        # OPTIMIZATION: Only cleanup if tracker is large enough to warrant it
        if tracker_size == 0:
            return

        # Clean up if tracker is too large
        if tracker_size > self._order_tracker_max_size:
            # OPTIMIZATION: Use list of (timestamp, order_id) tuples for efficient sorting
            orders_by_age = [
                (order_data.get("order_timestamp", 0), order_id)
                for order_id, order_data in self._order_tracker.items()
            ]
            orders_by_age.sort()  # Sort by timestamp (oldest first)

            # Remove oldest 20% of orders
            to_remove_count = len(orders_by_age) // 5
            for _, order_id in orders_by_age[:to_remove_count]:
                del self._order_tracker[order_id]

            logger.debug(f"Cleaned up {to_remove_count} old orders from tracker")

        # Also clean up orders older than cleanup age (more efficient iteration)
        to_remove = [
            order_id
            for order_id, order_data in self._order_tracker.items()
            if order_data.get("order_timestamp", 0) > 0
            and (current_time - order_data.get("order_timestamp", 0)) > self._order_tracker_cleanup_age
        ]

        for order_id in to_remove:
            del self._order_tracker[order_id]

        if to_remove:
            logger.debug(f"Cleaned up {len(to_remove)} expired orders from tracker")

    def _log_order_execution(self, order_details: Dict, account, action: str):
        """Log order execution details"""
        symbol = order_details["symbol"]
        qty = order_details["qty"]
        entry_price = order_details["entry_price"]
        side = order_details["side"]

        if order_details.get("is_closing"):
            logger.info(f"✅ {side.value} {qty} {symbol} @ ${entry_price:.2f} (closing position)")
        else:
            position_value = qty * entry_price
            position_size_pct = (
                (position_value / float(account.buying_power)) * 100 if action == "BUY" else 0
            )
            order_type = "LIMIT" if self.config.get("use_limit_orders", False) else "MARKET"
            logger.info(
                f"✅ {order_type} {side.value} {qty} {symbol} @ ${entry_price:.2f} (${position_value:,.2f}, {position_size_pct:.1f}% of buying power)"
            )

    def _execute_sim(self, signal):
        logger.info(
            f"✅ SIM: {signal['action']} {signal['symbol']} @ ${signal.get('entry_price', 0):.2f}"
        )
        return f"SIM_{int(datetime.utcnow().timestamp())}"

    def get_order_status(self, order_id):
        """Get order status and verify execution"""
        if not self.alpaca_enabled:
            return None
        try:
            order = self.alpaca.get_order_by_id(order_id)
            return {
                "id": order.id,
                "symbol": order.symbol,
                "status": str(order.status),
                "side": str(order.side),
                "qty": float(order.qty),
                "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                "filled_avg_price": (
                    float(order.filled_avg_price) if order.filled_avg_price else None
                ),
                "order_type": str(order.order_type),
                "time_in_force": str(order.time_in_force),
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "updated_at": order.updated_at.isoformat() if order.updated_at else None,
            }
        except Exception as e:
            logger.error(f"Error getting order status for {order_id}: {e}")
            return None

    def get_all_orders(self, status="all", limit=50):
        """Get all orders with optional status filter"""
        if not self.alpaca_enabled:
            return []
        try:
            from alpaca.trading.requests import GetOrdersRequest

            # Build filter request
            filter_request = GetOrdersRequest(limit=limit)
            if status != "all":
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
                    return float(data["Close"].iloc[-1])
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
                    if pos["symbol"] == symbol:
                        return pos.get("current_price")
            except:
                pass

            # Fallback to yfinance
            import yfinance as yf

            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return float(data["Close"].iloc[-1])

            return None
        except Exception as e:
            logger.warning(f"Error getting current price for {symbol}: {e}")
            return None

    def get_positions(self, use_cache: bool = True):
        """Get all positions with optional caching

        Args:
            use_cache: If True, use cached positions if available and fresh
        """
        if not self.alpaca_enabled:
            return []

        # OPTIMIZATION: Check cache first
        if use_cache:
            current_time = time.time()
            if (
                self._positions_cache is not None
                and self._positions_cache_time is not None
                and (current_time - self._positions_cache_time) < self._positions_cache_ttl
            ):
                logger.debug("Using cached positions")
                return self._positions_cache

        try:
            positions = self.alpaca.get_all_positions()
            result = []
            for p in positions:
                # FIX: Improved position side detection
                # Alpaca can return side as enum, string, or use negative qty for SHORT
                qty_float = float(p.qty) if isinstance(p.qty, (int, float)) else float(str(p.qty))

                # Determine side: check side attribute first, then qty sign
                if hasattr(p, "side") and p.side is not None:
                    # Alpaca PositionSide enum or string
                    side_attr = str(p.side).upper()
                    if "SHORT" in side_attr or side_attr == "SHORT":
                        side_str = "SHORT"
                    elif "LONG" in side_attr or side_attr == "LONG":
                        side_str = "LONG"
                    else:
                        # Fallback to qty sign if side attribute is unclear
                        side_str = "SHORT" if qty_float < 0 else "LONG"
                else:
                    # No side attribute - use qty sign (negative = SHORT)
                    side_str = "SHORT" if qty_float < 0 else "LONG"

                # Normalize qty to positive value for consistency
                qty_abs = abs(qty_float)

                # Get stop loss and take profit from order tracker if available
                stop_price = None
                target_price = None
                for order_id, order_data in self._order_tracker.items():
                    if order_data.get("symbol") == p.symbol:
                        signal = order_data.get("signal", {})
                        stop_price = signal.get("stop_price")
                        target_price = signal.get("target_price")
                        break

                result.append(
                    {
                        "symbol": p.symbol,
                        "qty": qty_abs,  # Always positive
                        "side": side_str,  # Explicit LONG or SHORT
                        "entry_price": (
                            float(p.avg_entry_price)
                            if isinstance(p.avg_entry_price, (int, float))
                            else float(str(p.avg_entry_price))
                        ),
                        "current_price": (
                            float(p.current_price)
                            if isinstance(p.current_price, (int, float))
                            else float(str(p.current_price))
                        ),
                        "pnl_pct": (
                            float(p.unrealized_plpc) * 100
                            if isinstance(p.unrealized_plpc, (int, float))
                            else float(str(p.unrealized_plpc)) * 100
                        ),
                        "stop_price": stop_price,
                        "target_price": target_price,
                    }
                )

            # Cache the result
            if use_cache:
                self._positions_cache = result
                self._positions_cache_time = time.time()

            return result
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            # Invalidate cache on error
            if use_cache:
                self._invalidate_positions_cache()
            return []

    def get_account_details(self):
        """Get detailed account information with caching"""
        if not self.alpaca_enabled:
            return None
        try:
            # OPTIMIZATION: Use cached account data
            account = self._get_cached_account()
            return {
                "account_number": account.account_number,
                "status": account.status,
                "currency": account.currency,
                "buying_power": float(account.buying_power),
                "cash": float(account.cash),
                "portfolio_value": float(account.portfolio_value),
                "equity": float(account.equity),
                "last_equity": float(account.last_equity),
                "day_trading_buying_power": float(account.daytrading_buying_power),
                "pattern_day_trader": account.pattern_day_trader,
                "trading_blocked": account.trading_blocked,
                "transfers_blocked": account.transfers_blocked,
                "account_blocked": account.account_blocked,
                "created_at": account.created_at.isoformat() if account.created_at else None,
            }
        except Exception as e:
            logger.error(f"Error getting account details: {e}")
            # Invalidate cache on error
            self._invalidate_account_cache()
            return None


if __name__ == "__main__":
    # Use dev config path if it exists
    dev_config_path = Path(__file__).parent.parent.parent.parent / "config.json"
    config_path = str(dev_config_path) if dev_config_path.exists() else None

    engine = PaperTradingEngine(config_path=config_path)

    if engine.alpaca_enabled:
        print("\n" + "=" * 60)
        print("📊 ALPACA PORTFOLIO STATUS")
        print("=" * 60)

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
            daily_pnl = account["equity"] - account["last_equity"]
            daily_pnl_pct = (
                (daily_pnl / account["last_equity"] * 100) if account["last_equity"] > 0 else 0
            )
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
            print(
                f"\n{'Symbol':<10} {'Side':<6} {'Qty':<8} {'Entry':<10} {'Current':<10} {'P&L %':<10}"
            )
            print("-" * 60)
            for pos in positions:
                pnl_sign = "+" if pos["pnl_pct"] >= 0 else ""
                print(
                    f"{pos['symbol']:<10} {pos['side']:<6} {pos['qty']:<8} "
                    f"${pos['entry_price']:<9.2f} ${pos['current_price']:<9.2f} "
                    f"{pnl_sign}{pos['pnl_pct']:<9.2f}%"
                )
        else:
            print("   No open positions")

        print("\n" + "=" * 60 + "\n")
    else:
        print("❌ Alpaca not connected - cannot retrieve portfolio information")
        print("   Check your config.json file and Alpaca credentials")
