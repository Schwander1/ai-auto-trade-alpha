#!/bin/bash
# Start local services
set -e

PROJECT="${1:-all}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "$WORKSPACE_DIR"

# Source dependency checking utilities
if [ -f "$WORKSPACE_DIR/scripts/lib/wait-for-dependencies.sh" ]; then
    source "$WORKSPACE_DIR/scripts/lib/wait-for-dependencies.sh"
fi

if [ "$PROJECT" = "all" ] || [ "$PROJECT" = "alpine" ]; then
    echo "  Starting Alpine databases..."
    docker-compose -f alpine-backend/docker-compose.local.yml up -d 2>/dev/null || true
    
    # Wait for databases to be ready
    if command -v wait_for_postgres &> /dev/null; then
        echo "  Waiting for PostgreSQL to be ready..."
        export POSTGRES_HOST=localhost
        export POSTGRES_PORT=5433
        export POSTGRES_USER=alpine_user
        export POSTGRES_DB=alpine_analytics
        wait_for_postgres "PostgreSQL" || echo "  ⚠️  PostgreSQL may not be ready yet"
    fi
fi

if [ "$PROJECT" = "all" ] || [ "$PROJECT" = "argo" ]; then
    echo "  Starting Argo..."
    cd argo
    if [ ! -d "venv" ]; then
        echo "  ⚠️  Virtual environment not found. Creating..."
        python3 -m venv venv
    fi
    source venv/bin/activate
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 > /tmp/argo-local.log 2>&1 &
    ARGO_PID=$!
    echo "  ✅ Argo started (PID: $ARGO_PID, logs: /tmp/argo-local.log)"
    echo "  🌐 Argo: http://localhost:8000"
    
    # Wait for Argo to be ready
    if command -v wait_for_service &> /dev/null; then
        echo "  Waiting for Argo to be ready..."
        wait_for_service "http://localhost:8000/health" "Argo" 10
    else
        sleep 3
    fi
    cd ..
fi

if [ "$PROJECT" = "all" ] || [ "$PROJECT" = "alpine" ]; then
    echo "  Starting Alpine Backend..."
    cd alpine-backend
    if [ ! -d "venv" ]; then
        echo "  ⚠️  Virtual environment not found. Creating..."
        python3 -m venv venv
    fi
    source venv/bin/activate
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 9001 > /tmp/alpine-backend-local.log 2>&1 &
    ALPINE_BACKEND_PID=$!
    echo "  ✅ Alpine Backend started (PID: $ALPINE_BACKEND_PID, logs: /tmp/alpine-backend-local.log)"
    echo "  🌐 Alpine Backend: http://localhost:9001"
    
    # Wait for backend to be ready
    if command -v wait_for_service &> /dev/null; then
        echo "  Waiting for Alpine Backend to be ready..."
        wait_for_service "http://localhost:9001/health" "Alpine Backend" 10
    else
        sleep 3
    fi
    cd ..
    
    echo "  Starting Alpine Frontend..."
    cd alpine-frontend
    npm run dev > /tmp/alpine-frontend-local.log 2>&1 &
    ALPINE_FRONTEND_PID=$!
    echo "  ✅ Alpine Frontend started (PID: $ALPINE_FRONTEND_PID, logs: /tmp/alpine-frontend-local.log)"
    echo "  🌐 Alpine Frontend: http://localhost:3000"
    cd ..
fi

echo ""
echo "✅ All requested services started!"
echo ""
echo "📋 Service URLs:"
[ "$PROJECT" = "all" ] || [ "$PROJECT" = "argo" ] && echo "  - Argo: http://localhost:8000"
[ "$PROJECT" = "all" ] || [ "$PROJECT" = "alpine" ] && echo "  - Alpine Backend: http://localhost:9001"
[ "$PROJECT" = "all" ] || [ "$PROJECT" = "alpine" ] && echo "  - Alpine Frontend: http://localhost:3000"
echo ""
echo "📝 Logs:"
[ "$PROJECT" = "all" ] || [ "$PROJECT" = "argo" ] && echo "  - Argo: tail -f /tmp/argo-local.log"
[ "$PROJECT" = "all" ] || [ "$PROJECT" = "alpine" ] && echo "  - Alpine Backend: tail -f /tmp/alpine-backend-local.log"
[ "$PROJECT" = "all" ] || [ "$PROJECT" = "alpine" ] && echo "  - Alpine Frontend: tail -f /tmp/alpine-frontend-local.log"

