#!/usr/bin/env python3
"""xAI Grok Data Source - AI Sentiment Analysis (20% weight) - Option 2B Optimized"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("xAIGrok")

# Market hours: 9:30 AM - 4:00 PM ET
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 30
MARKET_CLOSE_HOUR = 16
MARKET_CLOSE_MINUTE = 0

# Try to import pytz, fallback to manual timezone calculation
try:
    from pytz import timezone as pytz_timezone
    ET = pytz_timezone('US/Eastern')
    PYTZ_AVAILABLE = True
except ImportError:
    PYTZ_AVAILABLE = False
    logger.warning("⚠️  pytz not available - using UTC for market hours check")

class XAIGrokDataSource:
    """
    xAI Grok integration for sentiment analysis
    Weight: 20% in Alpine Analytics consensus
    Option 2B Optimized:
    - Model: grok-4-fast-reasoning (cost-effective, high quality)
    - Market hours only for stocks (9:30 AM - 4:00 PM ET)
    - 24/7 for crypto symbols
    - 1-2 minute cache (50% API calls)
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        # xAI Grok API endpoint (verified)
        self.base_url = "https://api.x.ai/v1/chat/completions"
        self.enabled = bool(api_key)
        
        # HTTP Session with connection pooling for better performance
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        # OPTIMIZATION 14: Increased connection pool sizes
        adapter = HTTPAdapter(
            pool_connections=20,  # Increased from 10
            pool_maxsize=50,      # Increased from 20
            max_retries=retry_strategy,
            pool_block=False
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Sentiment cache: {symbol: (sentiment_data, timestamp)}
        self._sentiment_cache: Dict[str, tuple] = {}
        self._cache_duration = 90  # 90 seconds (1.5 minutes) cache
        
        if not self.enabled:
            logger.warning("⚠️  xAI Grok API key not configured - using fallback sentiment")
        else:
            logger.info(f"✅ xAI Grok initialized (Option 2B: grok-4-fast-reasoning, market hours stocks, 24/7 crypto, 90s cache)")
            logger.debug(f"   API key: {api_key[:10]}...")
    
    def _is_market_hours(self) -> bool:
        """Check if current time is within market hours (9:30 AM - 4:00 PM ET)"""
        try:
            if PYTZ_AVAILABLE:
                now_et = datetime.now(ET)
            else:
                # Fallback: Use UTC and approximate ET (UTC-5 or UTC-4)
                from datetime import timedelta
                now_utc = datetime.now(timezone.utc)
                # Approximate ET offset (UTC-5, or UTC-4 during DST)
                # Simple approximation: assume UTC-5
                et_offset = timedelta(hours=-5)
                now_et = (now_utc + et_offset).replace(tzinfo=None)
            
            current_time = now_et.time()
            market_open = current_time.replace(hour=MARKET_OPEN_HOUR, minute=MARKET_OPEN_MINUTE, second=0, microsecond=0)
            market_close = current_time.replace(hour=MARKET_CLOSE_HOUR, minute=MARKET_CLOSE_MINUTE, second=0, microsecond=0)
            
            # Check if weekday (Monday=0, Friday=4)
            is_weekday = now_et.weekday() < 5
            
            return is_weekday and market_open <= current_time <= market_close
        except Exception as e:
            logger.debug(f"Error checking market hours: {e}")
            return True  # Default to open if check fails
    
    def _is_crypto_symbol(self, symbol: str) -> bool:
        """Check if symbol is crypto"""
        return '-USD' in symbol or symbol.startswith('BTC') or symbol.startswith('ETH') or symbol.startswith('SOL')
    
    def _get_cached_sentiment(self, symbol: str) -> Optional[any]:
        """Get cached sentiment if still valid"""
        if symbol not in self._sentiment_cache:
            return None
        
        sentiment_data, cache_time = self._sentiment_cache[symbol]
        age_seconds = (datetime.now(timezone.utc) - cache_time).total_seconds()
        
        if age_seconds < self._cache_duration:
            logger.debug(f"✅ Using cached sentiment for {symbol} (age: {age_seconds:.1f}s)")
            return sentiment_data
        
        # Cache expired
        del self._sentiment_cache[symbol]
        return None
    
    async def fetch_sentiment(self, symbol):
        """
        Get AI-powered sentiment analysis
        Option 2B Optimized:
        - Market hours only for stocks
        - 24/7 for crypto
        - 90 second cache
        """
        if not self.enabled:
            return self._get_fallback_sentiment('fallback')
        
        # Check market hours and cache
        sentiment = self._check_market_hours_and_cache(symbol)
        if sentiment:
            return sentiment
        
        # Fetch from API
        return await self._fetch_sentiment_from_api(symbol)
    
    def _get_fallback_sentiment(self, source: str) -> Dict:
        """Get fallback neutral sentiment"""
        return {
            'sentiment': 'neutral',
            'score': 0.5,
            'source': source
        }
    
    def _check_market_hours_and_cache(self, symbol: str) -> Optional:
        """Check market hours and return cached sentiment if available"""
        is_crypto = self._is_crypto_symbol(symbol)
        if not is_crypto and not self._is_market_hours():
            logger.debug(f"⏭️  Market closed for {symbol} (stocks only during market hours)")
            cached = self._get_cached_sentiment(symbol)
            if cached:
                return cached
            return self._get_fallback_sentiment('market_closed')
        
        # Check cache
        cached_sentiment = self._get_cached_sentiment(symbol)
        if cached_sentiment:
            return cached_sentiment
        
        return None
    
    async def _fetch_sentiment_from_api(self, symbol: str):
        """Fetch sentiment from xAI Grok API"""
        try:
            prompt = self._build_sentiment_prompt(symbol)
            headers = self._build_headers()
            payload = self._build_payload(prompt)
            
            response = await self._make_api_request(headers, payload)
            
            if response.status_code == 200:
                return self._parse_successful_response(response, symbol)
            else:
                return self._handle_api_error(response)
                
        except Exception as e:
            logger.error(f"xAI Grok error for {symbol}: {e}")
            return None
    
    def _build_sentiment_prompt(self, symbol: str) -> str:
        """Build sentiment analysis prompt"""
        return f"""Analyze market sentiment for {symbol}:
            
            Consider recent news, social media, and market trends.
            
            Provide:
            1. Sentiment (bullish/bearish/neutral)
            2. Confidence score (0-100)
            3. Key reasoning
            
            Format: SENTIMENT: [sentiment] | SCORE: [0-100] | REASON: [text]"""
    
    def _build_headers(self) -> Dict:
        """Build API request headers"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def _build_payload(self, prompt: str) -> Dict:
        """Build API request payload"""
        return {
            'model': 'grok-4-fast-reasoning',
            'messages': [
                {'role': 'system', 'content': 'You are a market sentiment analyst.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.2,
            'max_tokens': 150
        }
    
    async def _make_api_request(self, headers: Dict, payload: Dict):
        """Make API request with async handling"""
        try:
            return await asyncio.to_thread(
                self.session.post, self.base_url, headers=headers, json=payload, timeout=15
            )
        except AttributeError:
            # Fallback for Python < 3.9
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, lambda: self.session.post(self.base_url, headers=headers, json=payload, timeout=15)
            )
    
    def _parse_successful_response(self, response, symbol: str):
        """Parse successful API response"""
        data = response.json()
        analysis = data['choices'][0]['message']['content']
        
        # Cache the sentiment
        self._sentiment_cache[symbol] = (analysis, datetime.now(timezone.utc))
        logger.info(f"✅ xAI Grok: {symbol} sentiment received (cached for {self._cache_duration}s)")
        return analysis
    
    def _handle_api_error(self, response) -> Optional:
        """Handle API error responses"""
        if response.status_code == 403:
            error_detail = response.text
            logger.error(f"xAI API error 403 (Forbidden): {error_detail[:200]}")
            logger.error("   Check: API key permissions, team access, or if key is blocked")
        else:
            error_detail = response.text
            logger.error(f"xAI API error {response.status_code}: {error_detail[:200]}")
        return None
    
    def generate_signal(self, sentiment_data, symbol):
        """Parse sentiment into trading signal"""
        if not sentiment_data:
            return None
        
        try:
            # If using fallback or market closed, return low-confidence neutral
            if isinstance(sentiment_data, dict):
                source = sentiment_data.get('source')
                if source in ['fallback', 'market_closed']:
                    return {
                        'direction': 'NEUTRAL',
                        'confidence': 50.0,
                        'source': 'xai_grok_fallback',
                        'weight': 0.20,
                        'note': f'Using fallback sentiment - {source}'
                }
            
            # Parse actual sentiment analysis
            analysis_lower = str(sentiment_data).lower()
            
            if 'bullish' in analysis_lower or 'sentiment: bullish' in analysis_lower:
                direction = 'LONG'
                confidence = 75.0
            elif 'bearish' in analysis_lower or 'sentiment: bearish' in analysis_lower:
                direction = 'SHORT'
                confidence = 75.0
            else:
                direction = 'NEUTRAL'
                confidence = 60.0
            
            # Extract confidence score if present
            import re
            score_match = re.search(r'score[:\s]+(\d+)', analysis_lower)
            if score_match:
                confidence = float(score_match.group(1))
            
            return {
                'direction': direction,
                'confidence': round(confidence, 2),
                'source': 'xai_grok',
                'weight': 0.20
            }
            
        except Exception as e:
            logger.error(f"Signal parsing error: {e}")
            return None
