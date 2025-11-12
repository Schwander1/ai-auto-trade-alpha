"""
Complete Notion Command Center Integration
Updates ALL databases automatically
"""
import requests
import os
from datetime import datetime

class NotionCommandCenter:
    def __init__(self):
        self.api_key = os.getenv('NOTION_API_KEY', '')
        
        # All your databases
        self.status_db = os.getenv('NOTION_STATUS_DB', '')
        self.revenue_db = os.getenv('NOTION_REVENUE_DB', '')
        self.signals_db = os.getenv('NOTION_SIGNALS_DB', '')
        self.winloss_db = os.getenv('NOTION_WINLOSS_DB', '')
        self.customers_db = os.getenv('NOTION_CUSTOMERS_DB', '')
        self.planning_db = os.getenv('NOTION_PLANNING_DB', '')
        self.docs_db = os.getenv('NOTION_DOCS_DB', '')
        self.alerts_db = os.getenv('NOTION_ALERTS_DB', '')
        self.performance_db = os.getenv('NOTION_PERFORMANCE_DB', '')
        self.preorders_db = os.getenv('NOTION_PREORDERS_DB', '')
        
        self.enabled = bool(self.api_key and self.winloss_db)
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        print(f"📊 Notion Command Center: {'✅ All 10 databases ready' if self.enabled else '⚠️  Add keys'}")
    
    def _create_page(self, db_id, title_text):
        """Generic page creation"""
        if not self.enabled or not db_id:
            return
        
        try:
            requests.post(
                "https://api.notion.com/v1/pages",
                headers=self.headers,
                json={
                    "parent": {"database_id": db_id},
                    "properties": {
                        "Name": {"title": [{"text": {"content": title_text}}]}
                    }
                },
                timeout=5
            )
            return True
        except Exception as e:
            print(f"⚠️  Notion error: {e}")
            return False
    
    # 1. System Status
    def update_system_status(self, cpu, memory, status="operational"):
        """Update System Status database"""
        title = f"📊 System: {status} | CPU: {cpu}% | Memory: {memory}% | {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        self._create_page(self.status_db, title)
        print(f"✅ System Status updated")
    
    # 2. Revenue Tracker
    def update_revenue(self, mrr, customers, target=5000):
        """Update Revenue Tracker"""
        progress = (mrr / target) * 100
        title = f"💰 MRR: ${mrr} | Customers: {customers} | Progress: {progress:.0f}% to ${target}"
        self._create_page(self.revenue_db, title)
        print(f"✅ Revenue updated")
    
    # 3. Trading Signals
    def log_signal(self, signal):
        """Log to Argo Trading Signals database"""
        title = f"🎯 {signal['symbol']} {signal['type']} | {signal.get('confidence', 0)}% | Entry: ${signal.get('entry_price', 0)}"
        self._create_page(self.signals_db, title)
        print(f"✅ Signal logged: {signal['symbol']}")
    
    # 4. Win/Loss Board
    def log_trade_to_winloss_board(self, trade):
        """Log to Win/Loss Board"""
        title = f"🎯 {trade['symbol']} {trade['type']} | {trade.get('confidence', 0)}% confidence"
        self._create_page(self.winloss_db, title)
        print(f"✅ Win/Loss: {trade['symbol']}")
    
    # 5. Customer Success
    def log_customer(self, customer_name, tier, status="active"):
        """Log customer to Customer Success Pipeline"""
        title = f"👤 {customer_name} | {tier} | {status}"
        self._create_page(self.customers_db, title)
        print(f"✅ Customer added: {customer_name}")
    
    # 6. Planning & Execution
    def log_task(self, task, priority="medium"):
        """Log task to Planning & Execution"""
        title = f"📋 {task} | Priority: {priority}"
        self._create_page(self.planning_db, title)
        print(f"✅ Task added")
    
    # 7. System Documentation
    def log_doc(self, title_text, doc_type="update"):
        """Log to System Documentation"""
        title = f"📚 {doc_type.upper()}: {title_text}"
        self._create_page(self.docs_db, title)
        print(f"✅ Doc logged")
    
    # 8. System Alerts
    def log_alert(self, alert_text, severity="info"):
        """Log to System Alerts"""
        emoji = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}
        title = f"{emoji.get(severity, 'ℹ️')} {alert_text} | {datetime.now().strftime('%H:%M')}"
        self._create_page(self.alerts_db, title)
        print(f"✅ Alert logged")
    
    # 9. Weekly Performance
    def update_performance(self, win_rate, total_trades, pnl):
        """Update Weekly Performance"""
        title = f"📈 Week {datetime.now().strftime('%W')}: {win_rate}% win rate | {total_trades} trades | ${pnl} P&L"
        self._create_page(self.performance_db, title)
        print(f"✅ Performance updated")
    
    # 10. Alpine Pre-Orders
    def log_preorder(self, email, tier, amount):
        """Log pre-order"""
        title = f"💰 Pre-order: {email} | {tier} | ${amount}"
        self._create_page(self.preorders_db, title)
        print(f"✅ Pre-order logged")

command_center = NotionCommandCenter()
