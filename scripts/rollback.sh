#!/bin/bash
# Rollback script for Argo Trading Engine
# Quickly reverts to previous deployment

set -e

ARGO_SERVER="${1:-178.156.194.174}"
ARGO_USER="${2:-root}"
BLUE_PATH="/root/argo-production-blue"
GREEN_PATH="/root/argo-production-green"

echo "🔄 Rolling back Argo deployment..."
echo "==================================="

# Determine current and previous deployment
CURRENT_COLOR=$(ssh ${ARGO_USER}@${ARGO_SERVER} "
    if [ -f ${BLUE_PATH}/.current ]; then
        echo 'blue'
    elif [ -f ${GREEN_PATH}/.current ]; then
        echo 'green'
    else
        # Check which port has active service
        PID=\$(lsof -ti :8000 | head -1)
        if [ -n \"\$PID\" ]; then
            CWD=\$(pwdx \$PID 2>/dev/null | awk '{print \$2}' || readlink /proc/\$PID/cwd 2>/dev/null || echo '')
            if echo \"\$CWD\" | grep -q 'blue'; then
                echo 'blue'
            elif echo \"\$CWD\" | grep -q 'green'; then
                echo 'green'
            else
                echo 'unknown'
            fi
        else
            echo 'unknown'
        fi
    fi
" 2>/dev/null || echo "unknown")

if [ "$CURRENT_COLOR" = "blue" ]; then
    ROLLBACK_COLOR="green"
    ROLLBACK_PATH=$GREEN_PATH
    CURRENT_PATH=$BLUE_PATH
elif [ "$CURRENT_COLOR" = "green" ]; then
    ROLLBACK_COLOR="blue"
    ROLLBACK_PATH=$BLUE_PATH
    CURRENT_PATH=$GREEN_PATH
else
    echo "❌ Cannot determine current deployment. Manual rollback required."
    exit 1
fi

echo "Current deployment: $CURRENT_COLOR"
echo "Rolling back to: $ROLLBACK_COLOR"

# Verify rollback target exists
echo ""
echo "🔍 Verifying rollback target..."
ROLLBACK_EXISTS=$(ssh ${ARGO_USER}@${ARGO_SERVER} "[ -d ${ROLLBACK_PATH} ] && echo 'yes' || echo 'no'" 2>/dev/null || echo "no")

if [ "$ROLLBACK_EXISTS" != "yes" ]; then
    echo "❌ Rollback target ${ROLLBACK_PATH} does not exist"
    exit 1
fi

# Stop current service
echo ""
echo "🛑 Stopping current service..."
ssh ${ARGO_USER}@${ARGO_SERVER} "
    pkill -f 'uvicorn.*--port 8000' || true
    sleep 2
    rm -f ${CURRENT_PATH}/.current
    echo '✅ Current service stopped'
"

# Start rollback service
echo ""
echo "🚀 Starting rollback service..."
ssh ${ARGO_USER}@${ARGO_SERVER} "
    cd ${ROLLBACK_PATH}
    
    if [ ! -d venv ]; then
        echo '❌ Virtual environment not found in rollback target'
        exit 1
    fi
    
    source venv/bin/activate
    nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/argo-${ROLLBACK_COLOR}.log 2>&1 &
    echo \$! > /tmp/argo-${ROLLBACK_COLOR}.pid
    touch ${ROLLBACK_PATH}/.current
    
    sleep 3
    echo '✅ Rollback service started'
"

# Verify rollback
echo ""
echo "🔍 Verifying rollback..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f -s --max-time 5 http://${ARGO_SERVER}:8000/health > /dev/null 2>&1; then
        echo "✅ Rollback successful - service responding"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "⏳ Waiting for service... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Rollback verification failed - service not responding"
    exit 1
fi

echo ""
echo "✅ Rollback complete!"
echo "   Active deployment: $ROLLBACK_COLOR"
echo "   Previous deployment: $CURRENT_COLOR (stopped)"
