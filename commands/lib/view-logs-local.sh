#!/bin/bash
# View logs for local services
set -e

ACTION="${1:-view}"
PROJECT="${2:-all}"

if [ "$ACTION" = "follow" ]; then
    FOLLOW_FLAG="-f"
else
    FOLLOW_FLAG=""
fi

if [ "$PROJECT" = "all" ] || [ "$PROJECT" = "argo" ]; then
    echo "📋 Argo Local Logs:"
    echo ""
    
    if [ "$ACTION" = "follow" ]; then
        tail -f /tmp/argo-local.log 2>/dev/null || echo "  ⚠️  Log file not found. Service may not be running."
    else
        tail -n 50 /tmp/argo-local.log 2>/dev/null || echo "  ⚠️  Log file not found. Service may not be running."
    fi
fi

if [ "$PROJECT" = "all" ] || [ "$PROJECT" = "alpine" ]; then
    if [ "$PROJECT" != "all" ]; then
        echo ""
    fi
    echo "📋 Alpine Backend Local Logs:"
    echo ""
    
    if [ "$ACTION" = "follow" ]; then
        tail -f /tmp/alpine-backend-local.log 2>/dev/null || echo "  ⚠️  Log file not found. Service may not be running."
    else
        tail -n 50 /tmp/alpine-backend-local.log 2>/dev/null || echo "  ⚠️  Log file not found. Service may not be running."
    fi
    
    if [ "$PROJECT" = "all" ]; then
        echo ""
    fi
    
    echo "📋 Alpine Frontend Local Logs:"
    echo ""
    
    if [ "$ACTION" = "follow" ]; then
        tail -f /tmp/alpine-frontend-local.log 2>/dev/null || echo "  ⚠️  Log file not found. Service may not be running."
    else
        tail -n 50 /tmp/alpine-frontend-local.log 2>/dev/null || echo "  ⚠️  Log file not found. Service may not be running."
    fi
fi

