#!/bin/bash
# Start Signal Generation Service
# Proper startup script with all environment setup

set -e

cd "$(dirname "$0")/.."

echo "🚀 Starting Argo Signal Generation Service"
echo "==========================================="

# Set PYTHONPATH
export PYTHONPATH="$(pwd)/argo"

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

