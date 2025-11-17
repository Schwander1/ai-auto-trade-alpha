#!/bin/bash
# Automated Troubleshooting Script using Agentic Features
# Diagnoses common issues and suggests fixes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

ISSUE_TYPE="${1:-health_check}"

echo "🔍 Automated Troubleshooting: $ISSUE_TYPE"
echo "=========================================="
echo ""

case "$ISSUE_TYPE" in
    health_check)
        "${SCRIPT_DIR}/copilot-with-rules.sh" "Health checks are failing. Check logs in argo/logs/, identify root cause, and suggest fixes based on Rules/29_ERROR_HANDLING.md and docs/SystemDocs/TROUBLESHOOTING_RECOVERY_COMPLETE_GUIDE.md. Provide specific steps to resolve."
        ;;
    api_failure)
        "${SCRIPT_DIR}/copilot-with-rules.sh" "Data source API is returning errors (e.g., 401, 429, 500). Diagnose the issue, check API key configuration in AWS Secrets Manager and config.json, verify rate limits, and suggest fixes following Rules/07_SECURITY.md and Rules/29_ERROR_HANDLING.md."
        ;;
    trading_paused)
        "${SCRIPT_DIR}/copilot-with-rules.sh" "Trading is paused. Check why _trading_paused flag is set, review risk limits in config.json, check daily loss limits, verify account status, and suggest fixes based on Rules/13_TRADING_OPERATIONS.md and Rules/14_RISK_MANAGEMENT.md."
        ;;
    signal_generation)
        "${SCRIPT_DIR}/copilot-with-rules.sh" "Signal generation is failing or producing low-quality signals. Check data source connectivity, consensus engine configuration, regime detection, and suggest fixes based on Rules/12A_ARGO_BACKEND.md and docs/SystemDocs/SIGNAL_GENERATION_COMPLETE_GUIDE.md."
        ;;
    deployment)
        "${SCRIPT_DIR}/copilot-with-rules.sh" "Deployment failed. Check deployment logs, verify all 11 safety gates, check health checks, review rollback procedures, and suggest fixes based on Rules/04_DEPLOYMENT.md and docs/SystemDocs/MONOREPO_DEPLOYMENT_GUIDE.md."
        ;;
    *)
        echo "Unknown issue type: $ISSUE_TYPE"
        echo "Available types: health_check, api_failure, trading_paused, signal_generation, deployment"
        exit 1
        ;;
esac

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Troubleshooting analysis completed"
    echo "📋 Review suggestions above and apply fixes"
else
    echo ""
    echo "❌ Troubleshooting failed - check logs"
    exit $EXIT_CODE
fi

