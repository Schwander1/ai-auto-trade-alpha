#!/usr/bin/env python3
"""
Cached Claude API wrapper to reduce costs
OPTIMIZATION: Enhanced with shared cache and cost-aware prompt optimization
Usage: from scripts.agentic.cached_claude import CachedClaude
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: anthropic package not installed. Install with: pip install anthropic")

# Try to import shared cache
try:
    from scripts.agentic.shared_cache import get_shared_cache
    SHARED_CACHE_AVAILABLE = True
except ImportError:
    SHARED_CACHE_AVAILABLE = False
    logger.debug("Shared cache not available")


class CachedClaude:
    """
    Cached wrapper for Anthropic Claude API to reduce costs
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        cache_ttl_hours: int = 24,
        use_shared_cache: bool = True
    ):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package required. Install with: pip install anthropic")
        
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or provided")
        
        self.client = Anthropic(api_key=self.api_key)
        
        # Setup cache directory (local fallback)
        if cache_dir is None:
            workspace_dir = Path(__file__).parent.parent.parent
            cache_dir = workspace_dir / "logs" / "agentic_cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        
        # OPTIMIZATION: Use shared Redis cache if available
        self.use_shared_cache = use_shared_cache and SHARED_CACHE_AVAILABLE
        if self.use_shared_cache:
            try:
                self.shared_cache = get_shared_cache()
                logger.info("✅ Using shared Redis cache for agentic features")
            except Exception as e:
                logger.warning(f"⚠️  Shared cache unavailable: {e}, using local cache")
                self.use_shared_cache = False
        else:
            self.shared_cache = None
    
    def _cache_key(self, prompt: str, model: str, max_tokens: int) -> str:
        """Generate cache key from prompt and parameters"""
        key_string = f"{prompt}:{model}:{max_tokens}"
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{cache_key}.json"
    
    def _load_cache(self, cache_path: Path) -> Optional[Dict[str, Any]]:
        """Load cached response if valid"""
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, "r") as f:
                cached = json.load(f)
            
            # Check if cache is still valid
            cached_time = datetime.fromisoformat(cached["timestamp"])
            if datetime.now(timezone.utc) - cached_time > self.cache_ttl:
                # Cache expired, delete it
                cache_path.unlink()
                return None
            
            return cached
        except (json.JSONDecodeError, KeyError, ValueError):
            # Invalid cache, delete it
            cache_path.unlink()
            return None
    
    def _save_cache(self, cache_path: Path, response: Dict[str, Any], prompt: str):
        """Save response to cache"""
        cache_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt": prompt,
            "response": response
        }
        
        with open(cache_path, "w") as f:
            json.dump(cache_entry, f, indent=2)
    
    def optimize_prompt_for_cost(self, prompt: str, max_tokens: int = 4000) -> tuple:
        """
        OPTIMIZATION: Optimize prompt to reduce token usage and cost
        Returns: (optimized_prompt, estimated_tokens, estimated_cost)
        """
        # Remove redundant whitespace
        optimized = ' '.join(prompt.split())
        
        # Estimate tokens (rough: 1 token ≈ 4 characters)
        estimated_tokens = len(optimized) // 4
        
        # Estimate cost (Claude 3.5 Sonnet: $3/1M input, $15/1M output)
        input_cost = (estimated_tokens / 1_000_000) * 3
        output_cost = (max_tokens / 1_000_000) * 15
        total_cost = input_cost + output_cost
        
        return optimized, estimated_tokens, total_cost
    
    def call(
        self,
        prompt: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4000,
        use_cache: bool = True,
        system: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call Claude API with optional caching and cost optimization
        
        Args:
            prompt: User prompt
            model: Claude model to use
            max_tokens: Maximum tokens in response
            use_cache: Whether to use cache
            system: Optional system message
        
        Returns:
            API response dictionary
        """
        # OPTIMIZATION: Optimize prompt for cost
        optimized_prompt, estimated_tokens, estimated_cost = self.optimize_prompt_for_cost(prompt, max_tokens)
        
        cache_key = self._cache_key(optimized_prompt, model, max_tokens)
        
        # Try to load from shared cache first
        if use_cache and self.use_shared_cache:
            cached = self.shared_cache.get(cache_key)
            if cached:
                logger.info(f"✅ Using shared cached response (saved ${estimated_cost:.6f})")
                return cached["response"]
        
        # Try local cache
        cache_path = self._get_cache_path(cache_key)
        if use_cache:
            cached = self._load_cache(cache_path)
            if cached:
                logger.info(f"✅ Using local cached response (saved ${estimated_cost:.6f})")
                # Also save to shared cache for future use
                if self.use_shared_cache:
                    self.shared_cache.set(cache_key, cached, ttl_hours=24)
                return cached["response"]
        
        # Make API call
        messages = [{"role": "user", "content": optimized_prompt}]
        
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages
        }
        
        if system:
            kwargs["system"] = system
        
        response = self.client.messages.create(**kwargs)
        
        # Convert response to dict for caching
        response_dict = {
            "id": response.id,
            "model": response.model,
            "role": response.role,
            "content": [{"type": block.type, "text": block.text} for block in response.content],
            "stop_reason": response.stop_reason,
            "stop_sequence": response.stop_sequence,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            },
            "estimated_cost": estimated_cost
        }
        
        # Save to cache (both shared and local)
        if use_cache:
            cache_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "prompt": optimized_prompt,
                "response": response_dict,
                "estimated_cost": estimated_cost
            }
            
            # Save to shared cache
            if self.use_shared_cache:
                self.shared_cache.set(cache_key, cache_entry, ttl_hours=24)
            
            # Save to local cache
            self._save_cache(cache_path, cache_entry, optimized_prompt)
        
        return response_dict
    
    def clear_cache(self, older_than_days: Optional[int] = None):
        """Clear cache files"""
        if older_than_days:
            cutoff = datetime.utcnow() - timedelta(days=older_than_days)
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, "r") as f:
                        cached = json.load(f)
                    cached_time = datetime.fromisoformat(cached["timestamp"])
                    if cached_time < cutoff:
                        cache_file.unlink()
                except:
                    cache_file.unlink()
        else:
            # Clear all
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
        
        print(f"✅ Cache cleared")


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python cached_claude.py <prompt> [model] [use_cache]")
        sys.exit(1)
    
    prompt = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "claude-3-5-sonnet-20241022"
    use_cache = sys.argv[3].lower() == "true" if len(sys.argv) > 3 else True
    
    claude = CachedClaude()
    response = claude.call(prompt, model=model, use_cache=use_cache)
    
    print("\nResponse:")
    for block in response["content"]:
        if block["type"] == "text":
            print(block["text"])
    
    print(f"\nUsage: {response['usage']['input_tokens']} input + {response['usage']['output_tokens']} output tokens")

