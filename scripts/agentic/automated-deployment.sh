#!/bin/bash
# Automated Deployment Script using Agentic Features
# This script automates the deployment process with all 11 safety gates

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

PROJECT="${1:-argo}"
ENVIRONMENT="${2:-production}"

echo "🚀 Automated Agentic Deployment: $PROJECT to $ENVIRONMENT"
echo "========================================================"
echo ""

# Use the agentic wrapper for deployment
"${SCRIPT_DIR}/copilot-with-rules.sh" "Deploy $PROJECT to $ENVIRONMENT following all 11 safety gates from Rules/04_DEPLOYMENT.md. Execute: 1) Pre-deployment validation, 2) Health checks, 3) Security audit, 4) Backup, 5) Blue-green deployment, 6) Post-deployment health checks, 7) Rollback if any gate fails. Follow Rules/10_MONOREPO.md for entity separation and Rules/07_SECURITY.md for security."

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Automated deployment completed successfully"
    echo "📊 Deployment metrics logged to logs/agentic_monitor.jsonl"
else
    echo ""
    echo "❌ Automated deployment failed - check logs above"
    echo "🔄 Automatic rollback initiated if configured"
    exit $EXIT_CODE
fi

