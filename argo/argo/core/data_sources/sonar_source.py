#!/usr/bin/env python3
"""Sonar AI (Perplexity) Data Source - AI Analysis (15% weight) - Optimized"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SonarAI")

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

class SonarDataSource:
    """
    Perplexity Sonar AI integration for deep analysis
    Weight: 15% in Alpine Analytics consensus
    Optimized with caching and market hours detection (similar to xAI Grok)
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
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
        
        # Analysis cache: {symbol: (analysis_data, timestamp)}
        self._analysis_cache: Dict[str, tuple] = {}
        self._cache_duration = 120  # 120 seconds (2 minutes) cache for Sonar
        
        if not self.enabled:
            logger.warning("⚠️  Sonar AI API key not configured - using fallback analysis")
        else:
            logger.info(f"✅ Sonar AI initialized (market hours stocks, 24/7 crypto, 120s cache)")
            logger.debug(f"   API key: {api_key[:10]}...")
    
    def _is_market_hours(self) -> bool:
        """Check if current time is within market hours (9:30 AM - 4:00 PM ET) on weekdays"""
        try:
            if PYTZ_AVAILABLE:
                now_et = datetime.now(ET)
            else:
                # Fallback: assume ET is UTC-5 (EST) or UTC-4 (EDT)
                # This is approximate - pytz is recommended
                from datetime import timedelta
                now_utc = datetime.now(timezone.utc)
                # Approximate ET offset (UTC-5, or UTC-4 during DST)
                # Simple approximation: assume UTC-5
                et_offset = timedelta(hours=-5)
                now_et = (now_utc + et_offset).replace(tzinfo=None)
            
            # Check if weekday (Monday=0, Friday=4)
            is_weekday = now_et.weekday() < 5
            if not is_weekday:
                return False
            
            current_time = now_et.time()
            market_open = current_time.replace(hour=MARKET_OPEN_HOUR, minute=MARKET_OPEN_MINUTE, second=0, microsecond=0)
            market_close = current_time.replace(hour=MARKET_CLOSE_HOUR, minute=MARKET_CLOSE_MINUTE, second=0, microsecond=0)
            
            # Check if within market hours (9:30 AM - 4:00 PM ET)
            return market_open <= current_time <= market_close
        except Exception as e:
            logger.debug(f"Market hours check error: {e}")
            return True  # Default to allowing if check fails
    
    def _is_crypto_symbol(self, symbol: str) -> bool:
        """Check if symbol is a cryptocurrency"""
        return '-USD' in symbol or symbol.startswith('BTC') or symbol.startswith('ETH') or symbol.startswith('SOL')
    
    def _get_cached_analysis(self, symbol: str) -> Optional[any]:
        """Get cached analysis if still valid"""
        if symbol not in self._analysis_cache:
            return None
        
        analysis_data, cache_time = self._analysis_cache[symbol]
        age_seconds = (datetime.now(timezone.utc) - cache_time).total_seconds()
        
        if age_seconds < self._cache_duration:
            logger.debug(f"✅ Using cached Sonar analysis for {symbol} (age: {age_seconds:.1f}s)")
            return analysis_data
        
        # Cache expired
        del self._analysis_cache[symbol]
        return None
        
    async def fetch_analysis(self, symbol):
        """
        Get AI-powered analysis for a symbol
        Optimized:
        - Market hours only for stocks
        - 24/7 for crypto
        - 120 second cache
        """
        if not self.enabled:
            return None
        
        # Check market hours and cache
        analysis = self._check_market_hours_and_cache(symbol)
        if analysis is not None:
            return analysis
        
        # Fetch from API
        return await self._fetch_analysis_from_api(symbol)
    
    def _check_market_hours_and_cache(self, symbol: str) -> Optional:
        """Check market hours and return cached analysis if available"""
        is_crypto = self._is_crypto_symbol(symbol)
        if not is_crypto and not self._is_market_hours():
            logger.debug(f"⏭️  Market closed for {symbol} (stocks only during market hours)")
            return self._get_cached_analysis(symbol)
        
        # Check cache
        cached_analysis = self._get_cached_analysis(symbol)
        if cached_analysis:
            return cached_analysis
        
        return None
    
    async def _fetch_analysis_from_api(self, symbol: str):
        """Fetch analysis from Sonar AI API"""
        try:
            prompt = self._build_analysis_prompt(symbol)
            headers = self._build_headers()
            payload = self._build_payload(prompt)
            
            response = await self._make_api_request(headers, payload)
            
            if response.status_code == 200:
                return self._parse_successful_response(response, symbol)
            else:
                return self._handle_api_error(response)
                
        except Exception as e:
            logger.error(f"Sonar AI error for {symbol}: {e}")
            return None
    
    def _build_analysis_prompt(self, symbol: str) -> str:
        """Build analysis prompt"""
        return f"""Analyze {symbol} for trading:
            
            Consider:
            - Technical indicators (RSI, MACD, moving averages)
            - Recent price action and volume
            - Market sentiment
            - News and fundamentals
            
            Provide:
            1. Signal direction (LONG/SHORT/NEUTRAL)
            2. Confidence (0-100)
            3. Brief reasoning (1-2 sentences)
            
            Format: SIGNAL: [direction] | CONFIDENCE: [0-100] | REASONING: [text]"""
    
    def _build_headers(self) -> Dict:
        """Build API request headers"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def _build_payload(self, prompt: str) -> Dict:
        """Build API request payload"""
        return {
            'model': 'sonar',
            'messages': [
                {'role': 'system', 'content': 'You are a professional trading analyst providing concise signal analysis.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.2,
            'max_tokens': 200
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
        
        # Cache the analysis
        self._analysis_cache[symbol] = (analysis, datetime.now(timezone.utc))
        logger.info(f"✅ Sonar AI: {symbol} analysis received (cached for {self._cache_duration}s)")
        return analysis
    
    def _handle_api_error(self, response) -> Optional:
        """Handle API error responses"""
        status_code = response.status_code
        
        if status_code == 401:
            # Authentication error - API key invalid or expired
            # Only log once per session to reduce spam
            if not hasattr(self, '_auth_error_logged'):
                logger.warning(f"⚠️  Sonar API authentication failed (401) - API key may be invalid or expired")
                logger.warning("   Sonar AI will be disabled for this session. Check API key in config.json")
                self._auth_error_logged = True
                self.enabled = False  # Disable to prevent repeated errors
            return None
        elif status_code == 400:
            error_detail = response.text if hasattr(response, 'text') else str(response)
            logger.error(f"Sonar API error 400 (Bad Request): {error_detail[:200]}")
            logger.error("   Check: Request parameters, API key format, or model name")
        elif status_code == 429:
            # Rate limit - reduce log level
            logger.debug(f"Sonar API rate limit (429) - will retry later")
        else:
            error_detail = response.text if hasattr(response, 'text') else str(response)
            logger.error(f"Sonar API error {status_code}: {error_detail[:200]}")
        return None
    
    def generate_signal(self, analysis, symbol):
        """Parse AI analysis into structured signal"""
        if not analysis:
            return None
        
        try:
            # Parse the analysis
            analysis_lower = analysis.lower()
            
            # Extract direction
            if 'signal: long' in analysis_lower or 'bullish' in analysis_lower:
                direction = 'LONG'
            elif 'signal: short' in analysis_lower or 'bearish' in analysis_lower:
                direction = 'SHORT'
            else:
                direction = 'NEUTRAL'
            
            # Extract confidence (look for numbers)
            confidence = 75.0  # Default
            import re
            conf_match = re.search(r'confidence[:\s]+(\d+)', analysis_lower)
            if conf_match:
                confidence = float(conf_match.group(1))
            
            # Extract reasoning
            reasoning_match = re.search(r'reasoning[:\s]+(.+?)(?:\n|$)', analysis, re.IGNORECASE)
            reasoning = reasoning_match.group(1).strip() if reasoning_match else "AI analysis completed"
            
            return {
                'direction': direction,
                'confidence': round(confidence, 2),
                'source': 'sonar_ai',
                'weight': 0.15,
                'reasoning': reasoning[:200]  # Limit to 200 chars
            }
            
        except Exception as e:
            logger.error(f"Signal parsing error: {e}")
            return None
