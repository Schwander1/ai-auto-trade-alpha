#!/usr/bin/env python3
"""
Chinese Models Data Source with Rate Limiting & Cost Tracking
Implements Qwen → GLM → Baichuan (DeepSeek) fallback with comprehensive cost management
"""
import asyncio
import logging
import os
import json
import re
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class APICostConfig:
    """API cost configuration per model"""
    requests_per_minute: int
    cost_per_request: float
    daily_budget: float = 100.0  # Daily budget limit

class APIRateLimiter:
    """
    Rate limiter with cost tracking for Chinese model APIs.
    Prevents API abuse and provides cost visibility.
    """
    def __init__(self, config: APICostConfig):
        self.config = config
        self.request_times = deque()
        self.total_cost = 0.0
        self.daily_cost = 0.0
        self.last_reset = datetime.now().date()
        self.request_count = 0
        self.rate_limit_violations = 0
        self._lock = asyncio.Lock()
        
    async def acquire(self) -> Tuple[bool, Optional[float]]:
        """
        Acquire permission to make API call with rate limiting.
        
        Returns:
            (allowed, wait_time_seconds) tuple
        """
        async with self._lock:
            now = datetime.now()
            
            # Reset daily cost tracking
            if now.date() > self.last_reset:
                self.daily_cost = 0.0
                self.last_reset = now.date()
                logger.info(f"📅 Daily cost reset. Previous day total: ${self.total_cost:.2f}")
                
            # Check daily budget (skip check if budget is 0.0, meaning unlimited/free)
            if self.config.daily_budget > 0.0 and self.daily_cost >= self.config.daily_budget:
                logger.warning(f"💰 Daily budget exceeded: ${self.daily_cost:.2f} >= ${self.config.daily_budget:.2f}")
                return False, None
                
            # Remove old requests outside the time window
            cutoff = now - timedelta(minutes=1)
            while self.request_times and self.request_times[0] < cutoff:
                self.request_times.popleft()
                
            # Check rate limit
            if len(self.request_times) >= self.config.requests_per_minute:
                self.rate_limit_violations += 1
                # Calculate wait time
                oldest_request = self.request_times[0]
                wait_time = 60 - (now - oldest_request).total_seconds()
                if wait_time > 0:
                    logger.warning(f"⏱️  Rate limit reached. Waiting {wait_time:.1f}s")
                    return False, wait_time
                    
            # Record request and cost
            self.request_times.append(now)
            self.total_cost += self.config.cost_per_request
            self.daily_cost += self.config.cost_per_request
            self.request_count += 1
            
            return True, None
            
    def get_cost_stats(self) -> Dict:
        """Get cost statistics for monitoring"""
        return {
            "total_cost": self.total_cost,
            "daily_cost": self.daily_cost,
            "requests_last_minute": len(self.request_times),
            "total_requests": self.request_count,
            "rate_limit": self.config.requests_per_minute,
            "rate_limit_violations": self.rate_limit_violations,
            "daily_budget_remaining": self.config.daily_budget - self.daily_cost
        }

class ChineseModelsDataSource:
    """
    Chinese models data source with multi-model fallback and cost management.
    Dynamic weight: 10% market hours → 20% off-hours
    """
    def __init__(self, config: Optional[Dict] = None):
        if config is None:
            config = {}
        
        # Load API keys from config or environment variables
        self.api_keys = {
            'qwen': config.get('qwen_api_key') or os.getenv('QWEN_API_KEY', ''),
            'qwen_access_key_id': config.get('qwen_access_key_id') or os.getenv('QWEN_ACCESS_KEY_ID', ''),
            'qwen_access_key_secret': config.get('qwen_access_key_secret') or os.getenv('QWEN_ACCESS_KEY_SECRET', ''),
            'glm': config.get('glm_api_key') or os.getenv('GLM_API_KEY', ''),
            'baichuan': config.get('baichuan_api_key') or os.getenv('BAICHUAN_API_KEY', ''),
            'deepseek': config.get('deepseek_api_key') or os.getenv('DEEPSEEK_API_KEY', '')
        }
        
        # Model configurations
        self.model_configs = {
            'qwen': {
                'model': config.get('qwen_model', 'qwen-turbo'),
                'enabled': config.get('qwen_enabled', False) and bool(
                    self.api_keys.get('qwen') or 
                    (self.api_keys.get('qwen_access_key_id') and self.api_keys.get('qwen_access_key_secret'))
                )
            },
            'glm': {
                'model': config.get('glm_model', 'glm-4.5-air'),
                'enabled': config.get('glm_enabled', True) and bool(self.api_keys.get('glm'))
            },
            'baichuan': {
                'model': config.get('baichuan_model', 'deepseek-chat'),
                'enabled': config.get('baichuan_enabled', True) and bool(
                    self.api_keys.get('baichuan') or self.api_keys.get('deepseek')
                )
            }
        }
            
        # Configure rate limiters for each model
        self.qwen_limiter = APIRateLimiter(APICostConfig(
            requests_per_minute=config.get('qwen_rpm', 20),
            cost_per_request=config.get('qwen_cost', 0.002),
            daily_budget=config.get('qwen_budget', 50.0)
        ))
        self.glm_limiter = APIRateLimiter(APICostConfig(
            requests_per_minute=config.get('glm_rpm', 30),
            cost_per_request=config.get('glm_cost', 0.001),
            daily_budget=config.get('glm_budget', 30.0)
        ))
        self.baichuan_limiter = APIRateLimiter(APICostConfig(
            requests_per_minute=config.get('baichuan_rpm', 25),
            cost_per_request=config.get('baichuan_cost', 0.0015),
            daily_budget=config.get('baichuan_budget', 20.0)
        ))
        
        # Model priority order (only enabled models)
        self.models = []
        if self.model_configs['qwen']['enabled']:
            self.models.append(("qwen", self.qwen_limiter, self._query_qwen))
        if self.model_configs['glm']['enabled']:
            self.models.append(("glm", self.glm_limiter, self._query_glm))
        if self.model_configs['baichuan']['enabled']:
            self.models.append(("baichuan", self.baichuan_limiter, self._query_baichuan))
        
        # Cache configuration
        self.cache_ttl_market_hours = config.get('cache_ttl_market', 120)  # 120s
        self.cache_ttl_off_hours = config.get('cache_ttl_off', 60)  # 60s
        self._cache = {}
        
        # Log initialization status
        enabled_models = [name for name, _, _ in self.models]
        if enabled_models:
            logger.info(f"✅ Chinese Models initialized: {', '.join(enabled_models)}")
        else:
            logger.warning("⚠️  No Chinese models enabled (missing API keys?)")
        
    def _is_market_hours(self) -> bool:
        """Check if current time is during market hours (9:30 AM - 4:00 PM ET)"""
        from datetime import time
        
        try:
            import pytz
            et = pytz.timezone('US/Eastern')
            now_et = datetime.now(et)
        except ImportError:
            # Fallback if pytz not available
            now_et = datetime.now()
        
        current_time = now_et.time()
        
        market_open = time(9, 30)
        market_close = time(16, 0)
        
        return market_open <= current_time <= market_close and now_et.weekday() < 5
        
    def _get_cache_key(self, symbol: str) -> str:
        """Generate cache key"""
        return f"chinese_models:{symbol}"
        
    def _get_cached_signal(self, symbol: str) -> Optional[Dict]:
        """Get cached signal if still valid"""
        cache_key = self._get_cache_key(symbol)
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            ttl = self.cache_ttl_market_hours if self._is_market_hours() else self.cache_ttl_off_hours
            if (datetime.now() - entry['timestamp']).total_seconds() < ttl:
                return entry['signal']
        return None
        
    def _cache_signal(self, symbol: str, signal: Dict):
        """Cache signal with timestamp"""
        cache_key = self._get_cache_key(symbol)
        self._cache[cache_key] = {
            'signal': signal,
            'timestamp': datetime.now()
        }
        
    async def get_signal(self, symbol: str, market_data: dict) -> Optional[Dict]:
        """
        Get signal from Chinese models with parallel fetching (OPTIMIZATION).
        Fetches from all enabled models in parallel, uses first successful response.
        
        Args:
            symbol: Stock symbol
            market_data: Current market data
            
        Returns:
            Signal dict or None if all models fail
        """
        # Check cache first
        cached = self._get_cached_signal(symbol)
        if cached:
            logger.debug(f"✅ Cache hit for {symbol}")
            return cached
        
        if not self.models:
            logger.warning("No Chinese models enabled")
            return None
        
        # OPTIMIZATION: Fetch from all models in parallel
        tasks = []
        task_metadata = {}
        
        for model_name, limiter, query_fn in self.models:
            # Check rate limit before creating task
            allowed, wait_time = await limiter.acquire()
            
            if not allowed:
                if wait_time and wait_time < 2.0:  # Only wait if short wait time
                    await asyncio.sleep(wait_time)
                    allowed, _ = await limiter.acquire()
                
                if not allowed:
                    logger.debug(f"⏱️  {model_name} rate limit/budget exceeded, skipping")
                    continue
            
            # Create task for parallel execution
            task = asyncio.create_task(query_fn(symbol, market_data))
            tasks.append(task)
            task_metadata[id(task)] = (model_name, limiter)
        
        if not tasks:
            logger.warning("No Chinese models available (all rate limited or budget exceeded)")
            return None
        
        # Wait for first successful response (with timeout)
        try:
            done, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED,
                timeout=5.0  # 5 second timeout
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Get first successful result
            signal_result = None
            for task in done:
                try:
                    signal = await task
                    if signal:
                        model_name, _ = task_metadata[id(task)]
                        logger.info(f"✅ Signal from {model_name} for {symbol}: {signal.get('direction')} @ {signal.get('confidence')}%")
                        self._cache_signal(symbol, signal)
                        return signal
                except Exception as e:
                    model_name, _ = task_metadata.get(id(task), ('unknown', None))
                    logger.debug(f"❌ {model_name} failed: {e}")
            
            # If no successful result, try waiting for all remaining tasks
            if not signal_result and pending:
                remaining_tasks = list(pending)
                results = await asyncio.gather(*remaining_tasks, return_exceptions=True)
                for task, result in zip(remaining_tasks, results):
                    if not isinstance(result, Exception) and result:
                        model_name, _ = task_metadata.get(id(task), ('unknown', None))
                        logger.info(f"✅ Signal from {model_name} for {symbol} (fallback)")
                        self._cache_signal(symbol, result)
                        return result
                        
        except asyncio.TimeoutError:
            logger.warning(f"⚠️  Chinese models timeout for {symbol}")
            # Cancel all tasks
            for task in tasks:
                task.cancel()
        
        logger.error(f"❌ All Chinese models failed for {symbol}")
        return None
        
    async def _query_qwen(self, symbol: str, market_data: dict) -> Optional[Dict]:
        """Query Qwen model via DashScope API"""
        try:
            import dashscope
            from dashscope import Generation
            
            # Try DashScope API key first
            api_key = self.api_keys.get('qwen')
            
            # If no API key, try using AccessKey credentials with Alibaba Cloud SDK
            if not api_key:
                access_key_id = self.api_keys.get('qwen_access_key_id')
                access_key_secret = self.api_keys.get('qwen_access_key_secret')
                if access_key_id and access_key_secret:
                    try:
                        # Try to use AccessKey with Alibaba Cloud credentials
                        # DashScope may support this through environment variables
                        import os
                        os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'] = access_key_id
                        os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'] = access_key_secret
                        # Try to get DashScope API key from STS or use AccessKey directly
                        logger.info("Attempting to use AccessKey credentials for DashScope...")
                        # Note: DashScope typically requires a DashScope API key
                        # Get it from: https://dashscope.console.aliyun.com/
                        logger.warning("⚠️  DashScope requires a DashScope API key (not AccessKey). Get it from: https://dashscope.console.aliyun.com/")
                        return None
                    except Exception as e:
                        logger.warning(f"Could not use AccessKey: {e}")
                        return None
                else:
                    logger.warning("Qwen API key not found")
                    return None
                
            dashscope.api_key = api_key
            
            # Prepare prompt for trading signal
            price = market_data.get('price', market_data.get('close', 0))
            volume = market_data.get('volume', 0)
            
            prompt = f"""作为专业的股票分析师，请分析 {symbol} 的当前价格 ${price:.2f}，成交量 {volume:,.0f}，并给出交易建议。

请提供：
1. 交易方向（LONG/SHORT/NEUTRAL）
2. 信心度（0-100）
3. 简要分析原因

请用JSON格式返回，格式：
{{"direction": "LONG/SHORT/NEUTRAL", "confidence": 75, "analysis": "分析内容"}}"""

            # Call Qwen API
            model_name = self.model_configs['qwen']['model']
            response = Generation.call(
                model=model_name,
                prompt=prompt,
                max_tokens=500,
                temperature=0.3
            )
            
            if response.status_code == 200:
                result_text = response.output.text
                
                # Parse JSON response
                json_match = re.search(r'\{[^}]+\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    
                    return {
                        'source': 'qwen',
                        'symbol': symbol,
                        'direction': result.get('direction', 'NEUTRAL').upper(),
                        'confidence': float(result.get('confidence', 75.0)),
                        'analysis': result.get('analysis', result_text),
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                logger.warning(f"Qwen API error: {response.message}")
                return None
                
        except ImportError:
            logger.warning("dashscope package not installed. Install with: pip install dashscope")
            return None
        except Exception as e:
            logger.error(f"Qwen API call failed: {e}")
            return None
        
    async def _query_glm(self, symbol: str, market_data: dict) -> Optional[Dict]:
        """Query GLM model via Zhipu AI API"""
        try:
            import zhipuai
            
            api_key = self.api_keys.get('glm')
            if not api_key:
                logger.warning("GLM API key not found")
                return None
                
            client = zhipuai.ZhipuAI(api_key=api_key)
            
            # Prepare prompt
            price = market_data.get('price', market_data.get('close', 0))
            volume = market_data.get('volume', 0)
            
            prompt = f"""作为专业的股票分析师，请分析 {symbol} 的当前价格 ${price:.2f}，成交量 {volume:,.0f}，并给出交易建议。

请提供：
1. 交易方向（LONG/SHORT/NEUTRAL）
2. 信心度（0-100）
3. 简要分析原因

请用JSON格式返回，格式：
{{"direction": "LONG/SHORT/NEUTRAL", "confidence": 75, "analysis": "分析内容"}}"""

            # Call GLM API
            model_name = self.model_configs['glm']['model']
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            if response.choices and len(response.choices) > 0:
                result_text = response.choices[0].message.content
                
                # Parse JSON response
                json_match = re.search(r'\{[^}]+\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    
                    return {
                        'source': 'glm',
                        'symbol': symbol,
                        'direction': result.get('direction', 'NEUTRAL').upper(),
                        'confidence': float(result.get('confidence', 73.0)),
                        'analysis': result.get('analysis', result_text),
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                logger.warning("GLM API returned no response")
                return None
                
        except ImportError:
            logger.warning("zhipuai package not installed. Install with: pip install zhipuai")
            return None
        except Exception as e:
            logger.error(f"GLM API call failed: {e}")
            return None
        
    async def _query_baichuan(self, symbol: str, market_data: dict) -> Optional[Dict]:
        """Query DeepSeek model (Baichuan alternative) via OpenAI-compatible API"""
        try:
            import openai  # DeepSeek uses OpenAI-compatible API
            
            # Try Baichuan key first, then DeepSeek key
            api_key = self.api_keys.get('baichuan') or self.api_keys.get('deepseek')
            if not api_key:
                logger.warning("Baichuan/DeepSeek API key not found")
                return None
            
            # DeepSeek uses OpenAI-compatible API
            client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"  # DeepSeek endpoint
            )
            
            # Prepare prompt
            price = market_data.get('price', market_data.get('close', 0))
            volume = market_data.get('volume', 0)
            
            prompt = f"""作为专业的股票分析师，请分析 {symbol} 的当前价格 ${price:.2f}，成交量 {volume:,.0f}，并给出交易建议。

请提供：
1. 交易方向（LONG/SHORT/NEUTRAL）
2. 信心度（0-100）
3. 简要分析原因

请用JSON格式返回，格式：
{{"direction": "LONG/SHORT/NEUTRAL", "confidence": 75, "analysis": "分析内容"}}"""

            # Call API
            model_name = self.model_configs['baichuan']['model']
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            if response.choices and len(response.choices) > 0:
                result_text = response.choices[0].message.content
                
                # Parse JSON response
                json_match = re.search(r'\{[^}]+\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    
                    return {
                        'source': 'baichuan',  # Keep name for consistency
                        'symbol': symbol,
                        'direction': result.get('direction', 'NEUTRAL').upper(),
                        'confidence': float(result.get('confidence', 72.0)),
                        'analysis': result.get('analysis', result_text),
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                logger.warning("DeepSeek API returned no response")
                return None
                
        except ImportError:
            logger.warning("openai package not installed. Install with: pip install openai")
            return None
        except Exception as e:
            logger.error(f"DeepSeek API call failed: {e}")
            return None
        
    def get_cost_report(self) -> Dict:
        """Get comprehensive cost report"""
        return {
            "qwen": self.qwen_limiter.get_cost_stats(),
            "glm": self.glm_limiter.get_cost_stats(),
            "baichuan": self.baichuan_limiter.get_cost_stats(),
            "total_daily_cost": sum(
                limiter.daily_cost 
                for _, limiter, _ in self.models
            ),
            "total_monthly_estimate": sum(
                limiter.daily_cost * 30
                for _, limiter, _ in self.models
            )
        }
        
    def get_weight(self) -> float:
        """Get current weight based on market hours"""
        # 10% during market hours, 20% off-hours
        return 0.20 if not self._is_market_hours() else 0.10
