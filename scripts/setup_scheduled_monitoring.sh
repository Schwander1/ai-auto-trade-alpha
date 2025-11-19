#!/bin/bash
# Setup script for scheduled SHORT position monitoring
# This script helps configure cron jobs for automated monitoring

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CRON_FILE="$PROJECT_DIR/crontab_short_monitoring.txt"

echo "=========================================="
echo "SHORT Position Monitoring Setup"
echo "=========================================="
echo ""

# Check if scripts exist
if [ ! -f "$SCRIPT_DIR/scheduled_monitor_short.sh" ]; then
    echo "❌ Error: scheduled_monitor_short.sh not found"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/monitor_short_positions.py" ]; then
    echo "❌ Error: monitor_short_positions.py not found"
    exit 1
fi

# Make scripts executable
chmod +x "$SCRIPT_DIR/scheduled_monitor_short.sh"
chmod +x "$SCRIPT_DIR/monitor_short_positions.py"
chmod +x "$SCRIPT_DIR/alert_short_position_issues.py"
chmod +x "$SCRIPT_DIR/short_position_performance_tracker.py"

echo "✅ Scripts are executable"
echo ""

# Create log directory
mkdir -p "$PROJECT_DIR/logs"
echo "✅ Log directory created: $PROJECT_DIR/logs"
echo ""

# Generate crontab entries
cat > "$CRON_FILE" << EOF
# SHORT Position Monitoring - Auto-generated crontab entries
# Add these to your crontab with: crontab -e
# Or install with: crontab $CRON_FILE

# Monitor SHORT positions every 5 minutes
*/5 * * * * cd $PROJECT_DIR && $SCRIPT_DIR/scheduled_monitor_short.sh >> $PROJECT_DIR/logs/cron_short_monitor.log 2>&1

# Performance report daily at 9:00 AM
0 9 * * * cd $PROJECT_DIR && python3 $SCRIPT_DIR/short_position_performance_tracker.py --output $PROJECT_DIR/logs/performance_\$(date +\%Y\%m\%d).json >> $PROJECT_DIR/logs/cron_performance.log 2>&1

# Alert check every hour
0 * * * * cd $PROJECT_DIR && python3 $SCRIPT_DIR/alert_short_position_issues.py --output $PROJECT_DIR/logs/alerts_\$(date +\%Y\%m\%d_\%H\%M\%S).json >> $PROJECT_DIR/logs/cron_alerts.log 2>&1

# Comprehensive verification daily at 8:00 AM
0 8 * * * cd $PROJECT_DIR && python3 $SCRIPT_DIR/verify_short_positions.py >> $PROJECT_DIR/logs/cron_verification.log 2>&1

# Clean up old logs (keep 30 days) - runs daily at 2:00 AM
0 2 * * * find $PROJECT_DIR/logs -name "*.log" -mtime +30 -delete && find $PROJECT_DIR/logs -name "*.json" -mtime +30 -delete
EOF

echo "✅ Crontab file created: $CRON_FILE"
echo ""
echo "=========================================="
echo "Installation Options:"
echo "=========================================="
echo ""
echo "Option 1: Install to your crontab"
echo "  crontab $CRON_FILE"
echo ""
echo "Option 2: Add to existing crontab"
echo "  crontab -l > /tmp/current_crontab"
echo "  cat $CRON_FILE >> /tmp/current_crontab"
echo "  crontab /tmp/current_crontab"
echo ""
echo "Option 3: Review and edit manually"
echo "  cat $CRON_FILE"
echo "  crontab -e"
echo ""
echo "=========================================="
echo "Verification:"
echo "=========================================="
echo ""
echo "View current crontab:"
echo "  crontab -l"
echo ""
echo "Test monitoring script:"
echo "  $SCRIPT_DIR/scheduled_monitor_short.sh"
echo ""
echo "View logs:"
echo "  tail -f $PROJECT_DIR/logs/short_position_monitor_*.log"
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="

