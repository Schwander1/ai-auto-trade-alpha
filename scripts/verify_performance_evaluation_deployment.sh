#!/bin/bash
# Verify Performance Evaluation System Deployment on Production

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

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check scripts
print_step "VERIFYING SCRIPTS"

REQUIRED_SCRIPTS=(
    "evaluate_performance.py"
    "evaluate_performance_enhanced.py"
    "performance_optimizer.py"
    "performance_trend_analyzer.py"
    "performance_comparator.py"
    "performance_alert.py"
    "auto_optimize.py"
    "performance_summary.py"
    "performance_exporter.py"
    "setup_performance_monitoring.sh"
)

MISSING=0
for script in "${REQUIRED_SCRIPTS[@]}"; do
    RESULT=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "test -f ${REGULAR_DIR}/scripts/${script} && echo 'EXISTS' || echo 'MISSING'" 2>/dev/null || echo "ERROR")
    if [ "$RESULT" = "EXISTS" ]; then
        print_success "${script}"
    else
        print_error "${script} - NOT FOUND"
        MISSING=$((MISSING + 1))
    fi
done

# Check executability
print_step "VERIFYING EXECUTABILITY"

for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [[ "$script" == *.py ]] || [[ "$script" == *.sh ]]; then
        RESULT=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "test -x ${REGULAR_DIR}/scripts/${script} && echo 'EXECUTABLE' || echo 'NOT_EXECUTABLE'" 2>/dev/null || echo "ERROR")
        if [ "$RESULT" = "EXECUTABLE" ]; then
            print_success "${script} is executable"
        else
            print_error "${script} is not executable"
        fi
    fi
done

# Check directories
print_step "VERIFYING DIRECTORIES"

DIRS=(
    "${REGULAR_DIR}/reports"
    "${REGULAR_DIR}/logs/monitoring"
    "${PROP_FIRM_DIR}/reports"
    "${PROP_FIRM_DIR}/logs/monitoring"
)

for dir in "${DIRS[@]}"; do
    RESULT=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "test -d ${dir} && echo 'EXISTS' || echo 'MISSING'" 2>/dev/null || echo "ERROR")
    if [ "$RESULT" = "EXISTS" ]; then
        print_success "${dir}"
    else
        print_error "${dir} - NOT FOUND"
    fi
done

# Check cron jobs
print_step "VERIFYING CRON JOBS"

CRON_JOBS=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "crontab -l 2>/dev/null | grep -E '(performance_evaluation|performance_trend|performance_optimizer|performance_alert)' || echo 'NONE'" 2>/dev/null)

if [ "$CRON_JOBS" != "NONE" ] && [ -n "$CRON_JOBS" ]; then
    print_success "Cron jobs configured:"
    echo "$CRON_JOBS" | while read line; do
        echo "  $line"
    done
else
    print_error "No performance evaluation cron jobs found"
fi

# Test scripts
print_step "TESTING SCRIPTS"

print_info "Testing performance_summary.py..."
SUMMARY_TEST=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "cd ${REGULAR_DIR} && python3 scripts/performance_summary.py 2>&1" 2>/dev/null || echo "ERROR")
if [ "$SUMMARY_TEST" != "ERROR" ]; then
    print_success "performance_summary.py works"
    echo "$SUMMARY_TEST" | head -10
else
    print_error "performance_summary.py failed"
fi

print_info "Testing performance_alert.py..."
ALERT_TEST=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "cd ${REGULAR_DIR} && python3 scripts/performance_alert.py --check 2>&1" 2>/dev/null || echo "ERROR")
if [ "$ALERT_TEST" != "ERROR" ]; then
    print_success "performance_alert.py works"
    echo "$ALERT_TEST" | head -5
else
    print_error "performance_alert.py failed"
fi

# Final summary
print_step "VERIFICATION SUMMARY"

if [ $MISSING -eq 0 ]; then
    print_success "All scripts deployed successfully!"
    print_info ""
    print_info "Next steps:"
    print_info "  1. Wait for first scheduled evaluation (9 AM daily)"
    print_info "  2. Check reports: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'ls -lh ${REGULAR_DIR}/reports/'"
    print_info "  3. View alerts: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'tail -f ${REGULAR_DIR}/logs/monitoring/alerts.log'"
    print_info "  4. Run manual test: ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} 'cd ${REGULAR_DIR} && python3 scripts/evaluate_performance_enhanced.py --days 1'"
else
    print_error "${MISSING} script(s) missing. Please check deployment."
    exit 1
fi
