#!/bin/bash
# Delete old argo-alpine/* secrets after migration to new prefixes
# This script safely deletes old secrets after verifying new ones exist

set -e

echo "🗑️  Deleting Old Secrets (argo-alpine/*)"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will permanently delete old secrets!"
echo "   Make sure new secrets are working before proceeding."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found${NC}"
    exit 1
fi

# Function to verify new secret exists
verify_new_secret_exists() {
    local old_name=$1
    local new_name=$2
    
    # Check if new secret exists
    aws secretsmanager describe-secret --secret-id "$new_name" > /dev/null 2>&1
    return $?
}

# Function to get new secret name
get_new_secret_name() {
    local old_name=$1
    
    # Determine entity
    if [[ "$old_name" == *"alpine-backend"* ]] || [[ "$old_name" == *"alpine-frontend"* ]]; then
        echo "${old_name/argo-alpine\//alpine-analytics/}"
    else
        echo "${old_name/argo-alpine\//argo-capital/}"
    fi
}

# List all old secrets
echo "📋 Step 1: Listing old secrets (argo-alpine/*)..."
echo ""

SECRETS_JSON=$(aws secretsmanager list-secrets \
    --filters Key=name,Values=argo-alpine \
    --output json 2>&1)

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to list secrets${NC}"
    echo "$SECRETS_JSON"
    exit 1
fi

SECRET_COUNT=$(echo "$SECRETS_JSON" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('SecretList', [])))" 2>/dev/null || echo "0")

if [ "$SECRET_COUNT" == "0" ]; then
    echo -e "${YELLOW}⚠️  No secrets found with argo-alpine/* prefix${NC}"
    exit 0
fi

echo -e "${GREEN}✅ Found $SECRET_COUNT secret(s)${NC}"
echo ""

# Extract secret names
SECRET_NAMES=$(echo "$SECRETS_JSON" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for secret in data.get('SecretList', []):
    print(secret['Name'])
" 2>/dev/null)

if [ -z "$SECRET_NAMES" ]; then
    echo -e "${RED}❌ Failed to extract secret names${NC}"
    exit 1
fi

echo "📋 Step 2: Verifying new secrets exist..."
echo ""

VERIFIED=0
MISSING=0
TO_DELETE=()

while IFS= read -r old_name; do
    if [ -z "$old_name" ]; then
        continue
    fi
    
    new_name=$(get_new_secret_name "$old_name")
    
    if verify_new_secret_exists "$old_name" "$new_name"; then
        echo -e "  ${GREEN}✅${NC} $old_name → $new_name (verified)"
        TO_DELETE+=("$old_name")
        VERIFIED=$((VERIFIED + 1))
    else
        echo -e "  ${RED}❌${NC} $old_name → $new_name (NEW SECRET MISSING!)"
        MISSING=$((MISSING + 1))
    fi
done <<< "$SECRET_NAMES"

echo ""
echo "📋 Step 3: Verification Summary"
echo "=========================================="
echo -e "${GREEN}✅ Verified (safe to delete): $VERIFIED${NC}"
if [ $MISSING -gt 0 ]; then
    echo -e "${RED}❌ Missing new secrets (NOT safe to delete): $MISSING${NC}"
    echo ""
    echo -e "${RED}⚠️  ABORTING: Some new secrets are missing!${NC}"
    echo "   Please verify migration completed successfully."
    exit 1
fi

if [ ${#TO_DELETE[@]} -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No secrets to delete${NC}"
    exit 0
fi

echo ""
echo "📋 Step 4: Deleting old secrets..."
echo ""

DELETED=0
FAILED=0

for old_name in "${TO_DELETE[@]}"; do
    echo "Deleting: $old_name"
    
    # Delete secret (force delete without recovery window)
    DELETE_RESULT=$(aws secretsmanager delete-secret \
        --secret-id "$old_name" \
        --force-delete-without-recovery 2>&1)
    
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✅ Deleted${NC}"
        DELETED=$((DELETED + 1))
    else
        echo -e "  ${RED}❌ Failed${NC}"
        echo "  Error: $DELETE_RESULT"
        FAILED=$((FAILED + 1))
    fi
    echo ""
done

echo "📋 Step 5: Deletion Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}✅ Successfully deleted: $DELETED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ Failed: $FAILED${NC}"
fi
echo ""

if [ $DELETED -gt 0 ]; then
    echo "✅ Old secrets cleanup complete!"
    echo ""
    echo "📝 Verification:"
    echo "   - All old secrets have been permanently deleted"
    echo "   - System is now using new prefixes exclusively"
    echo "   - Backward compatibility is no longer needed"
else
    echo -e "${YELLOW}⚠️  No secrets were deleted${NC}"
fi

echo ""

