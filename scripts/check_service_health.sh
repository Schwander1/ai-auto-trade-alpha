#!/bin/bash
# Enhanced health check with retries and proper parsing
# Waits for service to be healthy after deployment

set -e

ARGO_SERVER="${1:-178.156.194.174}"
PORT="${2:-8000}"
MAX_RETRIES="${3:-30}"
RETRY_DELAY="${4:-2}"

BASE_URL="http://${ARGO_SERVER}:${PORT}"

echo "🔍 Checking service health..."
echo "=============================="
echo "Target: ${BASE_URL}"
echo "Max retries: ${MAX_RETRIES}"
echo "Retry delay: ${RETRY_DELAY}s"
echo ""

for i in $(seq 1 $MAX_RETRIES); do
    # Try to get health response
    HEALTH_RESPONSE=$(curl -s --max-time 5 "${BASE_URL}/api/v1/health" 2>/dev/null || echo "")
    
    if [ -n "$HEALTH_RESPONSE" ]; then
        # Parse health response using Python
        STATUS=$(echo "$HEALTH_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('status', 'unknown'))
except:
    print('error')
" 2>/dev/null || echo "error")
        
        if [ "$STATUS" != "error" ]; then
            VERSION=$(echo "$HEALTH_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('version', 'unknown'))
except:
    print('unknown')
" 2>/dev/null || echo "unknown")
            
            # Get data source info
            DS_INFO=$(echo "$HEALTH_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    ds = data.get('services', {}).get('data_sources', {})
    healthy = ds.get('healthy', 0)
    unhealthy = ds.get('unhealthy', 0)
    print(f'{healthy} healthy, {unhealthy} unhealthy')
except:
    print('unknown')
" 2>/dev/null || echo "unknown")
            
            echo "✅ Service is $STATUS"
            echo "   Version: $VERSION"
            echo "   Data sources: $DS_INFO"
            
            # Check if service is healthy or degraded (both are acceptable)
            if [ "$STATUS" = "healthy" ] || [ "$STATUS" = "degraded" ]; then
                echo ""
                echo "✅ Service health check passed"
                exit 0
            else
                echo "⚠️  Service status is $STATUS (waiting for improvement...)"
            fi
        fi
    fi
    
    if [ $i -lt $MAX_RETRIES ]; then
        echo "⏳ Waiting for service... [$i/$MAX_RETRIES]"
        sleep $RETRY_DELAY
    fi
done

echo ""
echo "❌ Service health check failed after ${MAX_RETRIES} retries"
echo "   Service may not be responding or is unhealthy"
exit 1


