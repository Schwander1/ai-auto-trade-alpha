#!/usr/bin/env python3
"""Massive.com (formerly Polygon.io) Data Source - Primary Market Data (40% weight)"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import logging
import asyncio
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Massive")
logger.setLevel(logging.DEBUG)  # Enable debug for troubleshooting

class MassiveDataSource:
    """
    Massive.com (formerly Polygon.io) integration for market data
    Weight: 40% in Alpine Analytics consensus (primary source)
    
    Note: Polygon.io rebranded to Massive.com on Oct 30, 2025
    API endpoints: api.massive.com (new) or api.polygon.io (legacy, still works)
    
    Plan: Currencies Starter ($49/month)
    - Unlimited API calls
    - Real-time data available
    - 10+ years historical data
    - WebSockets, second aggregates, crypto trades & quotes
    
    Caching: Optimized for performance (10s cache for faster signal updates)
    Connection Pooling: HTTP session with connection reuse for better performance
    """
    
    def __init__(self, api_key):
        self.api_key = api_key
        # Use new Massive.com endpoint with fallback to legacy Polygon.io
        self.base_url = "https://api.massive.com"  # New endpoint
        self.legacy_url = "https://api.polygon.io"  # Legacy endpoint (still works)
        
        # HTTP Session with connection pooling for better performance
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        # OPTIMIZATION 14: Increased connection pool sizes for better concurrency
        adapter = HTTPAdapter(
            pool_connections=20,  # Increased from 10
            pool_maxsize=50,      # Increased from 20
            max_retries=retry_strategy,
            pool_block=False      # Don't block, raise exception instead
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Price data cache for performance optimization (not rate limiting)
        # Format: {symbol: (dataframe, timestamp)}
        self._price_cache: Dict[str, tuple] = {}
        self._cache_duration = 10  # Cache for 10 seconds (performance optimization, not rate limiting)
        
        # Adaptive cache and rate limiting
        try:
            from argo.core.adaptive_cache import AdaptiveCache
            from argo.core.rate_limiter import get_rate_limiter
            from argo.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
            from argo.core.redis_cache import get_redis_cache
            self.adaptive_cache = AdaptiveCache()
            self.rate_limiter = get_rate_limiter()
            self.circuit_breaker = CircuitBreaker('massive', CircuitBreakerConfig(
                failure_threshold=5,
                success_threshold=2,
                timeout=60.0
            ))
            self.redis_cache = get_redis_cache()
        except ImportError:
            self.adaptive_cache = None
            self.rate_limiter = None
            self.circuit_breaker = None
            self.redis_cache = None
        
    def _get_cached_price_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get cached price data if still valid (performance optimization)"""
        # Try Redis cache first
        if self.redis_cache:
            try:
                cache_key = f"massive:price:{symbol}"
                cached = self.redis_cache.get(cache_key)
                if cached:
                    logger.debug(f"✅ Using Redis cached Massive.com data for {symbol}")
                    return cached
            except Exception as e:
                logger.debug(f"Redis cache get error: {e}")
        
        # Fallback to in-memory cache
        if symbol not in self._price_cache:
            return None
        
        df, cache_time = self._price_cache[symbol]
        
        # Handle both datetime and float timestamp formats
        if isinstance(cache_time, (int, float)):
            # cache_time is a timestamp, convert to datetime for comparison
            age_seconds = (datetime.now(timezone.utc).timestamp() - cache_time)
        else:
            # cache_time is a datetime object
            age_seconds = (datetime.now(timezone.utc) - cache_time).total_seconds()
        
        # Use adaptive cache TTL if available
        cache_duration = self._cache_duration
        if self.adaptive_cache:
            is_market_hours = self.adaptive_cache.is_market_hours()
            cache_duration = self.adaptive_cache.get_cache_ttl(symbol, is_market_hours, self._cache_duration)
        
        if age_seconds < cache_duration:
            logger.debug(f"✅ Using cached Massive.com data for {symbol} (age: {age_seconds:.1f}s, TTL: {cache_duration}s)")
            return df
        
        # Cache expired
        del self._price_cache[symbol]
        return None
    
    async def fetch_price_data(self, symbol, days=90):
        """
        Fetch historical price data from Massive.com API (async to avoid blocking event loop)
        
        Optimized for Starter plan with unlimited API calls:
        - No rate limiting (unlimited calls)
        - Adaptive cache TTL based on market hours and volatility
        - Redis distributed cache support
        - Circuit breaker protection
        - Supports unlimited crypto symbols
        """
        try:
            # Check cache first
            cached_df = self._get_cached_price_data(symbol)
            if cached_df is not None:
                return cached_df
            
            # Rate limiting
            if self.rate_limiter:
                await self.rate_limiter.wait_for_permission('massive')
            
            # Circuit breaker protection
            if self.circuit_breaker:
                async def _fetch():
                    ticker = self._convert_symbol_format(symbol)
                    start_date, end_date = self._get_date_range(days)
                    return await self._fetch_from_api(ticker, start_date, end_date, symbol)
                
                response = await self.circuit_breaker.call_async(_fetch)
            else:
                ticker = self._convert_symbol_format(symbol)
                start_date, end_date = self._get_date_range(days)
                response = await self._fetch_from_api(ticker, start_date, end_date, symbol)
            
            if not response:
                return None
            
            # Parse and cache response
            df = self._parse_api_response(response, symbol)
            if df is not None:
                self._cache_price_data(symbol, df)
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Massive error for {symbol}: {e}", exc_info=True)
            return None
    
    def _convert_symbol_format(self, symbol: str) -> str:
        """Convert symbol format for Massive.com API"""
        is_crypto = '-USD' in symbol
        
        if is_crypto:
            crypto_symbol = symbol.replace('-USD', '')
            return f"X:{crypto_symbol}USD"
        else:
            return symbol
    
    def _get_date_range(self, days: int) -> Tuple[str, str]:
        """Get start and end dates for API request"""
        end = datetime.now().strftime('%Y-%m-%d')
        start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        return start, end
    
    async def _fetch_from_api(self, ticker: str, start_date: str, end_date: str, symbol: str):
        """Fetch data from API with endpoint fallback"""
        import time
        from argo.core.data_source_health import get_health_monitor
        
        health_monitor = get_health_monitor()
        start_time = time.time()
        
        url = f"{self.base_url}/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
        params = {'adjusted': 'true', 'sort': 'asc', 'limit': 50000, 'apiKey': self.api_key}
        
        try:
            response = await asyncio.to_thread(self.session.get, url, params=params, timeout=10)
            duration = time.time() - start_time
            
            # Try legacy endpoint if new one fails
            if response.status_code != 200:
                logger.debug(f"New endpoint failed, trying legacy Polygon.io endpoint...")
                url = f"{self.legacy_url}/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
                response = await asyncio.to_thread(self.session.get, url, params=params, timeout=10)
                duration = time.time() - start_time
            
            if response.status_code == 200:
                health_monitor.record_success('massive', duration)
                return response
            else:
                error_msg = response.text[:200] if response.text else "No error message"
                error_type = f"http_{response.status_code}"
                health_monitor.record_error('massive', error_type, duration)
                
                # FIX: Improved error handling for API key errors
                if response.status_code == 401:
                    try:
                        error_json = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                        error_detail = error_json.get('error', error_msg) if error_json else error_msg
                        if 'api key' in error_detail.lower() or 'unknown api key' in error_detail.lower():
                            logger.error(f"❌ Massive API error 401: Invalid API key detected")
                            logger.error(f"   Error: {error_detail[:200]}")
                            logger.error("   ACTION REQUIRED: Update Massive API key in config.json or environment variable")
                            logger.error("   Get new key from: https://massive.com")
                            # Disable this source to prevent repeated failed calls
                            self.enabled = False
                    except Exception:
                        logger.error(f"❌ Massive API error 401 (Unauthorized): {error_msg}")
                        logger.error("   ACTION REQUIRED: Verify API key is correct and active")
                        self.enabled = False
                else:
                    logger.warning(f"⚠️  Massive API error {response.status_code} for {symbol}: {error_msg}")
                return None
        except Exception as e:
            duration = time.time() - start_time
            error_type = type(e).__name__
            health_monitor.record_error('massive', error_type, duration)
            logger.error(f"❌ Massive API exception for {symbol}: {e}")
            return None
    
    def _parse_api_response(self, response, symbol: str) -> Optional[pd.DataFrame]:
        """Parse API response into DataFrame"""
        data = response.json()
        if data.get('status') not in ['OK', 'DELAYED'] or not data.get('results'):
            logger.warning(f"⚠️  Massive API returned status '{data.get('status')}' for {symbol} - no results")
            return None
        
        df = pd.DataFrame(data['results'])
        df['Date'] = pd.to_datetime(df['t'], unit='ms')
        df = df.rename(columns={'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'})
        df = df.set_index('Date')[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        logger.info(f"✅ Massive: {symbol} - {len(df)} bars")
        return df
    
    def _cache_price_data(self, symbol: str, df: pd.DataFrame):
        """Cache price data for performance optimization"""
        # Calculate adaptive TTL
        cache_duration = self._cache_duration
        if self.adaptive_cache:
            is_market_hours = self.adaptive_cache.is_market_hours()
            cache_duration = self.adaptive_cache.get_cache_ttl(symbol, is_market_hours, self._cache_duration)
        
        # Cache in Redis (store only DataFrame, not tuple with timestamp)
        if self.redis_cache:
            try:
                cache_key = f"massive:price:{symbol}"
                # Store only the DataFrame, Redis will handle TTL
                self.redis_cache.set(cache_key, df, ttl=cache_duration)
            except Exception as e:
                logger.debug(f"Redis cache set error: {e}")
        
        # Also cache in-memory (store tuple with datetime for age calculation)
        self._price_cache[symbol] = (df, datetime.now(timezone.utc))
        logger.debug(f"💾 Cached Massive.com data for {symbol} (TTL: {cache_duration}s)")
    
    def generate_signal(self, df, symbol):
        """Generate signal from price data"""
        if df is None or len(df) < 50:
            return None
        
        try:
            # Calculate indicators
            indicators = self._calculate_indicators(df)
            
            # Determine signal direction and confidence
            direction, confidence = self._determine_signal(indicators, df)
            
            # Allow signals even with lower confidence - consensus will filter them
            # Only filter out completely invalid signals (confidence < 50)
            if confidence < 50:
                return None
            
            return self._build_signal_dict(direction, confidence, indicators)
            
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
            return None
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict:
        """
        Calculate technical indicators using vectorized operations
        OPTIMIZATION 8: Vectorized pandas operations (10-100x faster than loops)
        """
        # OPTIMIZATION 8: Vectorized operations (10-100x faster than loops)
        df['SMA_20'] = df['Close'].rolling(20, min_periods=1).mean()
        df['SMA_50'] = df['Close'].rolling(50, min_periods=1).mean()
        df['Volume_SMA'] = df['Volume'].rolling(20, min_periods=1).mean()
        
        # OPTIMIZATION 8: Vectorized volume ratio calculation
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # OPTIMIZATION 8: Vectorized price change calculation
        df['Price_Change'] = df['Close'].pct_change()
        
        # Get latest values (single operation)
        latest = df.iloc[-1]
        
        return {
            'current_price': float(latest['Close']),
            'sma_20': float(latest['SMA_20']),
            'sma_50': float(latest['SMA_50']),
            'volume_ratio': float(latest['Volume_Ratio']),
            'price_change': float(latest['Price_Change']) if not pd.isna(latest['Price_Change']) else 0.0
        }
    
    def _determine_signal(self, indicators: Dict, df: pd.DataFrame) -> Tuple[str, float]:
        """Determine signal direction and confidence"""
        current_price = indicators['current_price']
        sma_20 = indicators['sma_20']
        sma_50 = indicators['sma_50']
        volume_ratio = indicators['volume_ratio']
        
        confidence = 60.0
        direction = 'NEUTRAL'
        
        # Trend-based
        if current_price > sma_20 > sma_50:
            direction = 'LONG'
            confidence += 15.0
        elif current_price < sma_20 < sma_50:
            direction = 'SHORT'
            confidence += 15.0
        
        # Volume confirmation
        if volume_ratio > 1.2:
            confidence += 10.0
        
        # Price momentum
        price_change_pct = ((current_price - df.iloc[-5]['Close']) / df.iloc[-5]['Close']) * 100
        if abs(price_change_pct) > 2:
            confidence += 10.0
        
        confidence = min(confidence, 95.0)
        return direction, confidence
    
    def _build_signal_dict(self, direction: str, confidence: float, indicators: Dict) -> Dict:
        """Build signal dictionary"""
        return {
            'direction': direction,
            'confidence': round(confidence, 2),
            'source': 'massive',
            'weight': 0.40,
            'entry_price': round(indicators['current_price'], 2),
            'indicators': {
                'sma_20': round(indicators['sma_20'], 2),
                'sma_50': round(indicators['sma_50'], 2),
                'volume_ratio': round(indicators['volume_ratio'], 2)
            }
        }
