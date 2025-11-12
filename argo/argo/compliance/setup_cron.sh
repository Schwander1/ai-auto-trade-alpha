#!/bin/bash
# Setup cron jobs for Argo Capital compliance automation

ARGO_PATH="/root/argo-production/argo"

echo "🔧 Setting up cron jobs for Argo Capital..."

# Create cron entries
(crontab -l 2>/dev/null | grep -v "argo-compliance"; cat <<CRON
# Argo Capital Compliance Automation
# Daily backup at midnight UTC
0 0 * * * cd $ARGO_PATH && /usr/bin/python3 compliance/daily_backup.py >> logs/daily_backup.log 2>&1

# Weekly report every Sunday at 6 AM UTC
0 6 * * 0 cd $ARGO_PATH && /usr/bin/python3 compliance/weekly_report.py >> logs/weekly_report.log 2>&1

# Health check every hour
0 * * * * cd $ARGO_PATH && /usr/bin/python3 compliance/health_check.py >> logs/health.log 2>&1
CRON
) | crontab -

echo "✅ Cron jobs installed"
echo ""
echo "Installed jobs:"
crontab -l | grep -A 10 "Argo Capital"
