#!/bin/bash
# Update IAM Policy to include new secret prefixes (argo-capital, alpine-analytics)
# This script updates the existing policy to support all three prefixes

set -e

IAM_USER="argo-compliance-backup"
POLICY_NAME="ArgoAlpineSecretsManagerAccess"
POLICY_FILE="$(dirname "$0")/iam-policy-secrets-manager.json"

echo "🔐 Updating IAM Policy for New Secret Prefixes"
echo "==============================================="
echo ""
echo "IAM User: $IAM_USER"
echo "Policy Name: $POLICY_NAME"
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

echo "📋 Step 1: Finding existing policy..."
echo ""

# Get the policy ARN
POLICY_ARN=$(aws iam list-policies --query "Policies[?PolicyName=='$POLICY_NAME'].Arn" --output text 2>/dev/null || echo "")

if [ -z "$POLICY_ARN" ]; then
    echo "❌ Policy '$POLICY_NAME' not found"
    echo ""
    echo "Creating new policy..."
    POLICY_OUTPUT=$(aws iam create-policy \
        --policy-name "$POLICY_NAME" \
        --policy-document "file://$POLICY_FILE" \
        --description "Allows access to Argo Capital, Alpine Analytics, and legacy Argo-Alpine secrets in AWS Secrets Manager" \
        2>&1)
    
    POLICY_ARN=$(echo "$POLICY_OUTPUT" | grep -o '"Arn": "[^"]*"' | head -1 | sed 's/"Arn": "//;s/"//' || echo "")
    
    if [ -z "$POLICY_ARN" ]; then
        echo "❌ Failed to create policy"
        exit 1
    fi
    
    echo "✅ Created new policy: $POLICY_ARN"
else
    echo "✅ Found existing policy: $POLICY_ARN"
fi

echo ""
echo "📋 Step 2: Creating new policy version with updated permissions..."
echo ""

# Create new policy version
POLICY_VERSION_OUTPUT=$(aws iam create-policy-version \
    --policy-arn "$POLICY_ARN" \
    --policy-document "file://$POLICY_FILE" \
    --set-as-default \
    2>&1)

if echo "$POLICY_VERSION_OUTPUT" | grep -q "VersionId"; then
    VERSION_ID=$(echo "$POLICY_VERSION_OUTPUT" | grep -o '"VersionId": "[^"]*"' | head -1 | sed 's/"VersionId": "//;s/"//' || echo "")
    echo "✅ Created new policy version: $VERSION_ID"
    echo "✅ Set as default version"
else
    echo "⚠️  Policy version creation output:"
    echo "$POLICY_VERSION_OUTPUT"
    
    # Check if it's a limit error (max 5 versions)
    if echo "$POLICY_VERSION_OUTPUT" | grep -q "LimitExceeded"; then
        echo ""
        echo "⚠️  Policy has maximum versions (5). Deleting oldest non-default version..."
        
        # List all versions
        OLD_VERSIONS=$(aws iam list-policy-versions --policy-arn "$POLICY_ARN" --query "Versions[?IsDefaultVersion==\`false\`].VersionId" --output text 2>&1)
        
        if [ -n "$OLD_VERSIONS" ]; then
            OLDEST_VERSION=$(echo "$OLD_VERSIONS" | awk '{print $1}')
            echo "   Deleting version: $OLDEST_VERSION"
            aws iam delete-policy-version --policy-arn "$POLICY_ARN" --version-id "$OLDEST_VERSION" 2>&1 || true
            sleep 2
            
            # Try again
            POLICY_VERSION_OUTPUT=$(aws iam create-policy-version \
                --policy-arn "$POLICY_ARN" \
                --policy-document "file://$POLICY_FILE" \
                --set-as-default \
                2>&1)
            
            if echo "$POLICY_VERSION_OUTPUT" | grep -q "VersionId"; then
                VERSION_ID=$(echo "$POLICY_VERSION_OUTPUT" | grep -o '"VersionId": "[^"]*"' | head -1 | sed 's/"VersionId": "//;s/"//' || echo "")
                echo "✅ Created new policy version: $VERSION_ID"
            else
                echo "❌ Failed to create policy version after cleanup"
                echo "   Output: $POLICY_VERSION_OUTPUT"
                exit 1
            fi
        else
            echo "❌ No non-default versions to delete"
            exit 1
        fi
    else
        echo "❌ Failed to create policy version"
        exit 1
    fi
fi

echo ""
echo "📋 Step 3: Verifying policy is attached to user..."
echo ""

# Check if policy is attached
ATTACHED=$(aws iam list-attached-user-policies --user-name "$IAM_USER" --query "AttachedPolicies[?PolicyArn=='$POLICY_ARN']" --output text 2>&1 || echo "")

if [ -z "$ATTACHED" ]; then
    echo "⚠️  Policy is not attached to user. Attaching now..."
    if aws iam attach-user-policy --user-name "$IAM_USER" --policy-arn "$POLICY_ARN" 2>&1; then
        echo "✅ Policy attached successfully"
    else
        echo "❌ Failed to attach policy"
        echo ""
        echo "Please attach manually:"
        echo "1. Go to IAM Console → Users → $IAM_USER"
        echo "2. Click 'Add permissions' → 'Attach policies directly'"
        echo "3. Search for: $POLICY_NAME"
        echo "4. Select it and click 'Add permissions'"
        exit 1
    fi
else
    echo "✅ Policy is already attached to user"
fi

echo ""
echo "✅ IAM Policy Update Complete!"
echo ""
echo "📋 Updated Policy Includes:"
echo "   ✅ argo-capital/* (new Argo prefix)"
echo "   ✅ alpine-analytics/* (new Alpine prefix)"
echo "   ✅ argo-alpine/* (legacy prefix - backward compatibility)"
echo ""
echo "⏳ Waiting 10 seconds for permissions to propagate..."
sleep 10

echo ""
echo "📋 Step 4: Testing permissions..."
echo ""

# Test access to new prefixes
echo "Testing argo-capital prefix access..."
if aws secretsmanager list-secrets --filters Key=name,Values=argo-capital --max-results 1 > /dev/null 2>&1; then
    echo "✅ argo-capital prefix: Access granted"
else
    echo "⚠️  argo-capital prefix: May need more time to propagate (or no secrets exist yet)"
fi

echo "Testing alpine-analytics prefix access..."
if aws secretsmanager list-secrets --filters Key=name,Values=alpine-analytics --max-results 1 > /dev/null 2>&1; then
    echo "✅ alpine-analytics prefix: Access granted"
else
    echo "⚠️  alpine-analytics prefix: May need more time to propagate (or no secrets exist yet)"
fi

echo "Testing argo-alpine prefix access..."
if aws secretsmanager list-secrets --filters Key=name,Values=argo-alpine --max-results 1 > /dev/null 2>&1; then
    echo "✅ argo-alpine prefix: Access granted"
else
    echo "⚠️  argo-alpine prefix: May need more time to propagate"
fi

echo ""
echo "✅ IAM Policy Update Complete!"
echo ""
echo "📝 Next Steps:"
echo "   1. Permissions should be active now (may take up to 60 seconds to fully propagate)"
echo "   2. Test on production server to verify access"
echo "   3. System will now use new prefixes when available"
echo ""

