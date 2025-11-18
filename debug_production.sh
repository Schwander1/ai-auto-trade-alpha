#!/bin/bash
# Wrapper script for comprehensive production debugging
# Usage: ./debug_production.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/debug_production_comprehensive.py"

echo "🔍 Starting Comprehensive Production Debugging..."
echo ""

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Error: Debug script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed"
    exit 1
fi

# Check if required Python packages are available
if ! python3 -c "import requests" 2>/dev/null; then
    echo "⚠️  Warning: 'requests' package not found. Installing..."
    pip3 install requests 2>/dev/null || {
        echo "❌ Error: Failed to install 'requests' package"
        echo "   Please install it manually: pip3 install requests"
        exit 1
    }
fi

# Run the debug script
python3 "$PYTHON_SCRIPT" "$@"

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✅ Debugging completed successfully"
else
    echo "⚠️  Debugging completed with issues (exit code: $exit_code)"
fi

exit $exit_code

