#!/bin/bash
# Verification Script for Argo Blue-Green Setup
# Non-interactive verification of current state

set -e

ARGO_SERVER="178.156.194.174"
ARGO_USER="root"
BLUE_PATH="/root/argo-production-blue"
GREEN_PATH="/root/argo-production-green"
LEGACY_PATH="/root/argo-production"

echo "🔍 VERIFYING ARGO BLUE-GREEN SETUP"
echo "===================================="
echo ""

# Check current active service
echo "📊 Current Service Status:"
echo "---------------------------"
ACTIVE_SERVICE=$(ssh ${ARGO_USER}@${ARGO_SERVER} "
    if lsof -i :8000 2>/dev/null | grep -q uvicorn; then
        PID=\$(lsof -ti :8000 | head -1)
        if [ -n \"\$PID\" ]; then
            CWD=\$(pwdx \$PID 2>/dev/null | awk '{print \$2}' || readlink /proc/\$PID/cwd 2>/dev/null || echo '')
            if echo \"\$CWD\" | grep -q 'blue'; then
                echo 'blue'
            elif echo \"\$CWD\" | grep -q 'green'; then
                echo 'green'
            elif echo \"\$CWD\" | grep -q 'argo-production\$'; then
                echo 'legacy'
            else
                echo 'unknown'
            fi
        else
            echo 'unknown'
        fi
    else
        echo 'none'
    fi
" 2>/dev/null || echo "none")

if [ "$ACTIVE_SERVICE" = "blue" ]; then
    echo "✅ Active: BLUE environment (port 8000)"
    CURRENT_COLOR="blue"
elif [ "$ACTIVE_SERVICE" = "green" ]; then
    echo "✅ Active: GREEN environment (port 8000)"
    CURRENT_COLOR="green"
elif [ "$ACTIVE_SERVICE" = "legacy" ]; then
    echo "⚠️  Active: LEGACY environment (/root/argo-production)"
    CURRENT_COLOR="legacy"
elif [ "$ACTIVE_SERVICE" = "none" ]; then
    echo "❌ No active service on port 8000"
    CURRENT_COLOR="none"
else
    echo "⚠️  Active: UNKNOWN environment"
    CURRENT_COLOR="unknown"
fi

# Check directories
echo ""
echo "📁 Directory Status:"
echo "-------------------"
BLUE_EXISTS=$(ssh ${ARGO_USER}@${ARGO_SERVER} "[ -d ${BLUE_PATH} ] && echo 'yes' || echo 'no'" 2>/dev/null || echo "no")
GREEN_EXISTS=$(ssh ${ARGO_USER}@${ARGO_SERVER} "[ -d ${GREEN_PATH} ] && echo 'yes' || echo 'no'" 2>/dev/null || echo "no")
LEGACY_EXISTS=$(ssh ${ARGO_USER}@${ARGO_SERVER} "[ -d ${LEGACY_PATH} ] && echo 'yes' || echo 'no'" 2>/dev/null || echo "no")

if [ "$BLUE_EXISTS" = "yes" ]; then
    echo "✅ Blue environment exists: ${BLUE_PATH}"
else
    echo "❌ Blue environment missing: ${BLUE_PATH}"
fi

if [ "$GREEN_EXISTS" = "yes" ]; then
    echo "✅ Green environment exists: ${GREEN_PATH}"
else
    echo "❌ Green environment missing: ${GREEN_PATH}"
fi

if [ "$LEGACY_EXISTS" = "yes" ]; then
    echo "⚠️  Legacy environment exists: ${LEGACY_PATH}"
else
    echo "✅ No legacy environment (good - fully migrated)"
fi

# Check health endpoint
echo ""
echo "🏥 Health Check:"
echo "----------------"
HEALTH_RESPONSE=$(curl -s --max-time 5 http://${ARGO_SERVER}:8000/health 2>&1)
if echo "$HEALTH_RESPONSE" | grep -q "healthy\|status"; then
    echo "✅ Health endpoint responding"
    echo "$HEALTH_RESPONSE" | head -5
else
    echo "❌ Health endpoint not responding"
    echo "   Response: $HEALTH_RESPONSE"
fi

# Check for services on internal port
echo ""
echo "🔌 Internal Port Status:"
echo "------------------------"
INTERNAL_SERVICE=$(ssh ${ARGO_USER}@${ARGO_SERVER} "lsof -i :8001 2>/dev/null | grep uvicorn || echo 'none'" 2>/dev/null || echo "none")
if [ "$INTERNAL_SERVICE" != "none" ]; then
    echo "⚠️  Service found on port 8001 (internal/staging port)"
    echo "   This might be a test service or old environment"
else
    echo "✅ No service on port 8001 (expected)"
fi

# Summary and recommendations
echo ""
echo "======================================================================"
echo "📋 SUMMARY & RECOMMENDATIONS"
echo "======================================================================"
echo ""

if [ "$CURRENT_COLOR" = "legacy" ]; then
    echo "⚠️  LEGACY DEPLOYMENT DETECTED"
    echo ""
    echo "Recommendation:"
    echo "  1. Run: ./scripts/deploy-argo-blue-green.sh"
    echo "     This will automatically migrate legacy to blue-green"
    echo ""
elif [ "$CURRENT_COLOR" = "blue" ] || [ "$CURRENT_COLOR" = "green" ]; then
    echo "✅ BLUE-GREEN DEPLOYMENT ACTIVE"
    echo ""
    echo "Current Status:"
    echo "  - Active: $CURRENT_COLOR environment"
    echo "  - Blue exists: $BLUE_EXISTS"
    echo "  - Green exists: $GREEN_EXISTS"
    echo ""
    if [ "$BLUE_EXISTS" = "no" ] || [ "$GREEN_EXISTS" = "no" ]; then
        echo "⚠️  Missing environment detected"
        echo ""
        echo "Recommendation:"
        echo "  1. Run: ./scripts/deploy-argo-blue-green.sh"
        echo "     This will create missing environment and deploy"
        echo ""
    else
        echo "✅ Both environments exist - ready for blue-green deployment"
        echo ""
        echo "Next Steps:"
        echo "  1. Test deployment: ./scripts/test-argo-blue-green.sh"
        echo "  2. Full deployment: ./scripts/deploy-argo-blue-green.sh"
        echo ""
    fi
elif [ "$CURRENT_COLOR" = "none" ]; then
    echo "❌ NO ACTIVE SERVICE"
    echo ""
    echo "Recommendation:"
    echo "  1. Check if service crashed: ssh ${ARGO_USER}@${ARGO_SERVER} 'ps aux | grep uvicorn'"
    echo "  2. Check logs: ssh ${ARGO_USER}@${ARGO_SERVER} 'tail -50 /tmp/argo*.log'"
    echo "  3. Deploy: ./scripts/deploy-argo-blue-green.sh"
    echo ""
else
    echo "⚠️  UNKNOWN STATE"
    echo ""
    echo "Recommendation:"
    echo "  1. Investigate current state"
    echo "  2. Run: ./scripts/deploy-argo-blue-green.sh"
    echo ""
fi

echo "======================================================================"

