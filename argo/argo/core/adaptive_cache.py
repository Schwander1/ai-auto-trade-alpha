#!/usr/bin/env python3
"""
Adaptive Caching Strategy
Intelligent cache TTL based on market hours and volatility
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Tuple, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

# Try to import market hours detection
try:
    import pytz
    ET = pytz.timezone('US/Eastern')
    MARKET_OPEN = 9.5  # 9:30 AM
    MARKET_CLOSE = 16.0  # 4:00 PM
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False
    logger.warning("pytz not available - using UTC for market hours")

class AdaptiveCache:
    """Adaptive caching with market-hours aware TTL"""
    
    def __init__(self):
        self.price_history: Dict[str, list] = defaultdict(list)  # Track price changes
        self.volatility: Dict[str, float] = {}  # Track volatility per symbol
    
    def is_market_hours(self) -> bool:
        """Check if current time is within market hours (9:30 AM - 4:00 PM ET)"""
        if not HAS_PYTZ:
            return True  # Assume market hours if pytz not available
        
        try:
            now_et = datetime.now(ET)
            current_hour = now_et.hour + now_et.minute / 60.0
            is_weekday = now_et.weekday() < 5  # Monday = 0, Friday = 4
            return is_weekday and MARKET_OPEN <= current_hour < MARKET_CLOSE
        except Exception:
            return True  # Default to market hours on error
    
    def get_cache_ttl(self, symbol: str, is_market_hours: bool = None, base_ttl: int = 10) -> int:
        """
        Calculate adaptive cache TTL based on:
        - Market hours (stocks) vs 24/7 (crypto)
        - Volatility (high volatility = shorter cache)
        - Time of day
        
        OPTIMIZED: Crypto symbols always use shorter cache for 24/7 trading
        """
        if is_market_hours is None:
            is_market_hours = self.is_market_hours()
        
        # Crypto symbols (24/7) - always active, use shorter cache
        if '-USD' in symbol or symbol in ['BTC', 'ETH', 'SOL']:
            # Crypto markets are 24/7, so use shorter cache for real-time data
            # During high volatility periods, cache even shorter
            if symbol in self.volatility and self.volatility[symbol] > 0.05:
                return base_ttl  # 10 seconds during high volatility
            return base_ttl * 2  # 20 seconds during normal volatility (optimized from 30s)
        
        # Stock symbols (market hours)
        if is_market_hours:
            # During market hours, cache shorter for active trading
            if symbol in self.volatility and self.volatility[symbol] > 0.03:
                return base_ttl  # 10 seconds
            return base_ttl * 2  # 20 seconds
        else:
            # Off-hours: cache much longer
            return base_ttl * 30  # 5 minutes off-hours
    
    def should_refresh(self, symbol: str, cached_data, current_price: Optional[float] = None) -> bool:
        """
        Determine if cache should be refreshed based on price movement
        """
        if current_price is None:
            return True  # No price data, refresh
        
        # Track price history
        self.price_history[symbol].append(current_price)
        if len(self.price_history[symbol]) > 20:
            self.price_history[symbol].pop(0)
        
        # Calculate recent volatility
        if len(self.price_history[symbol]) >= 5:
            prices = self.price_history[symbol][-5:]
            price_changes = [abs(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            self.volatility[symbol] = sum(price_changes) / len(price_changes)
        
        # If price changed significantly, refresh cache
        if cached_data and len(self.price_history[symbol]) >= 2:
            last_price = self.price_history[symbol][-2]
            price_change = abs(current_price - last_price) / last_price
            if price_change > 0.005:  # 0.5% change threshold
                return True
        
        return False

