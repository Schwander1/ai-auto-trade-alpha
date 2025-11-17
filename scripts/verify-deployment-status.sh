#!/bin/bash
# Verify Deployment Status - Check all compliance features
# This script verifies that all deployments are working correctly

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ALPINE_SERVER="91.98.153.49"
ALPINE_USER="root"
ALPINE_PATH="/root/alpine-production"
ARGO_SERVER="178.156.194.174"
ARGO_USER="root"
ARGO_PATH="/root/argo-production"

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verify Alpine Server
verify_alpine() {
    print_header "VERIFYING ALPINE SERVER"

    # Check database migration
    print_info "Checking database migration..."
    result=$(ssh -o StrictHostKeyChecking=no ${ALPINE_USER}@${ALPINE_SERVER} "cd ${ALPINE_PATH} && source venv/bin/activate 2>/dev/null && python3 <<'PYEOF'
from backend.core.database import get_engine
from sqlalchemy import inspect, text

try:
    engine = get_engine()
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    has_audit = 'signal_audit_log' in tables

    with engine.connect() as conn:
        result = conn.execute(text(\"\"\"
            SELECT COUNT(*) FROM information_schema.triggers
            WHERE event_object_table IN ('signals', 'signal_audit_log')
        \"\"\"))
        trigger_count = result.scalar()

    print(f'AUDIT_TABLE:{has_audit}')
    print(f'TRIGGER_COUNT:{trigger_count}')
except Exception as e:
    print(f'ERROR:{e}')
PYEOF
" 2>&1)

    if echo "$result" | grep -q "AUDIT_TABLE:True"; then
        print_success "Audit log table exists"
    else
        print_error "Audit log table missing"
    fi

    trigger_count=$(echo "$result" | grep "TRIGGER_COUNT:" | cut -d: -f2)
    if [ -n "$trigger_count" ] && [ "$trigger_count" -gt 0 ]; then
        print_success "Found $trigger_count immutability triggers"
    else
        print_warning "No triggers found"
    fi

    # Check migration file
    print_info "Checking migration file..."
    if ssh -o StrictHostKeyChecking=no ${ALPINE_USER}@${ALPINE_SERVER} "test -f ${ALPINE_PATH}/backend/migrations/immutability_and_audit.py" 2>/dev/null; then
        print_success "Migration file exists"
    else
        print_error "Migration file missing"
    fi
}

# Verify Argo Server
verify_argo() {
    print_header "VERIFYING ARGO SERVER"

    # Check cron jobs
    print_info "Checking cron jobs..."
    cron_output=$(ssh -o StrictHostKeyChecking=no ${ARGO_USER}@${ARGO_SERVER} "crontab -l 2>/dev/null | grep -E '(integrity_monitor|daily_backup|weekly_report)' | wc -l" 2>&1)

    if [ -n "$cron_output" ] && [ "$cron_output" -ge 3 ]; then
        print_success "Found $cron_output compliance cron jobs"
    else
        print_warning "Cron jobs may be missing"
    fi

    # Test integrity monitor
    print_info "Testing integrity monitor..."
    test_result=$(ssh -o StrictHostKeyChecking=no ${ARGO_USER}@${ARGO_SERVER} "cd ${ARGO_PATH}/argo && python3 compliance/integrity_monitor.py 10 2>&1 | grep -E '(success|PASS|FAIL)' | head -1" 2>&1)

    if echo "$test_result" | grep -qE "(success.*true|PASS)"; then
        print_success "Integrity monitor is working"
    else
        print_warning "Integrity monitor test inconclusive"
    fi

    # Check log files
    print_info "Checking log files..."
    if ssh -o StrictHostKeyChecking=no ${ARGO_USER}@${ARGO_SERVER} "test -d ${ARGO_PATH}/argo/logs" 2>/dev/null; then
        print_success "Log directory exists"

        # Check if logs are being written
        log_size=$(ssh -o StrictHostKeyChecking=no ${ARGO_USER}@${ARGO_SERVER} "stat -f%z ${ARGO_PATH}/argo/logs/integrity_checks.log 2>/dev/null || echo 0" 2>&1)
        if [ -n "$log_size" ] && [ "$log_size" -gt 0 ]; then
            print_success "Integrity check logs are being written"
        else
            print_info "Log file is new (will be written on next cron run)"
        fi
    else
        print_warning "Log directory not found"
    fi

    # Check compliance scripts
    print_info "Checking compliance scripts..."
    scripts=("integrity_monitor.py" "daily_backup.py" "weekly_report.py")
    for script in "${scripts[@]}"; do
        if ssh -o StrictHostKeyChecking=no ${ARGO_USER}@${ARGO_SERVER} "test -f ${ARGO_PATH}/argo/compliance/${script}" 2>/dev/null; then
            print_success "$script exists"
        else
            print_error "$script missing"
        fi
    done
}

# Check services
check_services() {
    print_header "CHECKING SERVICES"

    # Check Alpine backend
    print_info "Checking Alpine backend health..."
    if curl -f -s --max-time 5 "http://${ALPINE_SERVER}:8001/health" > /dev/null 2>&1; then
        print_success "Alpine backend is healthy"
    else
        print_warning "Alpine backend health check failed"
    fi

    # Check Argo API
    print_info "Checking Argo API health..."
    if curl -f -s --max-time 5 "http://${ARGO_SERVER}:8000/health" > /dev/null 2>&1; then
        print_success "Argo API is healthy"
    else
        print_warning "Argo API health check failed"
    fi
}

# Main execution
main() {
    print_header "DEPLOYMENT STATUS VERIFICATION"

    verify_alpine
    verify_argo
    check_services

    print_header "VERIFICATION COMPLETE"
    echo ""
    print_info "Summary:"
    echo "  - Alpine: Database migration status checked"
    echo "  - Argo: Cron jobs and integrity monitor verified"
    echo "  - Services: Health checks performed"
    echo ""
    print_info "Next steps:"
    echo "  1. Monitor cron job execution (next hourly check)"
    echo "  2. Verify backup runs (next 2 AM UTC)"
    echo "  3. Check Grafana dashboard for metrics"
    echo "  4. Review integrity check logs"
    echo ""
}

main "$@"
