#!/bin/bash
# Status check for production services
set -e

PROJECT="${1:-all}"

ARGO_SERVER="178.156.194.174"
ALPINE_SERVER="91.98.153.49"

echo "📊 Production Status Check"
echo "=========================="
echo ""

if [ "$PROJECT" = "all" ] || [ "$PROJECT" = "argo" ]; then
    echo "🔍 Argo Service Status:"
    echo "  Server: $ARGO_SERVER"
    
    # Check which environment is active
    ACTIVE_ENV=$(ssh root@${ARGO_SERVER} "
        if [ -f /root/argo-production-green/.current ]; then
            echo 'green'
        elif [ -f /root/argo-production-blue/.current ]; then
            echo 'blue'
        else
            echo 'unknown'
        fi
    " 2>/dev/null || echo "unknown")
    
    echo "  Active Environment: $ACTIVE_ENV"
    
    # Check if service is running
    if curl -s "http://${ARGO_SERVER}:8000/health" | grep -q "healthy"; then
        echo "  Status: ✅ RUNNING"
        curl -s "http://${ARGO_SERVER}:8000/health" | python3 -m json.tool 2>/dev/null | grep -E '(status|version|uptime)' || true
    else
        echo "  Status: ❌ DOWN"
    fi
    echo ""
fi

if [ "$PROJECT" = "all" ] || [ "$PROJECT" = "alpine" ]; then
    echo "🔍 Alpine Service Status:"
    echo "  Server: $ALPINE_SERVER"
    
    # Check Docker containers
    CONTAINERS=$(ssh root@${ALPINE_SERVER} "docker ps --format '{{.Names}}' | grep alpine-production" 2>/dev/null || echo "")
    if [ -n "$CONTAINERS" ]; then
        echo "  Status: ✅ RUNNING"
        echo "  Containers:"
        echo "$CONTAINERS" | sed 's/^/    - /'
    else
        echo "  Status: ❌ DOWN"
    fi
    
    # Check health endpoint
    if curl -s "http://${ALPINE_SERVER}:8001/health" | grep -q "healthy"; then
        echo "  Health: ✅ HEALTHY"
    else
        echo "  Health: ❌ UNHEALTHY"
    fi
    echo ""
fi

