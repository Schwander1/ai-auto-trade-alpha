#!/bin/bash
# Template for agentic refactoring
# Usage: ./scripts/agentic/templates/refactoring-template.sh <target> [scope]

set -e

TARGET="${1}"
SCOPE="${2:-all}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTIC_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [ -z "$TARGET" ]; then
    echo "❌ Error: Target required"
    echo "Usage: $0 <target> [scope]"
    echo "  target: File or directory to refactor"
    echo "  scope: 'all' (default) or specific scope"
    exit 1
fi

echo "🔧 Agentic Refactoring: $TARGET"
echo ""

# Use copilot-with-rules wrapper
"${AGENTIC_DIR}/copilot-with-rules.sh" "Refactor $TARGET ($SCOPE scope) following:
1. Rules/02_CODE_QUALITY.md for refactoring guidelines
2. Break functions over 50 lines into smaller functions
3. Maintain 95% test coverage per Rules/03_TESTING.md
4. Follow all 25+ rules in Rules/ directory
5. Ensure entity separation per Rules/10_MONOREPO.md
6. Update tests and documentation"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Refactoring completed successfully"
else
    echo ""
    echo "❌ Refactoring failed - check logs above"
    exit $EXIT_CODE
fi

