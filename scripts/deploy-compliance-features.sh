#!/bin/bash
# Comprehensive Compliance Features Deployment Script
# Deploys all compliance, security, and auditability features

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ALPINE_SERVER="${ALPINE_SERVER:-91.98.153.49}"
ARGO_SERVER="${ARGO_SERVER:-178.156.194.174}"
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

# Check if running on correct server
check_server() {
    local expected_server=$1
    local current_host=$(hostname -I | awk '{print $1}')
    
    if [ "$expected_server" != "$current_host" ] && [ "$expected_server" != "localhost" ]; then
        print_warning "This script should be run on $expected_server"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Step 1: Database Migration
deploy_migration() {
    print_step "1️⃣  Deploying Database Migration (Immutability & Audit)"
    
    if [ -f "$ALPINE_PATH/backend/migrations/immutability_and_audit.py" ]; then
        cd "$ALPINE_PATH"
        source venv/bin/activate 2>/dev/null || true
        
        print_step "Running migration..."
        python -m backend.migrations.immutability_and_audit upgrade || {
            print_error "Migration failed!"
            return 1
        }
        
        print_success "Migration completed successfully"
    else
        print_error "Migration file not found: $ALPINE_PATH/backend/migrations/immutability_and_audit.py"
        return 1
    fi
}

# Step 2: Setup Cron Jobs
setup_cron_jobs() {
    print_step "2️⃣  Setting up Compliance Cron Jobs"
    
    # Argo server cron jobs
    if [ -d "$ARGO_PATH/argo/compliance" ]; then
        cd "$ARGO_PATH"
        
        # Remove old compliance cron jobs
        crontab -l 2>/dev/null | grep -v "argo-compliance" | crontab - 2>/dev/null || true
        
        # Add new cron jobs
        (crontab -l 2>/dev/null; cat <<CRON
# Argo Capital Compliance Automation
# Daily backup at 2 AM UTC
0 2 * * * cd $ARGO_PATH/argo && /usr/bin/python3 compliance/daily_backup.py >> logs/daily_backup.log 2>&1

# Hourly integrity check (sample 1000 signals)
0 * * * * cd $ARGO_PATH/argo && /usr/bin/python3 compliance/integrity_monitor.py 1000 >> logs/integrity_checks.log 2>&1

# Daily full integrity check at 3 AM UTC
0 3 * * * cd $ARGO_PATH/argo && /usr/bin/python3 compliance/integrity_monitor.py full >> logs/integrity_checks.log 2>&1

# Weekly report every Sunday at 6 AM UTC
0 6 * * 0 cd $ARGO_PATH/argo && /usr/bin/python3 compliance/weekly_report.py >> logs/weekly_report.log 2>&1
CRON
        ) | crontab -
        
        print_success "Cron jobs installed on Argo server"
        echo "   Installed jobs:"
        crontab -l | grep -A 5 "argo-compliance" | sed 's/^/   /'
    else
        print_warning "Argo compliance directory not found, skipping cron setup"
    fi
}

# Step 3: Setup S3 Versioning
setup_s3_versioning() {
    print_step "3️⃣  Setting up S3 Versioning and Lifecycle Policies"
    
    if [ -f "scripts/enable-s3-versioning.py" ]; then
        python3 scripts/enable-s3-versioning.py || {
            print_warning "S3 versioning setup failed (may need AWS credentials)"
            return 0  # Non-critical
        }
        print_success "S3 versioning configured"
    else
        print_warning "S3 versioning script not found, skipping"
    fi
}

# Step 4: Verify Services
verify_services() {
    print_step "4️⃣  Verifying Services"
    
    # Check Alpine backend
    if curl -f -s "http://localhost:8001/health" > /dev/null 2>&1; then
        print_success "Alpine backend is healthy"
    else
        print_warning "Alpine backend health check failed"
    fi
    
    # Check Argo API
    if curl -f -s "http://$ARGO_SERVER:8000/health" > /dev/null 2>&1; then
        print_success "Argo API is healthy"
    else
        print_warning "Argo API health check failed"
    fi
    
    # Check Prometheus
    if curl -f -s "http://localhost:9090/-/healthy" > /dev/null 2>&1; then
        print_success "Prometheus is healthy"
    else
        print_warning "Prometheus health check failed"
    fi
}

# Step 5: Run Initial Integrity Check
run_initial_integrity_check() {
    print_step "5️⃣  Running Initial Integrity Check"
    
    if [ -f "$ARGO_PATH/argo/compliance/integrity_monitor.py" ]; then
        cd "$ARGO_PATH/argo"
        python3 compliance/integrity_monitor.py 1000 > /tmp/integrity_check_result.json 2>&1
        
        if [ $? -eq 0 ]; then
            print_success "Initial integrity check passed"
            echo "   Results:"
            cat /tmp/integrity_check_result.json | head -20 | sed 's/^/   /'
        else
            print_error "Initial integrity check failed!"
            cat /tmp/integrity_check_result.json | tail -20
            return 1
        fi
    else
        print_warning "Integrity monitor not found, skipping"
    fi
}

# Step 6: Test Backup
test_backup() {
    print_step "6️⃣  Testing Backup System"
    
    if [ -f "$ARGO_PATH/argo/compliance/daily_backup.py" ]; then
        cd "$ARGO_PATH/argo"
        python3 compliance/daily_backup.py || {
            print_warning "Backup test failed (may need AWS credentials)"
            return 0  # Non-critical
        }
        print_success "Backup test completed"
    else
        print_warning "Backup script not found, skipping"
    fi
}

# Step 7: Verify Immutability
verify_immutability() {
    print_step "7️⃣  Verifying Signal Immutability"
    
    if [ -f "$ALPINE_PATH/backend/migrations/immutability_and_audit.py" ]; then
        cd "$ALPINE_PATH"
        source venv/bin/activate 2>/dev/null || true
        
        # Try to update a signal (should fail)
        python3 <<EOF
from backend.core.database import get_db
from backend.models.signal import Signal
from sqlalchemy import text

db = next(get_db())
try:
    # Try to update a signal
    result = db.execute(text("UPDATE signals SET entry_price = 999.99 WHERE signal_id = (SELECT signal_id FROM signals LIMIT 1)"))
    db.commit()
    print("❌ ERROR: Signal update succeeded (should have failed!)")
    exit(1)
except Exception as e:
    if "immutable" in str(e).lower() or "permission denied" in str(e).lower():
        print("✅ Signal immutability verified (update blocked)")
    else:
        print(f"⚠️  Unexpected error: {e}")
        exit(1)
EOF
        
        if [ $? -eq 0 ]; then
            print_success "Immutability verified"
        else
            print_error "Immutability verification failed"
            return 1
        fi
    else
        print_warning "Cannot verify immutability (migration file not found)"
    fi
}

# Step 8: Check Prometheus Metrics
check_metrics() {
    print_step "8️⃣  Checking Prometheus Metrics"
    
    METRICS_URL="http://localhost:9090/api/v1/query?query="
    
    # Check if metrics are available
    metrics=(
        "signal_generation_latency_seconds"
        "signal_delivery_latency_seconds"
        "integrity_failed_verifications_total"
    )
    
    for metric in "${metrics[@]}"; do
        if curl -f -s "${METRICS_URL}${metric}" > /dev/null 2>&1; then
            print_success "Metric available: $metric"
        else
            print_warning "Metric not found: $metric"
        fi
    done
}

# Main execution
main() {
    echo "=========================================="
    echo "  Compliance Features Deployment"
    echo "=========================================="
    echo ""
    echo "Alpine Server: $ALPINE_SERVER"
    echo "Argo Server: $ARGO_SERVER"
    echo "Alpine Path: $ALPINE_PATH"
    echo "Argo Path: $ARGO_PATH"
    echo ""
    
    read -p "Continue with deployment? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
    
    # Run deployment steps
    deploy_migration || print_error "Migration step failed"
    setup_cron_jobs || print_error "Cron setup failed"
    setup_s3_versioning || print_warning "S3 setup failed (non-critical)"
    verify_services
    run_initial_integrity_check || print_warning "Integrity check failed"
    test_backup || print_warning "Backup test failed (non-critical)"
    verify_immutability || print_error "Immutability verification failed"
    check_metrics
    
    echo ""
    echo "=========================================="
    print_success "Deployment Complete!"
    echo "=========================================="
    echo ""
    echo "Next Steps:"
    echo "1. Import Grafana dashboard: infrastructure/monitoring/grafana-dashboards/compliance-dashboard.json"
    echo "2. Configure alerting channels (PagerDuty, Slack, Email)"
    echo "3. Review logs: $ARGO_PATH/argo/logs/"
    echo "4. Monitor metrics in Grafana"
    echo ""
}

# Run main function
main "$@"

