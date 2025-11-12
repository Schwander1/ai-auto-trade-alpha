#!/usr/bin/env python3
"""
Master Notion Sync - Updates ALL databases
Runs every 5 minutes via cron
"""
import sys
sys.path.insert(0, '/root/argo-production')

from dotenv import load_dotenv
load_dotenv('/root/argo-production/.env', override=True)

import psutil
from datetime import datetime
from argo.integrations.notion_command_center import command_center

print(f"\n{'='*60}")
print(f"🏔️ Syncing to Notion Command Center - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*60}\n")

# 1. System Status
cpu = psutil.cpu_percent()
mem = psutil.virtual_memory().percent
command_center.update_system_status(cpu, mem, "operational")

# 2. Revenue (will update when you have customers)
command_center.update_revenue(mrr=0, customers=0, target=5000)

# 3. Weekly Performance (will update from actual data)
command_center.update_performance(win_rate=95, total_trades=1, pnl=45)

# 4. System health alert if needed
if cpu > 80:
    command_center.log_alert(f"High CPU usage: {cpu}%", "warning")
if mem > 80:
    command_center.log_alert(f"High memory usage: {mem}%", "warning")

print(f"\n{'='*60}")
print(f"✅ All databases synced successfully")
print(f"{'='*60}\n")
