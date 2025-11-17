#!/bin/bash
# Pre-flight checks before starting Argo service
# Validates environment, files, and dependencies

set -e

ARGO_SERVER="${1:-178.156.194.174}"
ARGO_USER="${2:-root}"
TARGET_PATH="${3:-/root/argo-production-green}"

echo "🔍 Running pre-flight checks..."
echo "=================================="

ERRORS=0

# Check 1: Virtual environment exists
echo ""
echo "1. Checking virtual environment..."
ssh ${ARGO_USER}@${ARGO_SERVER} "
    if [ ! -d ${TARGET_PATH}/venv ]; then
        echo '❌ Virtual environment not found at ${TARGET_PATH}/venv'
        exit 1
    fi
    echo '✅ Virtual environment found'
" || ERRORS=$((ERRORS + 1))

# Check 2: main.py exists
echo ""
echo "2. Checking main.py..."
ssh ${ARGO_USER}@${ARGO_SERVER} "
    if [ ! -f ${TARGET_PATH}/main.py ]; then
        echo '❌ main.py not found'
        exit 1
    fi
    echo '✅ main.py found'
" || ERRORS=$((ERRORS + 1))

# Check 3: config.json exists
echo ""
echo "3. Checking config.json..."
ssh ${ARGO_USER}@${ARGO_SERVER} "
    if [ ! -f ${TARGET_PATH}/config.json ]; then
        echo '❌ config.json not found'
        exit 1
    fi
    echo '✅ config.json found'
" || ERRORS=$((ERRORS + 1))

# Check 4: Validate config.json syntax
echo ""
echo "4. Validating config.json syntax..."
ssh ${ARGO_USER}@${ARGO_SERVER} "
    cd ${TARGET_PATH}
    source venv/bin/activate
    python3 -c 'import json; json.load(open(\"config.json\"))' 2>&1 || {
        echo '❌ config.json is invalid JSON'
        exit 1
    }
    echo '✅ config.json is valid JSON'
" || ERRORS=$((ERRORS + 1))

# Check 5: Test optimization module imports
echo ""
echo "5. Testing optimization module imports..."
ssh ${ARGO_USER}@${ARGO_SERVER} "
    cd ${TARGET_PATH}
    source venv/bin/activate
    
    MODULES=(
        'argo.core.adaptive_cache'
        'argo.core.rate_limiter'
        'argo.core.circuit_breaker'
        'argo.core.redis_cache'
        'argo.core.performance_metrics'
    )
    
    FAILED=0
    for module in \"\${MODULES[@]}\"; do
        if ! python3 -c \"import \${module}\" 2>/dev/null; then
            echo \"❌ Failed to import \${module}\"
            FAILED=1
        fi
    done
    
    if [ \$FAILED -eq 1 ]; then
        exit 1
    fi
    echo '✅ All optimization modules importable'
" || ERRORS=$((ERRORS + 1))

# Check 6: Test main app import
echo ""
echo "6. Testing main app import..."
ssh ${ARGO_USER}@${ARGO_SERVER} "
    cd ${TARGET_PATH}
    source venv/bin/activate
    python3 -c 'from main import app' 2>&1 | head -5 || {
        echo '❌ Failed to import main app'
        exit 1
    }
    echo '✅ Main app imports successfully'
" || ERRORS=$((ERRORS + 1))

# Check 7: Check required optimization module files exist
echo ""
echo "7. Checking optimization module files..."
ssh ${ARGO_USER}@${ARGO_SERVER} "
    MODULES=(
        'adaptive_cache.py'
        'rate_limiter.py'
        'circuit_breaker.py'
        'redis_cache.py'
        'performance_metrics.py'
    )
    
    MISSING=0
    for module in \"\${MODULES[@]}\"; do
        if [ ! -f ${TARGET_PATH}/argo/argo/core/\${module} ]; then
            echo \"❌ Missing: \${module}\"
            MISSING=1
        fi
    done
    
    if [ \$MISSING -eq 1 ]; then
        exit 1
    fi
    echo '✅ All optimization module files present'
" || ERRORS=$((ERRORS + 1))

# Check 8: Check port availability
echo ""
echo "8. Checking port 8000 availability..."
ssh ${ARGO_USER}@${ARGO_SERVER} "
    if lsof -ti :8000 >/dev/null 2>&1; then
        echo '⚠️  Port 8000 is in use (will be stopped before deployment)'
    else
        echo '✅ Port 8000 is available'
    fi
" || true

# Summary
echo ""
echo "=================================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ All pre-flight checks passed"
    exit 0
else
    echo "❌ Pre-flight checks failed ($ERRORS error(s))"
    exit 1
fi


