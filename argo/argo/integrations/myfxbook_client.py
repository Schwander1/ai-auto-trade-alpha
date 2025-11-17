"""
MyFXBook Integration Client
Reference implementation following existing integration patterns
"""
import requests
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

# Use Argo-specific secrets manager
try:
    from argo.utils.secrets_manager import get_secret
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False

logger = logging.getLogger(__name__)


class MyFXBookClient:
    """
    MyFXBook API Client
    
    Follows the same pattern as other integrations (Notion, Tradervue, etc.)
    Uses AWS Secrets Manager with fallback to environment variables
    """
    
    BASE_URL = "https://www.myfxbook.com/api"
    
    def __init__(self):
        """Initialize MyFXBook client with credentials"""
        service = "argo"
        
        # Try AWS Secrets Manager first, fallback to environment variables
        if SECRETS_MANAGER_AVAILABLE:
            try:
                self.email = get_secret("myfxbook-email", service=service) or os.getenv('MYFXBOOK_EMAIL', '')
                self.password = get_secret("myfxbook-password", service=service) or os.getenv('MYFXBOOK_PASSWORD', '')
                self.account_id = get_secret("myfxbook-account-id", service=service) or os.getenv('MYFXBOOK_ACCOUNT_ID', '')
            except Exception:
                # Fallback to environment variables
                self.email = os.getenv('MYFXBOOK_EMAIL', '')
                self.password = os.getenv('MYFXBOOK_PASSWORD', '')
                self.account_id = os.getenv('MYFXBOOK_ACCOUNT_ID', '')
        else:
            self.email = os.getenv('MYFXBOOK_EMAIL', '')
            self.password = os.getenv('MYFXBOOK_PASSWORD', '')
            self.account_id = os.getenv('MYFXBOOK_ACCOUNT_ID', '')
        
        self.enabled = bool(self.email and self.password)
        self.session = requests.Session()
        self.session_token: Optional[str] = None
        self.logged_in = False
        
        if self.enabled:
            logger.info("✅ MyFXBook client initialized")
        else:
            logger.warning("⚠️  MyFXBook credentials not configured")
    
    def login(self) -> bool:
        """
        Login and get session token
        
        Note: Sessions are IP-bound and expire after 1 month
        """
        if not self.enabled:
            logger.warning("MyFXBook not enabled - cannot login")
            return False
        
        try:
            response = self.session.post(
                f"{self.BASE_URL}/login.json",
                json={
                    "email": self.email,
                    "password": self.password
                },
                timeout=10
            )
            data = response.json()
            
            if data.get("error"):
                error_msg = data.get("message", "Unknown error")
                logger.error(f"MyFXBook login error: {error_msg}")
                return False
            
            self.session_token = data.get("session")
            self.logged_in = True
            logger.info("✅ MyFXBook login successful")
            return True
        except Exception as e:
            logger.error(f"MyFXBook login failed: {e}")
            return False
    
    def logout(self) -> bool:
        """Logout and revoke session"""
        if not self.logged_in:
            return True
        
        try:
            response = self.session.post(
                f"{self.BASE_URL}/logout.json",
                json={"session": self.session_token},
                timeout=10
            )
            self.logged_in = False
            self.session_token = None
            logger.info("✅ MyFXBook logout successful")
            return True
        except Exception as e:
            logger.error(f"MyFXBook logout failed: {e}")
            return False
    
    def get_accounts(self) -> List[Dict]:
        """Get user's accounts"""
        if not self.enabled:
            return []
        
        if not self.logged_in:
            if not self.login():
                return []
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/get-my-accounts.json",
                params={"session": self.session_token},
                timeout=10
            )
            data = response.json()
            
            if data.get("error"):
                error_msg = data.get("message", "Unknown error")
                logger.error(f"MyFXBook error: {error_msg}")
                return []
            
            return data.get("accounts", [])
        except Exception as e:
            logger.error(f"Failed to get accounts: {e}")
            return []
    
    def get_account_details(self, account_id: Optional[int] = None) -> Dict:
        """Get account details and performance metrics"""
        if not self.enabled:
            return {}
        
        if not self.logged_in:
            if not self.login():
                return {}
        
        account_id = account_id or self.account_id
        if not account_id:
            logger.error("No account ID provided")
            return {}
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/get-account.json",
                params={
                    "session": self.session_token,
                    "id": account_id
                },
                timeout=10
            )
            data = response.json()
            
            if data.get("error"):
                error_msg = data.get("message", "Unknown error")
                logger.error(f"MyFXBook error: {error_msg}")
                return {}
            
            return data.get("account", {})
        except Exception as e:
            logger.error(f"Failed to get account details: {e}")
            return {}
    
    def get_open_trades(self, account_id: Optional[int] = None) -> List[Dict]:
        """Get open trades for account"""
        if not self.enabled:
            return []
        
        if not self.logged_in:
            if not self.login():
                return []
        
        account_id = account_id or self.account_id
        if not account_id:
            logger.error("No account ID provided")
            return []
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/get-open-trades.json",
                params={
                    "session": self.session_token,
                    "id": account_id
                },
                timeout=10
            )
            data = response.json()
            
            if data.get("error"):
                error_msg = data.get("message", "Unknown error")
                logger.error(f"MyFXBook error: {error_msg}")
                return []
            
            return data.get("trades", [])
        except Exception as e:
            logger.error(f"Failed to get open trades: {e}")
            return []
    
    def get_trading_history(
        self, 
        account_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """Get trading history for account"""
        if not self.enabled:
            return []
        
        if not self.logged_in:
            if not self.login():
                return []
        
        account_id = account_id or self.account_id
        if not account_id:
            logger.error("No account ID provided")
            return []
        
        params = {
            "session": self.session_token,
            "id": account_id
        }
        
        if start_date:
            params["start"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["end"] = end_date.strftime("%Y-%m-%d")
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/get-history.json",
                params=params,
                timeout=10
            )
            data = response.json()
            
            if data.get("error"):
                error_msg = data.get("message", "Unknown error")
                logger.error(f"MyFXBook error: {error_msg}")
                return []
            
            return data.get("history", [])
        except Exception as e:
            logger.error(f"Failed to get trading history: {e}")
            return []
    
    def get_performance_metrics(self, account_id: Optional[int] = None) -> Dict:
        """
        Get comprehensive performance metrics
        
        Returns metrics like:
        - Total profit/loss
        - Win rate
        - Sharpe ratio
        - Max drawdown
        - Profit factor
        - etc.
        """
        account_details = self.get_account_details(account_id)
        
        if not account_details:
            return {}
        
        # Extract performance metrics from account details
        # Structure depends on MyFXBook API response
        return {
            "account_id": account_details.get("id"),
            "balance": account_details.get("balance", 0),
            "equity": account_details.get("equity", 0),
            "profit": account_details.get("profit", 0),
            "profit_percent": account_details.get("profitPercent", 0),
            "daily_gain": account_details.get("dailyGain", 0),
            "daily_gain_percent": account_details.get("dailyGainPercent", 0),
            "monthly_gain": account_details.get("monthlyGain", 0),
            "monthly_gain_percent": account_details.get("monthlyGainPercent", 0),
            "drawdown": account_details.get("drawdown", 0),
            "drawdown_percent": account_details.get("drawdownPercent", 0),
            "max_drawdown": account_details.get("maxDrawdown", 0),
            "max_drawdown_percent": account_details.get("maxDrawdownPercent", 0),
            "win_rate": account_details.get("winRate", 0),
            "profit_factor": account_details.get("profitFactor", 0),
            "sharpe_ratio": account_details.get("sharpeRatio", 0),
            "verified": account_details.get("verified", False)
        }
    
    def get_widget_url(self, widget_type: str = "balance", account_id: Optional[int] = None) -> Optional[str]:
        """
        Get widget URL for embedding
        
        Widget types: balance, growth, etc.
        """
        if not self.enabled:
            return None
        
        account_id = account_id or self.account_id
        if not account_id:
            return None
        
        # MyFXBook widget URLs typically follow this pattern:
        # https://www.myfxbook.com/widgets/{account_id}/{widget_type}
        return f"https://www.myfxbook.com/widgets/{account_id}/{widget_type}"


# Singleton instance (following pattern from complete_tracking.py)
_client_instance: Optional[MyFXBookClient] = None

def get_myfxbook_client() -> MyFXBookClient:
    """Get singleton MyFXBook client instance"""
    global _client_instance
    if _client_instance is None:
        _client_instance = MyFXBookClient()
    return _client_instance

