#!/bin/bash
# Test Coverage Analysis using Agentic Features
# Identifies test gaps and suggests test cases

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

TARGET_DIR="${1:-argo/argo/core}"

echo "🧪 Test Coverage Analysis: $TARGET_DIR"
echo "======================================="
echo ""

"${SCRIPT_DIR}/copilot-with-rules.sh" "Analyze test coverage in $TARGET_DIR. Identify functions with low or no test coverage. For each function, suggest specific test cases following Rules/03_TESTING.md. Focus on critical paths that need 95% coverage. Include unit tests, integration tests, and edge cases. Generate a prioritized list with specific test scenarios."

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Test coverage analysis completed"
    echo "📊 Analysis report saved to logs/test_coverage_analysis_$(date +%Y%m%d).txt"
else
    echo ""
    echo "❌ Test coverage analysis failed"
    exit $EXIT_CODE
fi

