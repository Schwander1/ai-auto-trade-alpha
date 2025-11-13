#!/usr/bin/env python3
"""
Alpine Backend API Sync
Syncs signals from Argo to Alpine Analytics via secure API
Maintains separation: Argo sends via API, Alpine stores in its own database
"""
import logging
import os
import sys
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger("AlpineSync")

# Try to import httpx for API calls
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    logger.warning("httpx not available - Alpine sync disabled")

class AlpineBackendSync:
    """
    Syncs signals to Alpine Analytics via secure API
    Maintains separation: Argo sends via API, Alpine stores in its own database
    """
    
    def __init__(self):
        self.enabled = False
        self.api_url = None
        self.api_key = None
        
        if not HTTPX_AVAILABLE:
            logger.warning("⚠️  Alpine sync disabled: httpx not available")
            return
        
        # Get Alpine API URL and API key
        self.api_url = self._get_alpine_api_url()
        self.api_key = self._get_api_key()
        
        if not self.api_url or not self.api_key:
            logger.warning("⚠️  Alpine sync disabled: API URL or API key not configured")
            return
        
        self.enabled = True
        logger.info("✅ Alpine Backend API sync initialized")
    
    def _get_alpine_api_url(self) -> Optional[str]:
        """Get Alpine Backend API URL from AWS Secrets Manager or environment"""
        try:
            # Try AWS Secrets Manager first
            import sys
            from pathlib import Path
            
            shared_path = Path(__file__).parent.parent.parent.parent.parent / "packages" / "shared"
            if shared_path.exists():
                sys.path.insert(0, str(shared_path))
            
            try:
                from utils.secrets_manager import get_secret
                api_url = get_secret("alpine-api-url", service="argo")
                if api_url:
                    return api_url
            except ImportError:
                pass
            except Exception as e:
                logger.debug(f"Secrets Manager error: {e}")
            
            # Fallback to environment variable
            return os.getenv("ALPINE_API_URL") or "http://localhost:9001"
        
        except Exception as e:
            logger.debug(f"Error getting Alpine API URL: {e}")
            return None
    
    def _get_api_key(self) -> Optional[str]:
        """Get Argo API key for authenticating with Alpine Backend"""
        try:
            # Try AWS Secrets Manager first
            import sys
            from pathlib import Path
            
            shared_path = Path(__file__).parent.parent.parent.parent.parent / "packages" / "shared"
            if shared_path.exists():
                sys.path.insert(0, str(shared_path))
            
            try:
                from utils.secrets_manager import get_secret
                api_key = get_secret("argo-api-key", service="argo")
                if api_key:
                    return api_key
            except ImportError:
                pass
            except Exception as e:
                logger.debug(f"Secrets Manager error: {e}")
            
            # Fallback to environment variable
            return os.getenv("ARGO_API_KEY")
        
        except Exception as e:
            logger.debug(f"Error getting API key: {e}")
            return None
    
    def sync_signal(self, signal: Dict) -> bool:
        """
        Sync a signal to Alpine Analytics via secure API
        
        Args:
            signal: Signal dictionary with all signal data
        
        Returns:
            bool: True if synced successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            # Prepare signal data for API
            verification_hash = signal.get('sha256') or signal.get('verification_hash')
            if not verification_hash:
                logger.warning("Signal missing verification hash, skipping sync")
                return False
            
            # Prepare payload
            payload = {
                "signal_id": signal.get('signal_id', ''),
                "symbol": signal.get('symbol'),
                "action": signal.get('action'),
                "entry_price": signal.get('entry_price') or signal.get('price'),
                "target_price": signal.get('target_price') or signal.get('take_profit'),
                "stop_price": signal.get('stop_price') or signal.get('stop_loss'),
                "confidence": signal.get('confidence', 0),
                "strategy": signal.get('strategy', 'weighted_consensus_v6'),
                "asset_type": signal.get('asset_type', 'stock'),
                "data_source": signal.get('data_source', 'weighted_consensus'),
                "timestamp": signal.get('timestamp', datetime.utcnow().isoformat()),
                "sha256": verification_hash,
                "verification_hash": verification_hash,
                "reasoning": signal.get('reasoning'),
                "regime": signal.get('regime'),
                "consensus_agreement": signal.get('consensus_agreement'),
                "sources_count": signal.get('sources_count')
            }
            
            # Send to Alpine API (use sync httpx for compatibility)
            sync_url = f"{self.api_url}/api/v1/argo/sync/signal"
            
            try:
                # Use sync client (works in both sync and async contexts)
                with httpx.Client(timeout=10.0) as client:
                    response = client.post(
                        sync_url,
                        json=payload,
                        headers={
                            "X-API-Key": self.api_key,
                            "Content-Type": "application/json"
                        }
                    )
                    response.raise_for_status()
                    result = response.json()
                    logger.info(f"✅ Signal synced to Alpine: {signal.get('symbol')} {signal.get('action')}")
                    return True
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 409 or "duplicate" in str(e.response.text).lower():
                    logger.debug(f"Signal {verification_hash[:8]} already exists in Alpine")
                    return True  # Not an error, just a duplicate
                logger.error(f"❌ Alpine API error: {e.response.status_code} - {e.response.text}")
                return False
            except Exception as e:
                logger.error(f"❌ Error syncing signal to Alpine API: {e}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Alpine sync error: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test connection to Alpine Backend API"""
        if not self.enabled:
            return False
        
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(
                    f"{self.api_url}/api/v1/argo/sync/health",
                    headers={"X-API-Key": self.api_key} if self.api_key else {}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Alpine API connection test failed: {e}")
            return False

# Global instance
_alpine_sync: Optional[AlpineBackendSync] = None

def get_alpine_sync() -> AlpineBackendSync:
    """Get or create global Alpine sync instance"""
    global _alpine_sync
    if _alpine_sync is None:
        _alpine_sync = AlpineBackendSync()
    return _alpine_sync

