#!/bin/bash
# Weekly Code Quality Review using Agentic Features
# Reviews code for violations and generates prioritized list of issues

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

TARGET_DIR="${1:-argo/argo/core}"

echo "📋 Weekly Code Quality Review: $TARGET_DIR"
echo "==========================================="
echo ""

"${SCRIPT_DIR}/copilot-with-rules.sh" "Review code in $TARGET_DIR for violations of Rules/02_CODE_QUALITY.md. Check for: functions over 50 lines, magic numbers, complex conditionals, code duplication, naming violations, missing type hints, missing docstrings, and missing error handling. Generate a prioritized list of issues to fix with specific file paths and line numbers. Focus on critical paths first."

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Code quality review completed"
    echo "📊 Review report saved to logs/code_quality_review_$(date +%Y%m%d).txt"
else
    echo ""
    echo "❌ Code quality review failed"
    exit $EXIT_CODE
fi

