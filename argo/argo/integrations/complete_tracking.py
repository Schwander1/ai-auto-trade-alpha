"""
Complete Live Tracking
Every signal → Notion Pro (instant) + Tradervue Gold (instant) + Power BI (streaming)
"""
import requests
import os
import sys
from datetime import datetime
from pathlib import Path

# Add shared package to path
shared_path = Path(__file__).parent.parent.parent.parent.parent / "packages" / "shared"
if shared_path.exists():
    sys.path.insert(0, str(shared_path))

try:
    from utils.secrets_manager import get_secret
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False

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
        if SECRETS_MANAGER_AVAILABLE:
            try:
                self.tradervue_user = get_secret("tradervue-username", service=service) or os.getenv('TRADERVUE_USERNAME', '')
                self.tradervue_token = get_secret("tradervue-api-token", service=service) or os.getenv('TRADERVUE_API_TOKEN', '')
            except Exception:
                self.tradervue_user = os.getenv('TRADERVUE_USERNAME', '')
                self.tradervue_token = os.getenv('TRADERVUE_API_TOKEN', '')
        else:
            self.tradervue_user = os.getenv('TRADERVUE_USERNAME', '')
            self.tradervue_token = os.getenv('TRADERVUE_API_TOKEN', '')
        
        self.tradervue_enabled = bool(self.tradervue_user)
        
        # Power BI - Try AWS Secrets Manager first, fallback to env
        if SECRETS_MANAGER_AVAILABLE:
            try:
                self.powerbi_url = get_secret("powerbi-stream-url", service=service) or os.getenv('POWERBI_STREAM_URL', '')
            except Exception:
                self.powerbi_url = os.getenv('POWERBI_STREAM_URL', '')
        else:
            self.powerbi_url = os.getenv('POWERBI_STREAM_URL', '')
        
        self.powerbi_enabled = bool(self.powerbi_url)
        
        print(f"✅ Tracking: Notion {'✅' if self.notion_enabled else '❌'} | Tradervue {'✅' if self.tradervue_enabled else '❌'} | Power BI {'✅' if self.powerbi_enabled else '❌'}")
    
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
        
        # Log to Tradervue Gold (real-time, not daily batch)
        if self.tradervue_enabled:
            try:
                requests.post(
                    "https://www.tradervue.com/api/v1/trades",
                    auth=(self.tradervue_user, self.tradervue_token),
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
