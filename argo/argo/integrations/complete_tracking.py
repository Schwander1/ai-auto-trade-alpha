"""
Complete Live Tracking
Every signal → Notion Pro (instant) + Tradervue Gold (instant) + Power BI (streaming)
Enhanced with complete trade lifecycle tracking
"""
import requests
import os
import sys
from datetime import datetime
from pathlib import Path

# Use Argo-specific secrets manager
try:
    from argo.utils.secrets_manager import get_secret
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False

# Enhanced Tradervue integration
try:
    from argo.integrations.tradervue_integration import get_tradervue_integration
    TRADERVUE_INTEGRATION_AVAILABLE = True
except ImportError:
    TRADERVUE_INTEGRATION_AVAILABLE = False

class LiveTracker:
    def __init__(self):
        service = "argo"
        
        # Notion Pro - Try AWS Secrets Manager first, fallback to env
        if SECRETS_MANAGER_AVAILABLE:
            try:
                self.notion_key = get_secret("notion-api-key", service=service) or os.getenv('NOTION_API_KEY', '')
                self.notion_trades = get_secret("notion-trades-db", service=service) or os.getenv('NOTION_TRADES_DB', '')
            except Exception:
                self.notion_key = os.getenv('NOTION_API_KEY', '')
                self.notion_trades = os.getenv('NOTION_TRADES_DB', '')
        else:
            self.notion_key = os.getenv('NOTION_API_KEY', '')
            self.notion_trades = os.getenv('NOTION_TRADES_DB', '')
        
        self.notion_enabled = bool(self.notion_key and self.notion_trades)
        
        # Tradervue Gold - Try AWS Secrets Manager first, fallback to env
        # Tradervue uses username and password (not API token)
        if SECRETS_MANAGER_AVAILABLE:
            try:
                self.tradervue_user = get_secret("tradervue-username", service=service) or os.getenv('TRADERVUE_USERNAME', '')
                self.tradervue_password = get_secret("tradervue-password", service=service) or os.getenv('TRADERVUE_PASSWORD', '')
            except Exception:
                self.tradervue_user = os.getenv('TRADERVUE_USERNAME', '')
                self.tradervue_password = os.getenv('TRADERVUE_PASSWORD', '')
        else:
            self.tradervue_user = os.getenv('TRADERVUE_USERNAME', '')
            self.tradervue_password = os.getenv('TRADERVUE_PASSWORD', '')
        
        self.tradervue_enabled = bool(self.tradervue_user and self.tradervue_password)
        
        # Power BI - Try AWS Secrets Manager first, fallback to env
        if SECRETS_MANAGER_AVAILABLE:
            try:
                self.powerbi_url = get_secret("powerbi-stream-url", service=service) or os.getenv('POWERBI_STREAM_URL', '')
            except Exception:
                self.powerbi_url = os.getenv('POWERBI_STREAM_URL', '')
        else:
            self.powerbi_url = os.getenv('POWERBI_STREAM_URL', '')
        
        self.powerbi_enabled = bool(self.powerbi_url)
        
        # Enhanced Tradervue integration (if available)
        if self.tradervue_enabled and TRADERVUE_INTEGRATION_AVAILABLE:
            try:
                self.tradervue_integration = get_tradervue_integration()
                self.tradervue_enhanced = self.tradervue_integration.client.enabled
            except Exception as e:
                print(f"⚠️  Tradervue enhanced integration not available: {e}")
                self.tradervue_enhanced = False
                self.tradervue_integration = None
        else:
            self.tradervue_enhanced = False
            self.tradervue_integration = None
        
        print(f"✅ Tracking: Notion {'✅' if self.notion_enabled else '❌'} | Tradervue {'✅' if self.tradervue_enabled else '❌'} {'(Enhanced)' if self.tradervue_enhanced else ''} | Power BI {'✅' if self.powerbi_enabled else '❌'}")
    
    def track_signal_live(self, signal):
        """Track signal in ALL systems IMMEDIATELY"""
        
        # Log to Notion Pro (customers can see transparency)
        if self.notion_enabled:
            try:
                requests.post(
                    "https://api.notion.com/v1/pages",
                    headers={
                        "Authorization": f"Bearer {self.notion_key}",
                        "Notion-Version": "2022-06-28",
                        "Content-Type": "application/json"
                    },
                    json={
                        "parent": {"database_id": self.notion_trades},
                        "properties": {
                            "Symbol": {"title": [{"text": {"content": signal['symbol']}}]},
                            "Type": {"select": {"name": signal['type']}},
                            "Confidence": {"number": signal['confidence']},
                            "Entry": {"number": signal['entry_price']},
                            "Asset": {"select": {"name": signal.get('asset', 'stock')}},
                            "Status": {"select": {"name": "active"}},
                            "Time": {"date": {"start": datetime.now().isoformat()}}
                        }
                    },
                    timeout=5
                )
                print(f"✅ Notion: {signal['symbol']} logged live")
            except Exception as e:
                print(f"Notion error: {e}")
        
        # Enhanced Tradervue tracking (if trade_id available, use enhanced integration)
        if self.tradervue_enabled:
            if self.tradervue_enhanced and signal.get('trade_id'):
                # Use enhanced integration for complete trade tracking
                try:
                    from argo.tracking.unified_tracker import UnifiedPerformanceTracker
                    tracker = UnifiedPerformanceTracker()
                    trade = tracker._get_trade(signal['trade_id'])
                    if trade:
                        tradervue_id = self.tradervue_integration.sync_trade_entry(trade)
                        if tradervue_id:
                            print(f"✅ Tradervue (Enhanced): {signal['symbol']} synced live")
                        else:
                            # Fallback to basic sync
                            self._track_tradervue_basic(signal)
                    else:
                        # Fallback to basic sync
                        self._track_tradervue_basic(signal)
                except Exception as e:
                    print(f"Tradervue enhanced sync error: {e}")
                    # Fallback to basic sync
                    self._track_tradervue_basic(signal)
            else:
                # Basic sync (backward compatible)
                self._track_tradervue_basic(signal)
    
    def _track_tradervue_basic(self, signal):
        """Basic Tradervue tracking (backward compatible)"""
            try:
                requests.post(
                    "https://www.tradervue.com/api/v1/trades",
                auth=(self.tradervue_user, self.tradervue_password),
                    json={
                        "symbol": signal['symbol'],
                        "quantity": signal.get('quantity', 10),
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "price": signal['entry_price'],
                        "side": "B" if signal['type'] == 'long' else "SS",
                        "notes": f"Alpine Analytics | {signal['confidence']}% | SHA256: {signal.get('hash', 'N/A')[:8]}"
                    },
                    timeout=5
                )
                print(f"✅ Tradervue: {signal['symbol']} synced live")
            except Exception as e:
                print(f"Tradervue error: {e}")
        
        # Stream to Power BI (live dashboard updates)
        if self.powerbi_enabled:
            try:
                requests.post(
                    self.powerbi_url,
                    json=[{
                        "timestamp": datetime.now().isoformat(),
                        "symbol": signal['symbol'],
                        "type": signal['type'],
                        "confidence": signal['confidence'],
                        "asset": signal.get('asset', 'stock')
                    }],
                    timeout=5
                )
                print(f"✅ Power BI: {signal['symbol']} streamed")
            except Exception as e:
                print(f"Power BI error: {e}")

tracker = LiveTracker()
