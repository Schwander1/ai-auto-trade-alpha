#!/bin/bash
# Setup cron jobs for Argo Capital compliance automation

ARGO_PATH="${ARGO_PATH:-/root/argo-production/argo}"

echo "🔧 Setting up cron jobs for Argo Capital..."

# Create cron entries
(crontab -l 2>/dev/null | grep -v "argo-compliance"; cat <<CRON
# Argo Capital Compliance Automation
# Daily backup at 2 AM UTC
0 2 * * * cd $ARGO_PATH && /usr/bin/python3 compliance/daily_backup.py >> logs/daily_backup.log 2>&1

# Hourly integrity check (sample 1000 signals)
0 * * * * cd $ARGO_PATH && /usr/bin/python3 compliance/integrity_monitor.py 1000 >> logs/integrity_checks.log 2>&1

# Daily full integrity check at 3 AM UTC
0 3 * * * cd $ARGO_PATH && /usr/bin/python3 compliance/integrity_monitor.py full >> logs/integrity_checks.log 2>&1

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
