#!/bin/bash
# Stop local services
set -e

PROJECT="${1:-all}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "$WORKSPACE_DIR"

if [ "$PROJECT" = "all" ] || [ "$PROJECT" = "argo" ]; then
    echo "  Stopping Argo..."
    pkill -f "uvicorn main:app.*8000" 2>/dev/null && echo "  ✅ Argo stopped" || echo "  ⚠️  Argo not running"
fi

if [ "$PROJECT" = "all" ] || [ "$PROJECT" = "alpine" ]; then
    echo "  Stopping Alpine Backend..."
    pkill -f "uvicorn backend.main:app.*9001" 2>/dev/null && echo "  ✅ Alpine Backend stopped" || echo "  ⚠️  Alpine Backend not running"
    
    echo "  Stopping Alpine Frontend..."
    pkill -f "npm run dev" 2>/dev/null && echo "  ✅ Alpine Frontend stopped" || echo "  ⚠️  Alpine Frontend not running"
    
    echo "  Stopping Alpine databases..."
    docker-compose -f alpine-backend/docker-compose.local.yml down 2>/dev/null && echo "  ✅ Alpine databases stopped" || echo "  ⚠️  Alpine databases not running"
fi

echo ""
echo "✅ All requested services stopped!"

