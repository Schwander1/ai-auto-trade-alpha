#!/bin/bash
# Status check for local services
set -e

PROJECT="${1:-all}"

echo "📊 Local Status Check"
echo "===================="
echo ""

if [ "$PROJECT" = "all" ] || [ "$PROJECT" = "argo" ]; then
    echo "🔍 Argo Service Status:"
    if pgrep -f "uvicorn main:app.*8000" > /dev/null; then
        echo "  Status: ✅ RUNNING"
        PID=$(pgrep -f "uvicorn main:app.*8000" | head -1)
        echo "  PID: $PID"
        if curl -s "http://localhost:8000/health" | grep -q "healthy"; then
            echo "  Health: ✅ HEALTHY"
            curl -s "http://localhost:8000/health" | python3 -m json.tool 2>/dev/null | grep -E '(status|version|uptime)' || true
        else
            echo "  Health: ❌ UNHEALTHY"
        fi
    else
        echo "  Status: ❌ NOT RUNNING"
    fi
    echo ""
fi

if [ "$PROJECT" = "all" ] || [ "$PROJECT" = "alpine" ]; then
    echo "🔍 Alpine Backend Status:"
    if pgrep -f "uvicorn backend.main:app.*9001" > /dev/null; then
        echo "  Status: ✅ RUNNING"
        PID=$(pgrep -f "uvicorn backend.main:app.*9001" | head -1)
        echo "  PID: $PID"
        if curl -s "http://localhost:9001/health" | grep -q "healthy"; then
            echo "  Health: ✅ HEALTHY"
        else
            echo "  Health: ❌ UNHEALTHY"
        fi
    else
        echo "  Status: ❌ NOT RUNNING"
    fi
    echo ""
    
    echo "🔍 Alpine Frontend Status:"
    if pgrep -f "npm run dev" > /dev/null; then
        echo "  Status: ✅ RUNNING"
        PID=$(pgrep -f "npm run dev" | head -1)
        echo "  PID: $PID"
        if curl -s "http://localhost:3000" > /dev/null 2>&1; then
            echo "  Health: ✅ HEALTHY"
        else
            echo "  Health: ❌ UNHEALTHY"
        fi
    else
        echo "  Status: ❌ NOT RUNNING"
    fi
    echo ""
    
    echo "🔍 Alpine Databases Status:"
    if docker ps | grep -q "alpine.*postgres\|alpine.*redis"; then
        echo "  Status: ✅ RUNNING"
        docker ps --format "table {{.Names}}\t{{.Status}}" | grep alpine || true
    else
        echo "  Status: ❌ NOT RUNNING"
    fi
    echo ""
fi

