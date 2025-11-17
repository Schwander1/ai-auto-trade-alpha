#!/bin/bash
# Template for agentic troubleshooting
# Usage: ./scripts/agentic/templates/troubleshooting-template.sh <issue_description>

set -e

ISSUE="${1}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTIC_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [ -z "$ISSUE" ]; then
    echo "❌ Error: Issue description required"
    echo "Usage: $0 <issue_description>"
    exit 1
fi

echo "🔍 Agentic Troubleshooting: $ISSUE"
echo ""

# Use copilot-with-rules wrapper
"${AGENTIC_DIR}/copilot-with-rules.sh" "Troubleshoot: $ISSUE

Follow these steps:
1. Check logs and error messages
2. Review Rules/14_MONITORING_OBSERVABILITY.md for monitoring guidelines
3. Check health endpoints per Rules/04_DEPLOYMENT.md
4. Review Rules/29_ERROR_HANDLING.md for error handling patterns
5. Suggest fixes based on our troubleshooting guide
6. If deployment issue, check Rules/04_DEPLOYMENT.md rollback procedures"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Troubleshooting completed"
else
    echo ""
    echo "❌ Troubleshooting failed - check logs above"
    exit $EXIT_CODE
fi

