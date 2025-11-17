#!/bin/bash
# Compliance Deployment Verification Script
# Verifies that all compliance features are properly deployed and working

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ALPINE_PATH="${ALPINE_PATH:-/root/alpine-production}"
ARGO_PATH="${ARGO_PATH:-/root/argo-production}"

print_step() {
    echo -e "\n${BLUE}▶ $1${NC}"
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

# Check database triggers
check_immutability_triggers() {
    print_step "Checking Database Immutability Triggers"
    
    if [ -d "$ALPINE_PATH" ]; then
        cd "$ALPINE_PATH"
        source venv/bin/activate 2>/dev/null || true
        
        python3 <<EOF
from backend.core.database import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    # Check for immutability trigger
    result = conn.execute(text("""
        SELECT tgname, tgenabled 
        FROM pg_trigger 
        WHERE tgname LIKE '%signal%immutable%' OR tgname LIKE '%signal%audit%'
    """))
    triggers = result.fetchall()
    
    if triggers:
        print("✅ Found immutability triggers:")
        for trigger in triggers:
            print(f"   - {trigger[0]}")
    else:
        print("❌ No immutability triggers found!")
        exit(1)
EOF
        
        if [ $? -eq 0 ]; then
            print_success "Immutability triggers verified"
        else
            print_error "Immutability triggers not found"
            return 1
        fi
    else
        print_warning "Alpine path not found, skipping trigger check"
    fi
}

# Check audit log table
check_audit_log_table() {
    print_step "Checking Audit Log Table"
    
    if [ -d "$ALPINE_PATH" ]; then
        cd "$ALPINE_PATH"
        source venv/bin/activate 2>/dev/null || true
        
        python3 <<EOF
from backend.core.database import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    # Check if audit log table exists
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name = 'signal_audit_log'
    """))
    
    if result.fetchone():
        # Check row count
        count_result = conn.execute(text("SELECT COUNT(*) FROM signal_audit_log"))
        count = count_result.scalar()
        print(f"✅ Audit log table exists with {count} entries")
    else:
        print("❌ Audit log table not found!")
        exit(1)
EOF
        
        if [ $? -eq 0 ]; then
            print_success "Audit log table verified"
        else
            print_error "Audit log table not found"
            return 1
        fi
    else
        print_warning "Alpine path not found, skipping audit log check"
    fi
}

# Check cron jobs
check_cron_jobs() {
    print_step "Checking Cron Jobs"
    
    cron_output=$(crontab -l 2>/dev/null | grep -E "(daily_backup|integrity_monitor|weekly_report)" || true)
    
    if [ -n "$cron_output" ]; then
        print_success "Cron jobs found:"
        echo "$cron_output" | sed 's/^/   /'
    else
        print_error "No compliance cron jobs found!"
        return 1
    fi
}

# Check integrity monitor script
check_integrity_monitor() {
    print_step "Checking Integrity Monitor"
    
    if [ -f "$ARGO_PATH/argo/compliance/integrity_monitor.py" ]; then
        # Test run with small sample
        cd "$ARGO_PATH/argo"
        python3 compliance/integrity_monitor.py 10 > /tmp/integrity_test.json 2>&1
        
        if [ $? -eq 0 ]; then
            print_success "Integrity monitor is working"
            echo "   Test results:"
            cat /tmp/integrity_test.json | grep -E "(success|checked|failed)" | head -5 | sed 's/^/   /'
        else
            print_error "Integrity monitor test failed"
            cat /tmp/integrity_test.json | tail -10
            return 1
        fi
    else
        print_error "Integrity monitor script not found: $ARGO_PATH/argo/compliance/integrity_monitor.py"
        return 1
    fi
}

# Check backup script
check_backup_script() {
    print_step "Checking Backup Script"
    
    if [ -f "$ARGO_PATH/argo/compliance/daily_backup.py" ]; then
        # Check if script is executable and has required imports
        python3 -c "import sys; sys.path.insert(0, '$ARGO_PATH/argo'); import compliance.daily_backup" 2>&1
        
        if [ $? -eq 0 ]; then
            print_success "Backup script is valid"
        else
            print_warning "Backup script has import issues (may need dependencies)"
        fi
    else
        print_error "Backup script not found: $ARGO_PATH/argo/compliance/daily_backup.py"
        return 1
    fi
}

# Check Prometheus metrics
check_prometheus_metrics() {
    print_step "Checking Prometheus Metrics"
    
    METRICS_URL="http://localhost:9090/api/v1/query?query="
    
    metrics=(
        "signal_generation_latency_seconds"
        "signal_delivery_latency_seconds"
        "integrity_failed_verifications_total"
        "backup_duration_seconds"
        "last_backup_timestamp"
    )
    
    available=0
    missing=0
    
    for metric in "${metrics[@]}"; do
        response=$(curl -s "${METRICS_URL}${metric}")
        if echo "$response" | grep -q "result"; then
            print_success "Metric available: $metric"
            ((available++))
        else
            print_warning "Metric not found: $metric"
            ((missing++))
        fi
    done
    
    echo ""
    echo "   Metrics: $available available, $missing missing"
    
    if [ $missing -gt 2 ]; then
        print_warning "Many metrics are missing - check Prometheus configuration"
    fi
}

# Check Grafana dashboard
check_grafana_dashboard() {
    print_step "Checking Grafana Dashboard"
    
    if [ -f "infrastructure/monitoring/grafana-dashboards/compliance-dashboard.json" ]; then
        print_success "Dashboard file exists"
        echo "   Location: infrastructure/monitoring/grafana-dashboards/compliance-dashboard.json"
        echo "   Note: Import manually in Grafana UI"
    else
        print_error "Dashboard file not found"
        return 1
    fi
}

# Check alerting configuration
check_alerting() {
    print_step "Checking Alerting Configuration"
    
    if [ -f "$ARGO_PATH/argo/core/alerting.py" ]; then
        # Check environment variables
        env_vars=(
            "PAGERDUTY_ENABLED"
            "SLACK_ENABLED"
            "EMAIL_ALERTS_ENABLED"
        )
        
        configured=0
        for var in "${env_vars[@]}"; do
            if [ -n "${!var}" ]; then
                echo "   ✅ $var is set"
                ((configured++))
            else
                echo "   ⚠️  $var is not set"
            fi
        done
        
        if [ $configured -gt 0 ]; then
            print_success "Alerting is configured ($configured channels)"
        else
            print_warning "No alerting channels configured"
        fi
    else
        print_error "Alerting module not found"
        return 1
    fi
}

# Check signal model fields
check_signal_model() {
    print_step "Checking Signal Model Fields"
    
    if [ -d "$ALPINE_PATH" ]; then
        cd "$ALPINE_PATH"
        source venv/bin/activate 2>/dev/null || true
        
        python3 <<EOF
from backend.models.signal import Signal
from sqlalchemy import inspect

engine = Signal.__table__.bind
inspector = inspect(engine)
columns = [col['name'] for col in inspector.get_columns('signals')]

required_fields = [
    'retention_expires_at',
    'previous_hash',
    'chain_index',
    'generation_latency_ms',
    'delivery_latency_ms',
    'server_timestamp',
    'rationale'
]

missing = []
for field in required_fields:
    if field not in columns:
        missing.append(field)

if missing:
    print(f"❌ Missing fields: {', '.join(missing)}")
    exit(1)
else:
    print("✅ All required fields present")
EOF
        
        if [ $? -eq 0 ]; then
            print_success "Signal model fields verified"
        else
            print_error "Signal model missing required fields"
            return 1
        fi
    else
        print_warning "Alpine path not found, skipping model check"
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "  Compliance Deployment Verification"
    echo "=========================================="
    echo ""
    
    local errors=0
    
    check_immutability_triggers || ((errors++))
    check_audit_log_table || ((errors++))
    check_cron_jobs || ((errors++))
    check_integrity_monitor || ((errors++))
    check_backup_script || ((errors++))
    check_prometheus_metrics
    check_grafana_dashboard || ((errors++))
    check_alerting
    check_signal_model || ((errors++))
    
    echo ""
    echo "=========================================="
    if [ $errors -eq 0 ]; then
        print_success "All checks passed!"
    else
        print_error "$errors check(s) failed"
        exit 1
    fi
    echo "=========================================="
}

main "$@"

