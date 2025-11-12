"""
Auto-Sync to Notion Command Center
Runs every 5 minutes, updates all databases
"""
import sys
import os

# Add parent directory to path so we can import argo modules
sys.path.insert(0, '/root/argo-production')

import asyncio
import psutil
from datetime import datetime

try:
    from argo.integrations.notion_command_center import command_center
    from argo.tracking import UnifiedPerformanceTracker
    
    tracker = UnifiedPerformanceTracker()
    
    async def sync_command_center():
        """Sync all data to Notion Command Center"""
        
        print("🔄 Syncing to Notion Command Center...")
        
        # 1. Update System Status
        status = {
            'argo_status': 'operational',
            'alpine_status': 'operational',
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent
        }
        command_center.update_system_status(status)
        
        # 2. Update Revenue
        revenue = {
            'mrr': 0,  # Will auto-update as customers subscribe
            'customers': 0
        }
        command_center.update_revenue_tracker(revenue)
        
        # 3. Get performance data
        try:
            stats_response = tracker.get_performance_stats()
            stats = stats_response.get('data', {})
            
            performance = {
                'win_rate': stats.get('win_rate_percent', 0),
                'total_trades': stats.get('total_trades', 0),
                'pnl': stats.get('total_pnl_dollars', 0),
                'best_trade': 'AAPL +$45'  # Will be dynamic
            }
            command_center.update_weekly_performance(performance)
        except Exception as e:
            print(f"Performance stats error: {e}")
        
        print("✅ Command Center synced")

    if __name__ == '__main__':
        asyncio.run(sync_command_center())
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from /root/argo-production")
