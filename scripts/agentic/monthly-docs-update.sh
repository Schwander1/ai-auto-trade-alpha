#!/bin/bash
# Monthly Documentation Update using Agentic Features
# Reviews and updates documentation to match current codebase

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "📚 Monthly Documentation Update"
echo "==============================="
echo ""

"${SCRIPT_DIR}/copilot-with-rules.sh" "Review docs/SystemDocs/ and compare with current codebase. Update any outdated information, especially in SIGNAL_GENERATION_COMPLETE_GUIDE.md, RISK_MANAGEMENT_COMPLETE_GUIDE.md, TRADING_EXECUTION_COMPLETE_GUIDE.md, and MONOREPO_DEPLOYMENT_GUIDE.md. Ensure all code examples work, file paths are correct, and version numbers are updated. Generate a summary of changes made."

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Documentation update completed"
    echo "📊 Update summary saved to logs/docs_update_$(date +%Y%m%d).txt"
else
    echo ""
    echo "❌ Documentation update failed"
    exit $EXIT_CODE
fi

