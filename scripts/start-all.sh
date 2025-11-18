#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source dependency checking utilities
if [ -f "$WORKSPACE_DIR/scripts/lib/wait-for-dependencies.sh" ]; then
    source "$WORKSPACE_DIR/scripts/lib/wait-for-dependencies.sh"
fi

echo "🚀 Starting Argo → Alpine Dev Environment..."

# Start databases
echo "📦 Starting databases..."
docker-compose -f "$WORKSPACE_DIR/alpine-backend/docker-compose.local.yml" up -d

# Wait for databases to be ready
if command -v wait_for_postgres &> /dev/null; then
    echo "⏳ Waiting for PostgreSQL..."
    export POSTGRES_HOST=localhost
    export POSTGRES_PORT=5433
    export POSTGRES_USER=alpine_user
    export POSTGRES_DB=alpine_analytics
    wait_for_postgres "PostgreSQL" || echo "⚠️  PostgreSQL may not be ready yet"
fi

# Start Argo in background
echo "🚀 Starting Argo..."
cd "$WORKSPACE_DIR/argo"
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > /tmp/argo-dev.log 2>&1 &
ARGO_PID=$!

# Wait for Argo to be ready
if command -v wait_for_service &> /dev/null; then
    echo "⏳ Waiting for Argo to be ready..."
    wait_for_service "http://localhost:8000/health" "Argo" 15
fi

# Start Alpine Backend in background
echo "🚀 Starting Alpine Backend..."
cd "$WORKSPACE_DIR/alpine-backend"
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 9001 > /tmp/alpine-backend-dev.log 2>&1 &
BACKEND_PID=$!

# Wait for Backend to be ready
if command -v wait_for_service &> /dev/null; then
    echo "⏳ Waiting for Alpine Backend to be ready..."
    wait_for_service "http://localhost:9001/health" "Alpine Backend" 15
fi

# Start Alpine Frontend
echo "🚀 Starting Alpine Frontend..."
cd "$WORKSPACE_DIR/alpine-frontend"
npm run dev > /tmp/alpine-frontend-dev.log 2>&1 &
FRONTEND_PID=$!

echo ""
echo "✅ All services started!"
echo "   Argo:     http://localhost:8000 (PID: $ARGO_PID)"
echo "   Backend:  http://localhost:9001 (PID: $BACKEND_PID)"
echo "   Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""
echo "📝 Logs:"
echo "   Argo:     tail -f /tmp/argo-dev.log"
echo "   Backend:  tail -f /tmp/alpine-backend-dev.log"
echo "   Frontend: tail -f /tmp/alpine-frontend-dev.log"
