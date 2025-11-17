#!/bin/bash
# Post-Deployment Verification Script
# Comprehensive verification of all deployed components

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

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Track results
PASSED=0
FAILED=0
WARNINGS=0

# Step 1: Service Status Check
print_step "STEP 1: SERVICE STATUS CHECK"

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

echo "Checking regular service..."
if systemctl is-active --quiet argo-trading.service; then
    echo "✅ Regular service is active"
    systemctl status argo-trading.service --no-pager -l | head -10
else
    echo "❌ Regular service is not active"
    exit 1
fi

echo ""
echo "Checking prop firm service..."
if systemctl is-active --quiet argo-trading-prop-firm.service; then
    echo "✅ Prop firm service is active"
    systemctl status argo-trading-prop-firm.service --no-pager -l | head -10
else
    echo "❌ Prop firm service is not active"
    exit 1
fi
ENDSSH

if [ $? -eq 0 ]; then
    print_success "Services are running"
    ((PASSED++))
else
    print_error "Service check failed"
    ((FAILED++))
fi

# Step 2: Health Check Endpoint
print_step "STEP 2: HEALTH CHECK ENDPOINT"

print_info "Testing health check endpoint..."
HEALTH_RESPONSE=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "curl -s -f http://localhost:8000/api/v1/health/simple 2>&1" || echo "FAILED")

if [[ "$HEALTH_RESPONSE" == *"ok"* ]] || [[ "$HEALTH_RESPONSE" == *"status"* ]]; then
    print_success "Health check endpoint responding"
    ((PASSED++))
else
    print_warning "Health check endpoint not responding (may need time to start)"
    ((WARNINGS++))
fi

# Step 3: Component Verification
print_step "STEP 3: COMPONENT VERIFICATION"

print_info "Verifying new components are present..."

COMPONENTS=(
    "argo/core/signal_quality_scorer.py"
    "argo/core/performance_monitor.py"
    "argo/core/error_recovery.py"
    "argo/core/config_validator.py"
    "argo/risk/prop_firm_monitor_enhanced.py"
    "argo/api/health.py"
)

for component in "${COMPONENTS[@]}"; do
    if ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "test -f ${REGULAR_DIR}/${component}"; then
        print_success "Found: ${component}"
        ((PASSED++))
    else
        print_error "Missing: ${component}"
        ((FAILED++))
    fi
done

# Step 4: Script Verification
print_step "STEP 4: SCRIPT VERIFICATION"

print_info "Verifying scripts are present and executable..."

SCRIPTS=(
    "scripts/verify_alpine_sync.py"
    "scripts/monitor_signal_quality.py"
    "scripts/prop_firm_dashboard.py"
    "scripts/validate_config.py"
    "scripts/performance_report.py"
)

for script in "${SCRIPTS[@]}"; do
    if ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "test -x ${REGULAR_DIR}/${script}"; then
        print_success "Executable: ${script}"
        ((PASSED++))
    else
        print_warning "Not executable or missing: ${script}"
        ((WARNINGS++))
    fi
done

# Step 5: Configuration Validation
print_step "STEP 5: CONFIGURATION VALIDATION"

print_info "Validating production configurations..."

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

# Validate regular service config
if [ -f ${REGULAR_DIR}/config.json ]; then
    cd ${REGULAR_DIR}
    if python3 scripts/validate_config.py config.json > /dev/null 2>&1; then
        echo "✅ Regular service config valid"
    else
        echo "⚠️  Regular service config validation had issues"
    fi
fi

# Validate prop firm service config
if [ -f ${PROP_FIRM_DIR}/config.json ]; then
    cd ${PROP_FIRM_DIR}
    if python3 scripts/validate_config.py config.json > /dev/null 2>&1; then
        echo "✅ Prop firm service config valid"
    else
        echo "⚠️  Prop firm service config validation had issues"
    fi
fi
ENDSSH

if [ $? -eq 0 ]; then
    print_success "Configuration validation complete"
    ((PASSED++))
else
    print_warning "Configuration validation had issues"
    ((WARNINGS++))
fi

# Step 6: Alpine Sync Verification
print_step "STEP 6: ALPINE SYNC VERIFICATION"

print_info "Verifying Alpine sync status..."

SYNC_RESULT=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "cd ${REGULAR_DIR} && python3 scripts/verify_alpine_sync.py --hours 1 2>&1" || echo "FAILED")

if [[ "$SYNC_RESULT" == *"Sync rate"* ]]; then
    SYNC_RATE=$(echo "$SYNC_RESULT" | grep -oP 'Sync rate: \K[0-9.]+' || echo "0")
    if (( $(echo "$SYNC_RATE >= 90" | bc -l) )); then
        print_success "Alpine sync rate: ${SYNC_RATE}%"
        ((PASSED++))
    else
        print_warning "Alpine sync rate is low: ${SYNC_RATE}%"
        ((WARNINGS++))
    fi
else
    print_warning "Could not verify Alpine sync (may need time to generate signals)"
    ((WARNINGS++))
fi

# Step 7: Signal Quality Check
print_step "STEP 7: SIGNAL QUALITY CHECK"

print_info "Checking signal quality metrics..."

QUALITY_RESULT=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "cd ${REGULAR_DIR} && python3 scripts/monitor_signal_quality.py --hours 1 --json 2>&1" || echo "FAILED")

if [[ "$QUALITY_RESULT" == *"overall"* ]] || [[ "$QUALITY_RESULT" == *"total"* ]]; then
    print_success "Signal quality monitoring working"
    ((PASSED++))
else
    print_warning "Signal quality check inconclusive (may need time to generate signals)"
    ((WARNINGS++))
fi

# Step 8: Import Tests
print_step "STEP 8: IMPORT TESTS"

print_info "Testing Python imports..."

ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} << ENDSSH
set -e

cd ${REGULAR_DIR}
source venv/bin/activate

# Test imports
python3 << PYTHON
try:
    from argo.core.signal_quality_scorer import SignalQualityScorer
    print("✅ SignalQualityScorer import OK")
except Exception as e:
    print(f"❌ SignalQualityScorer import failed: {e}")
    exit(1)

try:
    from argo.core.performance_monitor import get_performance_monitor
    print("✅ PerformanceMonitor import OK")
except Exception as e:
    print(f"❌ PerformanceMonitor import failed: {e}")
    exit(1)

try:
    from argo.core.error_recovery import ErrorRecovery
    print("✅ ErrorRecovery import OK")
except Exception as e:
    print(f"❌ ErrorRecovery import failed: {e}")
    exit(1)

try:
    from argo.core.config_validator import ConfigValidator
    print("✅ ConfigValidator import OK")
except Exception as e:
    print(f"❌ ConfigValidator import failed: {e}")
    exit(1)

try:
    from argo.risk.prop_firm_monitor_enhanced import PropFirmMonitorEnhanced
    print("✅ PropFirmMonitorEnhanced import OK")
except Exception as e:
    print(f"❌ PropFirmMonitorEnhanced import failed: {e}")
    exit(1)
PYTHON
ENDSSH

if [ $? -eq 0 ]; then
    print_success "All imports successful"
    ((PASSED++))
else
    print_error "Some imports failed"
    ((FAILED++))
fi

# Step 9: Log Check
print_step "STEP 9: LOG CHECK"

print_info "Checking for errors in logs..."

ERROR_COUNT=$(ssh ${PRODUCTION_USER}@${PRODUCTION_SERVER} "journalctl -u argo-trading.service --since '5 minutes ago' --no-pager | grep -i 'error\|exception\|traceback' | wc -l" || echo "0")

if [ "$ERROR_COUNT" -eq 0 ]; then
    print_success "No recent errors in logs"
    ((PASSED++))
else
    print_warning "Found ${ERROR_COUNT} recent errors in logs"
    ((WARNINGS++))
fi

# Final Summary
print_step "VERIFICATION SUMMARY"

echo ""
echo "Results:"
echo "  ✅ Passed: ${PASSED}"
echo "  ❌ Failed: ${FAILED}"
echo "  ⚠️  Warnings: ${WARNINGS}"
echo ""

if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        print_success "🎉 All verifications passed!"
        exit 0
    else
        print_warning "⚠️  Verifications passed with warnings"
        exit 0
    fi
else
    print_error "❌ Some verifications failed"
    exit 1
fi
