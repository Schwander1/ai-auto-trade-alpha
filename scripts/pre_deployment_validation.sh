#!/bin/bash
# Pre-Deployment Validation Script
# Validates all components before deployment to ensure error-free deployment

set +e  # Don't exit on errors - we track them manually

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ARGO_DIR="${WORKSPACE_DIR}/argo"

echo "🔍 Pre-Deployment Validation"
echo "============================"
echo ""

ERRORS=0
WARNINGS=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✅${NC} $1"
}

check_fail() {
    echo -e "${RED}❌${NC} $1"
    ((ERRORS++))
}

check_warn() {
    echo -e "${YELLOW}⚠️${NC} $1"
    ((WARNINGS++))
}

# 1. Check Python syntax
echo "1. Checking Python syntax..."
cd "${ARGO_DIR}"
if python3 -m py_compile argo/core/signal_generation_service.py 2>/dev/null; then
    check_pass "signal_generation_service.py syntax valid"
else
    check_fail "signal_generation_service.py has syntax errors"
fi

if python3 -m py_compile argo/core/paper_trading_engine.py 2>/dev/null; then
    check_pass "paper_trading_engine.py syntax valid"
else
    check_fail "paper_trading_engine.py has syntax errors"
fi

if python3 -m py_compile argo/risk/prop_firm_risk_monitor.py 2>/dev/null; then
    check_pass "prop_firm_risk_monitor.py syntax valid"
else
    check_fail "prop_firm_risk_monitor.py has syntax errors"
fi

# 2. Check config.json syntax
echo ""
echo "2. Checking config.json..."
if python3 -c "import json; json.load(open('config.json'))" 2>/dev/null; then
    check_pass "config.json is valid JSON"
else
    check_fail "config.json has syntax errors"
fi

# 3. Check prop firm configuration
echo ""
echo "3. Checking prop firm configuration..."
python3 -c "
import json
import sys
config = json.load(open('config.json'))
prop_firm = config.get('prop_firm', {})
alpaca = config.get('alpaca', {})

# Check prop firm section exists
if not prop_firm:
    sys.exit(1)

# Check account exists
if 'prop_firm_test' not in alpaca:
    sys.exit(1)

# Check required fields
account = alpaca['prop_firm_test']
if not account.get('api_key') or not account.get('secret_key'):
    sys.exit(1)
" 2>/dev/null
CONFIG_CHECK=$?
if [ $CONFIG_CHECK -eq 0 ]; then
    check_pass "Prop firm configuration complete"
else
    check_fail "Prop firm configuration incomplete or invalid"
fi

# 4. Check imports
echo ""
echo "4. Checking imports..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from argo.risk.prop_firm_risk_monitor import PropFirmRiskMonitor
    from argo.core.paper_trading_engine import PaperTradingEngine
    from argo.core.signal_generation_service import SignalGenerationService
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)
" 2>/dev/null
IMPORT_CHECK=$?
if [ $IMPORT_CHECK -eq 0 ]; then
    check_pass "All imports successful"
else
    check_fail "Import errors detected"
fi

# 5. Run prop firm validation script
echo ""
echo "5. Running prop firm validation..."
if python3 scripts/validate_prop_firm_setup.py 2>&1 | grep -q "PROP FIRM SETUP VALIDATION PASSED"; then
    check_pass "Prop firm validation passed"
else
    check_warn "Prop firm validation had warnings (check output above)"
fi

# 6. Check systemd service files
echo ""
echo "6. Checking systemd service files..."
if [ -f "${WORKSPACE_DIR}/infrastructure/systemd/argo-trading.service" ]; then
    check_pass "Regular service file exists"
else
    check_warn "Regular service file not found"
fi

if [ -f "${WORKSPACE_DIR}/infrastructure/systemd/argo-trading-prop-firm.service" ]; then
    check_pass "Prop firm service file exists"
else
    check_warn "Prop firm service file not found"
fi

# 7. Check port availability (if on production server)
echo ""
echo "7. Checking port availability..."
if command -v lsof >/dev/null 2>&1; then
    if lsof -ti :8000 >/dev/null 2>&1; then
        check_warn "Port 8000 is in use (may be existing service)"
    else
        check_pass "Port 8000 is available"
    fi
    
    if lsof -ti :8001 >/dev/null 2>&1; then
        check_warn "Port 8001 is in use (may be existing service)"
    else
        check_pass "Port 8001 is available"
    fi
else
    check_warn "lsof not available - cannot check ports"
fi

# Summary
echo ""
echo "============================"
echo "Validation Summary"
echo "============================"
echo "Errors: ${ERRORS}"
echo "Warnings: ${WARNINGS}"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Validation PASSED${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  ${WARNINGS} warning(s) - review recommended${NC}"
    fi
    echo "Ready for deployment!"
    exit 0
else
    echo -e "${RED}❌ Validation FAILED${NC}"
    echo "Please fix errors before deploying"
    exit 1
fi
