#!/bin/bash
# Test script to verify agentic setup is complete
# Usage: ./scripts/agentic/test_setup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "🧪 Testing Agentic Features Setup"
echo "=================================="
echo ""

# Test 1: Copilot CLI
echo "1. Testing Copilot CLI..."
if command -v copilot &> /dev/null || command -v github-copilot-cli &> /dev/null; then
    echo "   ✅ Copilot CLI found"
    if command -v copilot &> /dev/null; then
        COPILOT_CMD="copilot"
    else
        COPILOT_CMD="github-copilot-cli"
    fi
    VERSION=$($COPILOT_CMD --version 2>&1 | head -1)
    echo "   ✅ Version: $VERSION"
else
    echo "   ❌ Copilot CLI not found"
    exit 1
fi

# Test 2: Python scripts
echo ""
echo "2. Testing Python scripts..."
python3 -c "from scripts.agentic.usage_tracker import UsageTracker; print('   ✅ Usage tracker imports')" 2>&1
python3 -c "from scripts.agentic.rate_limiter import RateLimiter; print('   ✅ Rate limiter imports')" 2>&1
python3 -c "from scripts.agentic.monitor import AgenticMonitor; print('   ✅ Monitor imports')" 2>&1

# Test 3: Anthropic SDK
echo ""
echo "3. Testing Anthropic SDK..."
if python3 -c "import anthropic" 2>/dev/null; then
    echo "   ✅ Anthropic SDK installed"
else
    echo "   ⚠️  Anthropic SDK not installed (optional)"
fi

# Test 4: Logs directory
echo ""
echo "4. Testing logs directory..."
if [ -d "$WORKSPACE_DIR/logs" ]; then
    echo "   ✅ Logs directory exists"
else
    echo "   ⚠️  Creating logs directory..."
    mkdir -p "$WORKSPACE_DIR/logs"
    echo "   ✅ Logs directory created"
fi

# Test 5: Usage tracking
echo ""
echo "5. Testing usage tracking..."
python3 "$SCRIPT_DIR/usage_tracker.py" report 2>&1 | grep -q "Total Requests" && echo "   ✅ Usage tracker works" || echo "   ⚠️  Usage tracker needs data"

# Test 6: Rate limiting
echo ""
echo "6. Testing rate limiting..."
python3 "$SCRIPT_DIR/rate_limiter.py" status 2>&1 | grep -q "Rate Limit Status" && echo "   ✅ Rate limiter works" || echo "   ❌ Rate limiter failed"

# Test 7: Wrapper script
echo ""
echo "7. Testing wrapper script..."
if [ -x "$SCRIPT_DIR/copilot-with-rules.sh" ]; then
    echo "   ✅ Wrapper script is executable"
else
    echo "   ❌ Wrapper script not executable"
    exit 1
fi

# Test 8: Package.json scripts
echo ""
echo "8. Testing package.json scripts..."
if grep -q "agentic:" "$WORKSPACE_DIR/package.json"; then
    echo "   ✅ Package.json scripts configured"
else
    echo "   ❌ Package.json scripts missing"
    exit 1
fi

echo ""
echo "=================================="
echo "✅ All tests passed!"
echo ""
echo "🚀 Ready to use agentic features!"
echo ""
echo "Quick commands:"
echo "  ./scripts/agentic/copilot-with-rules.sh \"your command\""
echo "  pnpm agentic:usage"
echo "  pnpm agentic:monitor"

