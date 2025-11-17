#!/bin/bash
# Wrapper script for Copilot CLI that automatically includes Rules/ directory
# Usage: ./scripts/agentic/copilot-with-rules.sh "your command"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Check if copilot is installed (try both copilot and github-copilot-cli)
if command -v copilot &> /dev/null; then
    COPILOT_CMD="copilot"
elif command -v github-copilot-cli &> /dev/null; then
    COPILOT_CMD="github-copilot-cli"
else
    echo "❌ Error: GitHub Copilot CLI not found"
    echo "   Install with: npm install -g @githubnext/github-copilot-cli"
    echo "   Then create alias: ln -sf github-copilot-cli copilot (in npm bin directory)"
    exit 1
fi

# Base rules context
RULES_CONTEXT="following all rules in Rules/ directory. 
Reference Rules/04_DEPLOYMENT.md for deployments, 
Rules/02_CODE_QUALITY.md for refactoring, 
Rules/01_DEVELOPMENT.md for development practices,
and Rules/35_AGENTIC_FEATURES.md for agentic workflows."

# Auto-detect context and add relevant rules
COMMAND_LOWER=$(echo "$*" | tr '[:upper:]' '[:lower:]')

if [[ "$COMMAND_LOWER" == *"deploy"* ]]; then
    RULES_CONTEXT="$RULES_CONTEXT Specifically follow all 11 safety gates 
    from Rules/04_DEPLOYMENT.md. Ensure entity separation per Rules/10_MONOREPO.md. 
    If any gate fails, rollback automatically."
fi

if [[ "$COMMAND_LOWER" == *"refactor"* ]] || [[ "$COMMAND_LOWER" == *"refactoring"* ]]; then
    RULES_CONTEXT="$RULES_CONTEXT Follow Rules/02_CODE_QUALITY.md for 
    refactoring guidelines. Functions over 50 lines must be broken down. 
    Maintain 95% test coverage per Rules/03_TESTING.md."
fi

if [[ "$COMMAND_LOWER" == *"test"* ]] || [[ "$COMMAND_LOWER" == *"testing"* ]]; then
    RULES_CONTEXT="$RULES_CONTEXT Follow Rules/03_TESTING.md. 
    Ensure 95% coverage minimum. All tests must pass."
fi

if [[ "$COMMAND_LOWER" == *"security"* ]] || [[ "$COMMAND_LOWER" == *"secret"* ]]; then
    RULES_CONTEXT="$RULES_CONTEXT Follow Rules/07_SECURITY.md strictly. 
    Never commit secrets. Use AWS Secrets Manager for production."
fi

if [[ "$COMMAND_LOWER" == *"argo"* ]] && [[ "$COMMAND_LOWER" != *"alpine"* ]]; then
    RULES_CONTEXT="$RULES_CONTEXT This is Argo Capital work. 
    Follow Rules/12A_ARGO_BACKEND.md. Maintain entity separation per Rules/10_MONOREPO.md."
fi

if [[ "$COMMAND_LOWER" == *"alpine"* ]]; then
    RULES_CONTEXT="$RULES_CONTEXT This is Alpine Analytics work. 
    Follow Rules/11_FRONTEND.md and Rules/12B_ALPINE_BACKEND.md. 
    Maintain entity separation per Rules/10_MONOREPO.md."
fi

# Execute copilot with rules context
FULL_COMMAND="$* $RULES_CONTEXT"

echo "🤖 Executing agentic command with automatic rule enforcement..."
echo ""

# Run copilot command using what-the-shell for general commands
$COPILOT_CMD what-the-shell "$FULL_COMMAND"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Agentic operation completed successfully"
else
    echo ""
    echo "❌ Agentic operation failed (exit code: $EXIT_CODE)"
    echo "   Check logs above for details"
    exit $EXIT_CODE
fi

