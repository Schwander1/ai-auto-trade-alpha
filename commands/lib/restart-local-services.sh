#!/bin/bash
# Restart local services
set -e

PROJECT="${1:-all}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔄 Restarting services..."
echo ""

# Stop first
"${SCRIPT_DIR}/stop-local-services.sh" "$PROJECT"

echo ""
sleep 2

# Start again
"${SCRIPT_DIR}/start-local-services.sh" "$PROJECT"

