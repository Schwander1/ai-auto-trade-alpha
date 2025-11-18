#!/bin/sh
set -e

echo "🚀 Starting Alpine Frontend..."

# Wait for backend to be ready (optional, but helpful)
if [ -n "$NEXT_PUBLIC_API_URL" ]; then
    echo "⏳ Waiting for backend API to be ready..."
    MAX_RETRIES=30
    RETRY_COUNT=0
    
    # Extract base URL from NEXT_PUBLIC_API_URL
    BACKEND_URL=$(echo "$NEXT_PUBLIC_API_URL" | sed 's|/api$||')
    HEALTH_URL="${BACKEND_URL}/health"
    
    until wget --spider --quiet --timeout=5 "$HEALTH_URL" 2>/dev/null || \
          curl -sf --max-time 5 "$HEALTH_URL" >/dev/null 2>&1; do
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
            echo "⚠️  WARNING: Backend API not ready after $MAX_RETRIES attempts, continuing anyway..."
            break
        fi
        echo "   Retry $RETRY_COUNT/$MAX_RETRIES..."
        sleep 2
    done
    
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
        echo "✅ Backend API is ready"
    fi
fi

echo "🚀 Starting Next.js application..."

# Execute the main command
exec "$@"

