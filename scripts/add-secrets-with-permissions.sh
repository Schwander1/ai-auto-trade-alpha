#!/bin/bash
# Complete workflow: Setup permissions and add secrets

set -e

echo "🚀 Complete Secrets Setup Workflow"
echo "==================================="
echo ""

# Step 1: Setup IAM permissions
echo "Step 1: Setting up IAM permissions..."
echo "--------------------------------------"
if ./scripts/setup-secrets-permissions.sh; then
    echo ""
    echo "✅ Permissions setup complete"
    echo ""
else
    echo ""
    echo "⚠️  Permissions setup had issues, but continuing..."
    echo ""
fi

# Wait a moment for permissions to propagate
echo "⏳ Waiting 5 seconds for permissions to propagate..."
sleep 5

# Step 2: Add secrets
echo ""
echo "Step 2: Adding secrets to AWS Secrets Manager..."
echo "------------------------------------------------"
python scripts/add-additional-secrets.py

echo ""
echo "✅ Complete workflow finished!"
echo ""
echo "📋 Verification:"
echo "   Run: python scripts/verify-secrets-health.py"

