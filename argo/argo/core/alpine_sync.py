#!/usr/bin/env python3
"""
Alpine Backend Signal Sync Service
Sends signals from Argo to Alpine backend for storage in production database

This service handles:
- HTTP POST requests to Alpine backend
- Authentication with API key
- Retry logic for failed syncs
- Error handling and logging
"""
import httpx
import logging
import os
import asyncio
import time
from typing import Dict, Optional, List
from datetime import datetime, timezone
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class AlpineSyncService:
    """Sync signals from Argo to Alpine backend"""
    
    def __init__(self):
        # Get configuration from environment or config
        self.alpine_url = self._get_alpine_url()
        self.api_key = self._get_api_key()
        self.endpoint = f"{self.alpine_url}/api/v1/external-signals/sync/signal"
        self.health_endpoint = f"{self.alpine_url}/api/v1/external-signals/sync/health"
        
        # HTTP client with timeout
        # OPTIMIZATION: Connection pooling and keepalive for better performance
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        
        # Failed signals queue (for retry)
        self._failed_signals: List[Dict] = []
        self._sync_enabled = self._check_sync_enabled()
        
        # OPTIMIZATION: Health check caching to reduce unnecessary checks
        self._health_check_cache: Optional[bool] = None
        self._health_check_cache_time: Optional[float] = None
        self._health_check_cache_ttl = 60.0  # Cache health check for 60 seconds
        
        if self._sync_enabled:
            logger.info(f"✅ Alpine sync service initialized: {self.alpine_url}")
        else:
            logger.warning("⚠️  Alpine sync disabled (missing configuration)")
    
    def _get_alpine_url(self) -> str:
        """Get Alpine API URL from environment or config"""
        # Try environment variable first
        alpine_url = os.getenv('ALPINE_API_URL')
        if alpine_url:
            return alpine_url.rstrip('/')
        
        # Try config.json
        try:
            from argo.core.config_loader import ConfigLoader
            config, _ = ConfigLoader.load_config()
            if config and 'alpine' in config:
                alpine_url = config['alpine'].get('api_url')
                if alpine_url:
                    return alpine_url.rstrip('/')
        except Exception as e:
            logger.debug(f"Could not load Alpine URL from config: {e}")
        
        # Default (production)
        return 'http://91.98.153.49:8001'
    
    def _get_api_key(self) -> str:
        """Get API key from environment or secrets manager"""
        # Try environment variable first
        api_key = os.getenv('ARGO_API_KEY')
        if api_key:
            return api_key
        
        # Try AWS Secrets Manager
        try:
            from argo.utils.secrets_manager import get_secret
            api_key = get_secret('argo-api-key', service='argo')
            if api_key:
                return api_key
        except Exception as e:
            logger.debug(f"Could not get API key from secrets manager: {e}")
        
        # Try config.json
        try:
            from argo.core.config_loader import ConfigLoader
            config_api_keys, _ = ConfigLoader.load_api_keys()
            if config_api_keys and 'argo_api_key' in config_api_keys:
                return config_api_keys['argo_api_key']
        except Exception as e:
            logger.debug(f"Could not load API key from config: {e}")
        
        return ''
    
    def _check_sync_enabled(self) -> bool:
        """Check if sync is enabled (has required configuration)"""
        if not self.alpine_url or not self.api_key:
            return False
        
        # Check if explicitly disabled
        sync_enabled = os.getenv('ALPINE_SYNC_ENABLED', 'true').lower()
        if sync_enabled == 'false':
            return False
        
        return True
    
    async def check_health(self) -> bool:
        """Check if Alpine backend is reachable"""
        # OPTIMIZATION: Cache health check results to reduce API calls
        import time
        current_time = time.time()
        
        # Check cache first
        if (
            self._health_check_cache is not None
            and self._health_check_cache_time is not None
            and (current_time - self._health_check_cache_time) < self._health_check_cache_ttl
        ):
            return self._health_check_cache
        
        # Perform actual health check
        try:
            response = await self.client.get(self.health_endpoint, timeout=5.0)
            is_healthy = response.status_code == 200
            
            # Cache result
            self._health_check_cache = is_healthy
            self._health_check_cache_time = current_time
            
            if is_healthy:
                logger.debug("✅ Alpine backend health check passed")
            else:
                logger.warning(f"⚠️  Alpine backend health check failed: {response.status_code}")
            
            return is_healthy
        except Exception as e:
            # Cache negative result too (but with shorter TTL)
            self._health_check_cache = False
            self._health_check_cache_time = current_time
            logger.warning(f"⚠️  Alpine backend health check error: {e}")
            return False
    
    async def sync_signal(self, signal: Dict, retry_count: int = 0) -> bool:
        """
        Send signal to Alpine backend
        
        Args:
            signal: Signal dictionary with all required fields
            retry_count: Current retry attempt (for internal use)
        
        Returns:
            True if sync successful, False otherwise
        """
        if not self._sync_enabled:
            logger.debug("Alpine sync disabled, skipping")
            return False
        
        try:
            # Prepare payload
            payload = {
                "signal_id": signal.get('signal_id', ''),
                "symbol": signal.get('symbol', ''),
                "action": signal.get('action', ''),
                "entry_price": float(signal.get('entry_price', 0)),
                "target_price": signal.get('target_price') or signal.get('take_profit'),
                "stop_price": signal.get('stop_price') or signal.get('stop_loss'),
                "confidence": float(signal.get('confidence', 0)),
                "strategy": signal.get('strategy', 'weighted_consensus_v6'),
                "asset_type": signal.get('asset_type', 'stock'),
                "data_source": signal.get('data_source', 'weighted_consensus'),
                "timestamp": signal.get('timestamp', datetime.now(timezone.utc).isoformat()),
                "sha256": signal.get('sha256') or signal.get('verification_hash', ''),
                "verification_hash": signal.get('sha256') or signal.get('verification_hash', ''),
                "reasoning": signal.get('reasoning') or signal.get('rationale', ''),
                "regime": signal.get('regime'),
                "consensus_agreement": signal.get('consensus_agreement'),
                "sources_count": signal.get('sources_count')
            }
            
            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}
            
            # Prepare headers
            headers = {
                "X-API-Key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Send request
            response = await self.client.post(
                self.endpoint,
                json=payload,
                headers=headers
            )
            
            # Handle response
            if response.status_code == 201:
                result = response.json()
                logger.info(
                    f"✅ Signal synced to Alpine: {signal.get('signal_id', 'unknown')} "
                    f"({signal.get('symbol', 'unknown')} {signal.get('action', 'unknown')})"
                )
                return True
            elif response.status_code == 409:
                # Duplicate signal (already exists) - this is OK
                logger.debug(f"Signal already exists in Alpine: {signal.get('signal_id', 'unknown')}")
                return True
            elif response.status_code == 401:
                logger.error("❌ Authentication failed - check ARGO_API_KEY")
                return False
            elif response.status_code == 400:
                logger.error(f"❌ Bad request: {response.text}")
                return False
            else:
                logger.error(
                    f"❌ Failed to sync signal: HTTP {response.status_code} - {response.text[:200]}"
                )
                
                # Retry on server errors (5xx)
                if response.status_code >= 500 and retry_count < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (retry_count + 1))
                    return await self.sync_signal(signal, retry_count + 1)
                
                return False
                
        except httpx.TimeoutException:
            logger.error(f"❌ Timeout syncing signal to Alpine: {signal.get('signal_id', 'unknown')}")
            
            # Retry on timeout
            if retry_count < self.max_retries:
                await asyncio.sleep(self.retry_delay * (retry_count + 1))
                return await self.sync_signal(signal, retry_count + 1)
            
            return False
            
        except httpx.ConnectError:
            logger.error(f"❌ Connection error - Alpine backend unreachable: {self.alpine_url}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error syncing signal to Alpine: {e}", exc_info=True)
            return False
    
    async def sync_signal_batch(self, signals: List[Dict]) -> Dict[str, int]:
        """
        Sync multiple signals in batch
        
        Returns:
            Dictionary with success and failure counts
        """
        if not self._sync_enabled:
            return {"success": 0, "failed": len(signals), "skipped": len(signals)}
        
        results = {"success": 0, "failed": 0}
        
        # Sync signals in parallel (with limit)
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
        
        async def sync_with_limit(signal):
            async with semaphore:
                success = await self.sync_signal(signal)
                return success
        
        tasks = [sync_with_limit(signal) for signal in signals]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results_list:
            if isinstance(result, Exception):
                logger.error(f"Exception in batch sync: {result}")
                results["failed"] += 1
            elif result:
                results["success"] += 1
            else:
                results["failed"] += 1
        
        logger.info(
            f"📊 Batch sync complete: {results['success']} success, "
            f"{results['failed']} failed out of {len(signals)} signals"
        )
        
        return results
    
    def queue_failed_signal(self, signal: Dict):
        """Queue a failed signal for retry later"""
        self._failed_signals.append(signal)
        logger.debug(f"Queued failed signal for retry: {signal.get('signal_id', 'unknown')}")
    
    async def retry_failed_signals(self) -> int:
        """Retry all queued failed signals"""
        if not self._failed_signals:
            return 0
        
        signals_to_retry = self._failed_signals.copy()
        self._failed_signals.clear()
        
        logger.info(f"🔄 Retrying {len(signals_to_retry)} failed signals")
        results = await self.sync_signal_batch(signals_to_retry)
        
        # Re-queue signals that still failed
        # (This would require tracking which signals failed, simplified here)
        
        return results["success"]
    
    async def close(self):
        """Close HTTP client"""
        try:
            await self.client.aclose()
            logger.debug("Alpine sync service closed")
        except Exception as e:
            logger.debug(f"Error closing Alpine sync service: {e}")


# Global instance
_alpine_sync_service: Optional[AlpineSyncService] = None


def get_alpine_sync_service() -> AlpineSyncService:
    """Get or create global Alpine sync service instance"""
    global _alpine_sync_service
    if _alpine_sync_service is None:
        _alpine_sync_service = AlpineSyncService()
    return _alpine_sync_service

