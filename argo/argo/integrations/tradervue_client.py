"""
Enhanced Tradervue Integration Client
Complete trade lifecycle tracking with performance metrics sync
"""
import requests
import os
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

# Use Argo-specific secrets manager
try:
    from argo.utils.secrets_manager import get_secret
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class TradervueTrade:
    """Tradervue trade data structure"""
    symbol: str
    quantity: float
    date: str  # YYYY-MM-DD
    price: float
    side: str  # "B" for buy, "SS" for short sell, "S" for sell (close)
    notes: Optional[str] = None
    commission: Optional[float] = None
    trade_id: Optional[str] = None  # For updating existing trades


class TradervueClient:
    """
    Enhanced Tradervue API Client
    
    Features:
    - Complete trade lifecycle tracking (entry + exit)
    - Automatic retry with exponential backoff
    - Performance metrics sync
    - Widget URL generation
    - Error handling and logging
    """
    
    BASE_URL = "https://www.tradervue.com/api/v1"
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    def __init__(self):
        """Initialize Tradervue client with credentials (username and password)"""
        service = "argo"
        
        # Try AWS Secrets Manager first, fallback to environment variables
        if SECRETS_MANAGER_AVAILABLE:
            try:
                self.username = get_secret("tradervue-username", service=service) or os.getenv('TRADERVUE_USERNAME', '')
                self.password = get_secret("tradervue-password", service=service) or os.getenv('TRADERVUE_PASSWORD', '')
            except Exception:
                self.username = os.getenv('TRADERVUE_USERNAME', '')
                self.password = os.getenv('TRADERVUE_PASSWORD', '')
        else:
            self.username = os.getenv('TRADERVUE_USERNAME', '')
            self.password = os.getenv('TRADERVUE_PASSWORD', '')
        
        self.enabled = bool(self.username and self.password)
        self.session = requests.Session()
        # Tradervue uses HTTP Basic Auth with username and password
        self.session.auth = (self.username, self.password)
        
        # Track synced trades to avoid duplicates
        self._synced_trade_ids = set()
        
        if self.enabled:
            logger.info("✅ Tradervue client initialized")
        else:
            logger.warning("⚠️  Tradervue credentials not configured")
    
    def submit_trade(
        self, 
        trade: TradervueTrade,
        retry_count: int = 0
    ) -> Optional[Dict]:
        """
        Submit trade to Tradervue with retry logic
        
        Args:
            trade: TradervueTrade object
            retry_count: Current retry attempt
            
        Returns:
            Response data or None if failed
        """
        if not self.enabled:
            logger.warning("Tradervue not enabled - cannot submit trade")
            return None
        
        try:
            payload = {
                "symbol": trade.symbol,
                "quantity": trade.quantity,
                "date": trade.date,
                "price": trade.price,
                "side": trade.side
            }
            
            if trade.notes:
                payload["notes"] = trade.notes
            
            if trade.commission:
                payload["commission"] = trade.commission
            
            # If trade_id provided, update existing trade
            if trade.trade_id:
                payload["id"] = trade.trade_id
            
            response = self.session.post(
                f"{self.BASE_URL}/trades",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                logger.info(f"✅ Tradervue: {trade.symbol} {trade.side} synced")
                return data
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Tradervue API error: {error_msg}")
                
                # Retry on server errors
                if response.status_code >= 500 and retry_count < self.MAX_RETRIES:
                    time.sleep(self.RETRY_DELAY * (2 ** retry_count))  # Exponential backoff
                    return self.submit_trade(trade, retry_count + 1)
                
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Tradervue request failed: {e}")
            
            # Retry on network errors
            if retry_count < self.MAX_RETRIES:
                time.sleep(self.RETRY_DELAY * (2 ** retry_count))
                return self.submit_trade(trade, retry_count + 1)
            
            return None
        except Exception as e:
            logger.error(f"Unexpected error submitting trade to Tradervue: {e}")
            return None
    
    def update_trade(
        self,
        trade_id: str,
        trade: TradervueTrade
    ) -> Optional[Dict]:
        """
        Update existing trade in Tradervue
        
        Args:
            trade_id: Tradervue trade ID
            trade: Updated trade data
            
        Returns:
            Response data or None if failed
        """
        trade.trade_id = trade_id
        return self.submit_trade(trade)
    
    def get_trades(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        symbol: Optional[str] = None
    ) -> List[Dict]:
        """
        Get trades from Tradervue
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            symbol: Filter by symbol
            
        Returns:
            List of trades
        """
        if not self.enabled:
            return []
        
        try:
            params = {}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            if symbol:
                params["symbol"] = symbol
            
            response = self.session.get(
                f"{self.BASE_URL}/trades",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get("trades", [])
            else:
                logger.error(f"Failed to get trades: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting trades from Tradervue: {e}")
            return []
    
    def get_performance_metrics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get performance metrics from Tradervue
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Performance metrics dict or None
        """
        if not self.enabled:
            return None
        
        try:
            params = {}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            
            response = self.session.get(
                f"{self.BASE_URL}/performance",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Performance metrics endpoint may not be available: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.warning(f"Could not get performance metrics: {e}")
            return None
    
    def get_widget_url(
        self,
        widget_type: str = "equity",
        width: int = 600,
        height: int = 400
    ) -> Optional[str]:
        """
        Get widget URL for embedding
        
        Widget types: equity, trades, performance, etc.
        
        Args:
            widget_type: Type of widget
            width: Widget width
            height: Widget height
            
        Returns:
            Widget URL or None
        """
        if not self.enabled:
            return None
        
        # Tradervue widget URLs typically follow this pattern:
        # https://www.tradervue.com/widgets/{username}/{widget_type}?width={width}&height={height}
        return f"https://www.tradervue.com/widgets/{self.username}/{widget_type}?width={width}&height={height}"
    
    def get_profile_url(self) -> Optional[str]:
        """Get public profile URL"""
        if not self.enabled:
            return None
        return f"https://www.tradervue.com/profile/{self.username}"


# Singleton instance
_client_instance: Optional[TradervueClient] = None

def get_tradervue_client() -> TradervueClient:
    """Get singleton Tradervue client instance"""
    global _client_instance
    if _client_instance is None:
        _client_instance = TradervueClient()
    return _client_instance

