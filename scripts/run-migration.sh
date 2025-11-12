#!/bin/bash
# Run database migration for indexes
# This script can be run locally or on production server

set -e

echo "🗄️  Running Database Index Migration"
echo "===================================="
echo ""

# Check if we're in Docker or local
if [ -f "/.dockerenv" ] || [ -n "$DOCKER_CONTAINER" ]; then
    echo "Running in Docker container..."
    cd /app/backend || cd /app
    python -m backend.migrations.add_indexes
else
    echo "Running locally..."
    cd "$(dirname "$0")/../alpine-backend"
    
    # Try to activate venv if it exists
    if [ -d "venv" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    fi
    
    # Check if we can import backend
    if python3 -c "import backend" 2>/dev/null; then
        python3 -m backend.migrations.add_indexes
    else
        echo "⚠️  Cannot import backend module"
        echo "Please ensure:"
        echo "  1. Virtual environment is activated"
        echo "  2. Dependencies are installed (pip install -r requirements.txt)"
        echo "  3. PYTHONPATH includes alpine-backend directory"
        echo ""
        echo "Alternative: Run migration via Docker:"
        echo "  docker-compose exec backend python -m backend.migrations.add_indexes"
        exit 1
    fi
fi

echo ""
echo "✅ Migration complete!"

