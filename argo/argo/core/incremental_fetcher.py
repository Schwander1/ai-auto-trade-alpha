#!/usr/bin/env python3
"""
Incremental Data Fetcher v5.0 - Phase 5
Fetches only changed data instead of full refreshes
Reduces API calls and improves efficiency
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IncrementalFetcher")


class IncrementalFetcher:
    """
    Incremental data fetching service
    Tracks what data has changed and only fetches updates
    """
    
    def __init__(self):
        # Track last fetched data per symbol and source
        self._last_data: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Track last fetch time
        self._last_fetch_time: Dict[str, Dict[str, datetime]] = defaultdict(dict)
        
        # Track change detection thresholds
        self._price_change_threshold = 0.001  # 0.1% price change
        self._indicator_change_threshold = 0.01  # 1% indicator change
    
    def should_fetch(self, symbol: str, source: str, current_data: Optional[Dict] = None) -> bool:
        """
        Determine if data should be fetched based on change detection
        
        Args:
            symbol: Symbol to check
            source: Data source name
            current_data: Current data if available (for comparison)
        
        Returns:
            True if fetch is needed, False if cached data is still valid
        """
        # Always fetch if no previous data
        if symbol not in self._last_data or source not in self._last_data[symbol]:
            return True
        
        # Check if enough time has passed (force refresh every 5 minutes)
        last_fetch = self._last_fetch_time.get(symbol, {}).get(source)
        if last_fetch:
            time_since_fetch = (datetime.utcnow() - last_fetch).total_seconds()
            if time_since_fetch > 300:  # 5 minutes
                return True
        
        # If current_data provided, check if significant changes
        if current_data:
            return self._has_significant_changes(symbol, source, current_data)
        
        # Default: fetch if no current data available
        return True
    
    def _has_significant_changes(self, symbol: str, source: str, current_data: Dict) -> bool:
        """Check if current data has significant changes from last fetched"""
        last_data = self._last_data[symbol].get(source, {})
        
        if not last_data:
            return True
        
        # Check price changes
        if 'price' in current_data and 'price' in last_data:
            price_change = abs(current_data['price'] - last_data['price']) / last_data['price']
            if price_change > self._price_change_threshold:
                return True
        
        # Check indicator changes
        for indicator in ['rsi', 'macd', 'sma', 'ema']:
            if indicator in current_data and indicator in last_data:
                if last_data[indicator] != 0:
                    change = abs(current_data[indicator] - last_data[indicator]) / abs(last_data[indicator])
                    if change > self._indicator_change_threshold:
                        return True
        
        # Check sentiment changes (if available)
        if 'sentiment' in current_data and 'sentiment' in last_data:
            if current_data['sentiment'] != last_data['sentiment']:
                return True
        
        return False
    
    def record_fetch(self, symbol: str, source: str, data: Dict):
        """Record fetched data for change detection"""
        if symbol not in self._last_data:
            self._last_data[symbol] = {}
        
        self._last_data[symbol][source] = data.copy()
        
        if symbol not in self._last_fetch_time:
            self._last_fetch_time[symbol] = {}
        
        self._last_fetch_time[symbol][source] = datetime.utcnow()
    
    def get_last_data(self, symbol: str, source: str) -> Optional[Dict]:
        """Get last fetched data for symbol and source"""
        return self._last_data.get(symbol, {}).get(source)
    
    def clear_cache(self, symbol: Optional[str] = None, source: Optional[str] = None):
        """Clear cached data"""
        if symbol and source:
            if symbol in self._last_data and source in self._last_data[symbol]:
                del self._last_data[symbol][source]
            if symbol in self._last_fetch_time and source in self._last_fetch_time[symbol]:
                del self._last_fetch_time[symbol][source]
        elif symbol:
            if symbol in self._last_data:
                del self._last_data[symbol]
            if symbol in self._last_fetch_time:
                del self._last_fetch_time[symbol]
        else:
            self._last_data.clear()
            self._last_fetch_time.clear()


class DataDeduplicator:
    """
    Data deduplication service
    Prevents processing duplicate signals and data
    """
    
    def __init__(self, dedup_window_seconds: int = 60):
        """
        Initialize deduplicator
        
        Args:
            dedup_window_seconds: Time window for deduplication (default: 60 seconds)
        """
        self.dedup_window = timedelta(seconds=dedup_window_seconds)
        
        # Track recent signals: {symbol: {signal_hash: timestamp}}
        self._recent_signals: Dict[str, Dict[str, datetime]] = defaultdict(dict)
        
        # Track recent data: {symbol: {source: {data_hash: timestamp}}}
        self._recent_data: Dict[str, Dict[str, Dict[str, datetime]]] = defaultdict(lambda: defaultdict(dict))
    
    def is_duplicate_signal(self, signal: Dict) -> bool:
        """
        Check if signal is a duplicate
        
        Args:
            signal: Signal dictionary
        
        Returns:
            True if duplicate, False if new
        """
        symbol = signal.get('symbol')
        if not symbol:
            return False
        
        # Create signal hash (exclude timestamp)
        signal_hash = self._hash_signal(signal)
        
        # Check if we've seen this signal recently
        if symbol in self._recent_signals:
            if signal_hash in self._recent_signals[symbol]:
                last_seen = self._recent_signals[symbol][signal_hash]
                if datetime.utcnow() - last_seen < self.dedup_window:
                    return True
        
        # Record this signal
        if symbol not in self._recent_signals:
            self._recent_signals[symbol] = {}
        
        self._recent_signals[symbol][signal_hash] = datetime.utcnow()
        
        # Clean old entries
        self._cleanup_old_signals(symbol)
        
        return False
    
    def is_duplicate_data(self, symbol: str, source: str, data: Dict) -> bool:
        """
        Check if data is a duplicate
        
        Args:
            symbol: Symbol
            source: Data source
            data: Data dictionary
        
        Returns:
            True if duplicate, False if new
        """
        # Create data hash
        data_hash = self._hash_data(data)
        
        # Check if we've seen this data recently
        if symbol in self._recent_data and source in self._recent_data[symbol]:
            if data_hash in self._recent_data[symbol][source]:
                last_seen = self._recent_data[symbol][source][data_hash]
                if datetime.utcnow() - last_seen < self.dedup_window:
                    return True
        
        # Record this data
        if symbol not in self._recent_data:
            self._recent_data[symbol] = {}
        if source not in self._recent_data[symbol]:
            self._recent_data[symbol][source] = {}
        
        self._recent_data[symbol][source][data_hash] = datetime.utcnow()
        
        # Clean old entries
        self._cleanup_old_data(symbol, source)
        
        return False
    
    def _hash_signal(self, signal: Dict) -> str:
        """Create hash for signal (excluding timestamp)"""
        import hashlib
        import json
        
        # Create copy without timestamp
        signal_copy = {k: v for k, v in signal.items() if k != 'timestamp'}
        signal_str = json.dumps(signal_copy, sort_keys=True)
        return hashlib.md5(signal_str.encode()).hexdigest()
    
    def _hash_data(self, data: Dict) -> str:
        """Create hash for data"""
        import hashlib
        import json
        
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _cleanup_old_signals(self, symbol: str):
        """Remove old signal entries"""
        if symbol not in self._recent_signals:
            return
        
        now = datetime.utcnow()
        to_remove = [
            signal_hash for signal_hash, timestamp in self._recent_signals[symbol].items()
            if now - timestamp > self.dedup_window
        ]
        
        for signal_hash in to_remove:
            del self._recent_signals[symbol][signal_hash]
    
    def _cleanup_old_data(self, symbol: str, source: str):
        """Remove old data entries"""
        if symbol not in self._recent_data or source not in self._recent_data[symbol]:
            return
        
        now = datetime.utcnow()
        to_remove = [
            data_hash for data_hash, timestamp in self._recent_data[symbol][source].items()
            if now - timestamp > self.dedup_window
        ]
        
        for data_hash in to_remove:
            del self._recent_data[symbol][source][data_hash]


class AdaptivePollingManager:
    """
    Adaptive polling interval manager
    Adjusts polling frequency based on market conditions and volatility
    """
    
    def __init__(self):
        # Base polling intervals (seconds)
        self.base_interval = 5.0  # Default 5 seconds
        self.min_interval = 1.0   # Minimum 1 second
        self.max_interval = 60.0  # Maximum 60 seconds
        
        # Track volatility per symbol
        self._symbol_volatility: Dict[str, float] = {}
        
        # Track last price changes
        self._price_changes: Dict[str, list] = defaultdict(list)
        
        # Market hours tracking
        self._is_market_hours: Dict[str, bool] = {}
    
    def get_polling_interval(self, symbol: str, is_market_hours: bool = True) -> float:
        """
        Get adaptive polling interval for symbol
        
        Args:
            symbol: Symbol to get interval for
            is_market_hours: Whether market is open
        
        Returns:
            Polling interval in seconds
        """
        # Off-market hours: use longer interval
        if not is_market_hours:
            return min(self.base_interval * 3, self.max_interval)
        
        # High volatility: use shorter interval
        volatility = self._symbol_volatility.get(symbol, 0.0)
        if volatility > 0.05:  # 5% volatility
            return max(self.base_interval * 0.5, self.min_interval)
        elif volatility > 0.02:  # 2% volatility
            return self.base_interval * 0.75
        elif volatility < 0.005:  # 0.5% volatility (low)
            return min(self.base_interval * 2, self.max_interval)
        
        # Default: base interval
        return self.base_interval
    
    def update_volatility(self, symbol: str, price_change_pct: float):
        """
        Update volatility estimate for symbol
        
        Args:
            symbol: Symbol
            price_change_pct: Recent price change percentage
        """
        # Track recent price changes (last 10)
        self._price_changes[symbol].append(abs(price_change_pct))
        if len(self._price_changes[symbol]) > 10:
            self._price_changes[symbol].pop(0)
        
        # Calculate volatility as average absolute price change
        if self._price_changes[symbol]:
            self._symbol_volatility[symbol] = sum(self._price_changes[symbol]) / len(self._price_changes[symbol])
    
    def set_market_hours(self, symbol: str, is_market_hours: bool):
        """Set market hours status for symbol"""
        self._is_market_hours[symbol] = is_market_hours
    
    def get_volatility(self, symbol: str) -> float:
        """Get current volatility estimate for symbol"""
        return self._symbol_volatility.get(symbol, 0.0)

