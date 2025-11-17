#!/bin/bash
# Setup Monitoring Script
# Configures monitoring and alerting for production

set -e

# Configuration
PRODUCTION_SERVER="${PRODUCTION_SERVER:-178.156.194.174}"
PRODUCTION_USER="${PRODUCTION_USER:-root}"
REGULAR_DIR="/root/argo-production"
PROP_FIRM_DIR="/root/argo-production-prop-firm"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Step 1: Create monitoring directories
print_step "STEP 1: CREATE MONITORING DIRECTORIES"

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

# Create log directories
mkdir -p ${REGULAR_DIR}/logs/monitoring
mkdir -p ${REGULAR_DIR}/logs/alerts
mkdir -p ${PROP_FIRM_DIR}/logs/monitoring
mkdir -p ${PROP_FIRM_DIR}/logs/alerts

# Create data directories
mkdir -p ${REGULAR_DIR}/data/metrics
mkdir -p ${PROP_FIRM_DIR}/data/metrics

echo "✅ Monitoring directories created"
ENDSSH

print_success "Directories created"

# Step 2: Create monitoring cron jobs
print_step "STEP 2: SETUP MONITORING CRON JOBS"

print_info "Setting up automated monitoring tasks..."

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

# Create cron job for Alpine sync verification (every hour)
(crontab -l 2>/dev/null | grep -v "verify_alpine_sync"; echo "0 * * * * cd ${REGULAR_DIR} && python3 scripts/verify_alpine_sync.py --hours 1 >> logs/monitoring/sync_verification.log 2>&1") | crontab -

# Create cron job for signal quality monitoring (every 6 hours)
(crontab -l 2>/dev/null | grep -v "monitor_signal_quality"; echo "0 */6 * * * cd ${REGULAR_DIR} && python3 scripts/monitor_signal_quality.py --hours 24 --json > logs/monitoring/quality_report.json 2>&1") | crontab -

# Create cron job for performance report (daily)
(crontab -l 2>/dev/null | grep -v "performance_report"; echo "0 0 * * * cd ${REGULAR_DIR} && python3 scripts/performance_report.py --hours 24 --json > logs/monitoring/performance_report.json 2>&1") | crontab -

# Create cron job for health check (every 15 minutes)
(crontab -l 2>/dev/null | grep -v "health_check"; echo "*/15 * * * * curl -s http://localhost:8000/api/v1/health/ > ${REGULAR_DIR}/logs/monitoring/health_check.json 2>&1") | crontab -

echo "✅ Cron jobs configured"
crontab -l | grep -E "(verify|monitor|performance|health)"
ENDSSH

print_success "Cron jobs configured"

# Step 3: Create monitoring script
print_step "STEP 3: CREATE MONITORING SCRIPT"

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << 'ENDSSH'
set -e

cat > /root/monitor_production.sh << 'SCRIPT'
#!/bin/bash
# Production Monitoring Script
# Runs all monitoring checks and generates report

REGULAR_DIR="/root/argo-production"
PROP_FIRM_DIR="/root/argo-production-prop-firm"
REPORT_FILE="${REGULAR_DIR}/logs/monitoring/daily_report_$(date +%Y%m%d).txt"

echo "=========================================="
echo "PRODUCTION MONITORING REPORT"
echo "Date: $(date)"
echo "=========================================="
echo ""

# Service status
echo "SERVICE STATUS:"
systemctl status argo-trading.service --no-pager -l | head -5
echo ""
systemctl status argo-trading-prop-firm.service --no-pager -l | head -5
echo ""

# Health check
echo "HEALTH CHECK:"
curl -s http://localhost:8000/api/v1/health/ | python3 -m json.tool 2>/dev/null || echo "Health check failed"
echo ""

# Alpine sync status
echo "ALPINE SYNC STATUS:"
cd ${REGULAR_DIR} && python3 scripts/verify_alpine_sync.py --hours 24 2>&1 | tail -10
echo ""

# Signal quality summary
echo "SIGNAL QUALITY SUMMARY:"
cd ${REGULAR_DIR} && python3 scripts/monitor_signal_quality.py --hours 24 2>&1 | grep -E "(Total|Average|High|Medium|Low)" | head -10
echo ""

# Recent errors
echo "RECENT ERRORS (last 100 lines):"
journalctl -u argo-trading.service --since '24 hours ago' --no-pager | grep -i "error\|exception" | tail -10
echo ""

echo "=========================================="
echo "Report saved to: ${REPORT_FILE}"
echo "=========================================="

) | tee ${REPORT_FILE}
SCRIPT

chmod +x /root/monitor_production.sh
echo "✅ Monitoring script created"
ENDSSH

print_success "Monitoring script created"

# Step 4: Setup log rotation
print_step "STEP 4: SETUP LOG ROTATION"

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

cat > /etc/logrotate.d/argo-production << 'LOGROTATE'
${REGULAR_DIR}/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
    sharedscripts
    postrotate
        systemctl reload argo-trading.service > /dev/null 2>&1 || true
    endscript
}

${PROP_FIRM_DIR}/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
    sharedscripts
    postrotate
        systemctl reload argo-trading-prop-firm.service > /dev/null 2>&1 || true
    endscript
}
LOGROTATE

echo "✅ Log rotation configured"
ENDSSH

print_success "Log rotation configured"

# Step 5: Test monitoring
print_step "STEP 5: TEST MONITORING"

print_info "Running test monitoring checks..."

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

echo "Testing health check..."
curl -s http://localhost:8000/api/v1/health/simple && echo " ✅" || echo " ❌"

echo "Testing Alpine sync verification..."
cd ${REGULAR_DIR} && python3 scripts/verify_alpine_sync.py --hours 1 > /dev/null 2>&1 && echo "Alpine sync check: ✅" || echo "Alpine sync check: ⚠️  (may need time)"

echo "Testing signal quality monitoring..."
cd ${REGULAR_DIR} && python3 scripts/monitor_signal_quality.py --hours 1 --json > /dev/null 2>&1 && echo "Signal quality check: ✅" || echo "Signal quality check: ⚠️  (may need time)"

echo "✅ Monitoring tests complete"
ENDSSH

print_success "Monitoring setup complete"

# Final summary
print_step "MONITORING SETUP COMPLETE"

print_success "🎉 Monitoring has been configured!"
echo ""
print_info "Monitoring Features:"
echo "  ✅ Automated Alpine sync verification (hourly)"
echo "  ✅ Signal quality monitoring (every 6 hours)"
echo "  ✅ Performance reporting (daily)"
echo "  ✅ Health checks (every 15 minutes)"
echo "  ✅ Log rotation (daily, 30 day retention)"
echo "  ✅ Daily monitoring report script"
echo ""
print_info "Manual Monitoring:"
echo "  Run daily report: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} '/root/monitor_production.sh'"
echo "  View logs: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'tail -f ${REGULAR_DIR}/logs/monitoring/*.log'"
echo ""
