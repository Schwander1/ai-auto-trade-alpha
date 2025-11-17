#!/bin/bash
# Template for agentic deployments
# Usage: ./scripts/agentic/templates/deployment-template.sh <project> <environment>

set -e

PROJECT="${1:-argo}"
ENVIRONMENT="${2:-production}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTIC_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORKSPACE_DIR="$(cd "${AGENTIC_DIR}/../.." && pwd)"

echo "🚀 Agentic Deployment: $PROJECT to $ENVIRONMENT"
echo ""

# Use copilot-with-rules wrapper
"${AGENTIC_DIR}/copilot-with-rules.sh" "Deploy $PROJECT to $ENVIRONMENT following:
1. All 11 safety gates from Rules/04_DEPLOYMENT.md
2. Entity separation from Rules/10_MONOREPO.md
3. Security rules from Rules/07_SECURITY.md
4. If any gate fails, rollback automatically using Rules/04_DEPLOYMENT.md rollback procedures
5. Post-deployment: Run Level 3 health check and verify 100% health"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Deployment completed successfully"
else
    echo ""
    echo "❌ Deployment failed - check logs above"
    exit $EXIT_CODE
fi

