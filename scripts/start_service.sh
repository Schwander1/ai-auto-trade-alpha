#!/bin/bash
# Start Signal Generation Service
# Proper startup script with all environment setup

set -e

cd "$(dirname "$0")/.."

# Source dependency checking utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/lib/wait-for-dependencies.sh" ]; then
    source "$SCRIPT_DIR/lib/wait-for-dependencies.sh"
else
    echo "⚠️  Warning: Dependency checking utilities not found"
fi

echo "🚀 Starting Argo Signal Generation Service"
echo "==========================================="

# Wait for dependencies before starting
if command -v wait_for_redis &> /dev/null; then
    wait_for_redis "Redis" || {
        echo "⚠️  Warning: Redis not available, continuing anyway..."
    }
fi

if command -v wait_for_database &> /dev/null; then
    wait_for_database "" "Database" || {
        echo "⚠️  Warning: Database not available, continuing anyway..."
    }
fi

# Set PYTHONPATH
export PYTHONPATH="$(pwd)/argo"

# Enable 24/7 mode for continuous signal generation
export ARGO_24_7_MODE=true

# Create log directory
mkdir -p argo/logs

# Log file
LOG_FILE="argo/logs/service_$(date +%Y%m%d_%H%M%S).log"

echo "📝 Log file: $LOG_FILE"
echo "🔧 PYTHONPATH: $PYTHONPATH"
echo ""

# Start service
echo "🚀 Starting service..."
python3 -m argo.core.signal_generation_service 2>&1 | tee "$LOG_FILE"

