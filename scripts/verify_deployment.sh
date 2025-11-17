#!/bin/bash
# Post-deployment verification script
# Verifies all files were deployed correctly

set -e

ARGO_SERVER="${1:-178.156.194.174}"
ARGO_USER="${2:-root}"
TARGET_PATH="${3:-/root/argo-production-green}"

echo "🔍 Verifying deployment..."
echo "=========================="

ERRORS=0

# Verify optimization modules
echo ""
echo "1. Verifying optimization modules..."
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
        else
            echo \"  ✅ \${module}\"
        fi
    done
    
    exit \$MISSING
" || ERRORS=$((ERRORS + 1))

# Verify core service files
echo ""
echo "2. Verifying core service files..."
ssh ${ARGO_USER}@${ARGO_SERVER} "
    FILES=(
        'signal_generation_service.py'
        'signal_tracker.py'
        'data_source_health.py'
    )
    
    MISSING=0
    for file in \"\${FILES[@]}\"; do
        if [ ! -f ${TARGET_PATH}/argo/argo/core/\${file} ]; then
            echo \"❌ Missing: \${file}\"
            MISSING=1
        else
            echo \"  ✅ \${file}\"
        fi
    done
    
    exit \$MISSING
" || ERRORS=$((ERRORS + 1))

# Verify data source files
echo ""
echo "3. Verifying data source files..."
ssh ${ARGO_USER}@${ARGO_SERVER} "
    FILES=(
        'massive_source.py'
        'alpha_vantage_source.py'
    )
    
    MISSING=0
    for file in \"\${FILES[@]}\"; do
        if [ ! -f ${TARGET_PATH}/argo/argo/core/data_sources/\${file} ]; then
            echo \"❌ Missing: \${file}\"
            MISSING=1
        else
            echo \"  ✅ \${file}\"
        fi
    done
    
    exit \$MISSING
" || ERRORS=$((ERRORS + 1))

# Verify API files
echo ""
echo "4. Verifying API files..."
ssh ${ARGO_USER}@${ARGO_SERVER} "
    FILES=(
        'health.py'
    )
    
    MISSING=0
    for file in \"\${FILES[@]}\"; do
        if [ ! -f ${TARGET_PATH}/argo/argo/api/\${file} ]; then
            echo \"❌ Missing: \${file}\"
            MISSING=1
        else
            echo \"  ✅ \${file}\"
        fi
    done
    
    exit \$MISSING
" || ERRORS=$((ERRORS + 1))

# Verify config.json
echo ""
echo "5. Verifying config.json..."
ssh ${ARGO_USER}@${ARGO_SERVER} "
    if [ ! -f ${TARGET_PATH}/config.json ]; then
        echo '❌ config.json not found'
        exit 1
    fi
    
    # Check file is valid JSON
    python3 -c 'import json; json.load(open(\"${TARGET_PATH}/config.json\"))' 2>/dev/null || {
        echo '❌ config.json is invalid JSON'
        exit 1
    }
    
    echo '  ✅ config.json present and valid'
" || ERRORS=$((ERRORS + 1))

# Summary
echo ""
echo "=========================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ Deployment verification passed"
    exit 0
else
    echo "❌ Deployment verification failed ($ERRORS error(s))"
    exit 1
fi


