#!/bin/bash
# Setup IAM permissions for AWS Secrets Manager
# This script helps you attach the necessary permissions to your IAM user

set -e

IAM_USER="argo-compliance-backup"
POLICY_NAME="ArgoAlpineSecretsManagerAccess"
POLICY_FILE="$(dirname "$0")/iam-policy-secrets-manager.json"

echo "🔐 Setting up IAM permissions for AWS Secrets Manager"
echo "======================================================"
echo ""
echo "IAM User: $IAM_USER"
echo "Policy File: $POLICY_FILE"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed"
    echo "   Install it with: pip install awscli"
    exit 1
fi

# Check if policy file exists
if [ ! -f "$POLICY_FILE" ]; then
    echo "❌ Policy file not found: $POLICY_FILE"
    exit 1
fi

echo "📋 Step 1: Creating IAM policy..."
echo ""

# Create the policy
POLICY_OUTPUT=$(aws iam create-policy \
    --policy-name "$POLICY_NAME" \
    --policy-document "file://$POLICY_FILE" \
    --description "Allows access to Argo-Alpine secrets in AWS Secrets Manager" \
    2>&1)

# Extract ARN from output (works on both Linux and macOS)
POLICY_ARN=$(echo "$POLICY_OUTPUT" | grep -o '"Arn": "[^"]*"' | head -1 | sed 's/"Arn": "//;s/"//' || echo "")

if [ -z "$POLICY_ARN" ]; then
    # Policy might already exist, try to get it
    echo "⚠️  Policy might already exist, checking..."
    POLICY_ARN=$(aws iam list-policies --query "Policies[?PolicyName=='$POLICY_NAME'].Arn" --output text 2>/dev/null || echo "")
    
    if [ -z "$POLICY_ARN" ]; then
        echo "❌ Failed to create or find policy"
        echo ""
        echo "Please create the policy manually:"
        echo "1. Go to IAM Console → Policies → Create Policy"
        echo "2. Use the JSON from: $POLICY_FILE"
        echo "3. Name it: $POLICY_NAME"
        exit 1
    else
        echo "✅ Found existing policy: $POLICY_ARN"
    fi
else
    echo "✅ Created policy: $POLICY_ARN"
fi

echo ""
echo "📋 Step 2: Attaching policy to user..."
echo ""

# Attach policy to user
if aws iam attach-user-policy \
    --user-name "$IAM_USER" \
    --policy-arn "$POLICY_ARN" 2>&1; then
    echo "✅ Policy attached successfully!"
else
    echo "⚠️  Failed to attach policy (might already be attached)"
    echo ""
    echo "Checking if policy is already attached..."
    if aws iam list-attached-user-policies --user-name "$IAM_USER" --query "AttachedPolicies[?PolicyArn=='$POLICY_ARN']" --output text | grep -q "$POLICY_ARN"; then
        echo "✅ Policy is already attached to user"
    else
        echo "❌ Policy attachment failed"
        echo ""
        echo "Please attach the policy manually:"
        echo "1. Go to IAM Console → Users → $IAM_USER"
        echo "2. Click 'Add permissions' → 'Attach policies directly'"
        echo "3. Search for: $POLICY_NAME"
        echo "4. Select it and click 'Add permissions'"
        exit 1
    fi
fi

echo ""
echo "✅ IAM permissions setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Wait a few seconds for permissions to propagate"
echo "   2. Run: python scripts/add-additional-secrets.py"
echo ""

