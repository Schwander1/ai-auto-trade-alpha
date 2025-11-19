#!/bin/bash
# Scheduled monitoring script for SHORT positions
# Can be run via cron or systemd timer

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/short_position_monitor_$(date +%Y%m%d).log"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Run monitoring check
echo "==========================================" >> "$LOG_FILE"
echo "SHORT Position Monitor - $(date)" >> "$LOG_FILE"
echo "==========================================" >> "$LOG_FILE"
python3 "$SCRIPT_DIR/monitor_short_positions.py" >> "$LOG_FILE" 2>&1

# Run alerting check
echo "" >> "$LOG_FILE"
echo "==========================================" >> "$LOG_FILE"
echo "SHORT Position Alerts - $(date)" >> "$LOG_FILE"
echo "==========================================" >> "$LOG_FILE"
python3 "$SCRIPT_DIR/alert_short_position_issues.py" --output "$LOG_DIR/alerts_$(date +%Y%m%d_%H%M%S).json" >> "$LOG_FILE" 2>&1

# Keep only last 7 days of logs
find "$LOG_DIR" -name "short_position_monitor_*.log" -mtime +7 -delete
find "$LOG_DIR" -name "alerts_*.json" -mtime +7 -delete

echo "Monitoring complete - $(date)" >> "$LOG_FILE"

