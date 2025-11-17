#!/bin/bash
# View logs for production services
set -e

ACTION="${1:-view}"
PROJECT="${2:-all}"

ARGO_SERVER="178.156.194.174"
ALPINE_SERVER="91.98.153.49"

if [ "$ACTION" = "follow" ]; then
    FOLLOW_FLAG="-f"
else
    FOLLOW_FLAG=""
fi

if [ "$PROJECT" = "all" ] || [ "$PROJECT" = "argo" ]; then
    echo "📋 Argo Production Logs:"
    echo "  Server: $ARGO_SERVER"
    
    # Determine active environment
    ACTIVE_ENV=$(ssh root@${ARGO_SERVER} "
        if [ -f /root/argo-production-green/.current ]; then
            echo 'green'
        elif [ -f /root/argo-production-blue/.current ]; then
            echo 'blue'
        else
            echo 'blue'
        fi
    " 2>/dev/null || echo "blue")
    
    echo "  Active Environment: $ACTIVE_ENV"
    echo ""
    
    if [ "$ACTION" = "follow" ]; then
        ssh root@${ARGO_SERVER} "tail -f /tmp/argo-${ACTIVE_ENV}.log"
    else
        ssh root@${ARGO_SERVER} "tail -n 50 /tmp/argo-${ACTIVE_ENV}.log"
    fi
fi

if [ "$PROJECT" = "all" ] || [ "$PROJECT" = "alpine" ]; then
    if [ "$PROJECT" != "all" ]; then
        echo ""
    fi
    echo "📋 Alpine Production Logs:"
    echo "  Server: $ALPINE_SERVER"
    echo ""
    
    if [ "$ACTION" = "follow" ]; then
        ssh root@${ALPINE_SERVER} "docker-compose -f /root/alpine-production/docker-compose.yml logs -f backend"
    else
        ssh root@${ALPINE_SERVER} "docker-compose -f /root/alpine-production/docker-compose.yml logs --tail=50 backend"
    fi
fi

