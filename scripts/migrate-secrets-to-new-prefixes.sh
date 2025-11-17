#!/bin/bash
# Migrate secrets from argo-alpine/* to new entity-specific prefixes
# argo-alpine/* → argo-capital/* (for Argo secrets)
# argo-alpine/* → alpine-analytics/* (for Alpine secrets)

set -e

echo "🔐 Migrating Secrets to New Prefixes"
echo "====================================="
echo ""
echo "This script will:"
echo "  1. List all secrets with prefix: argo-alpine/*"
echo "  2. Identify which belong to Argo vs Alpine"
echo "  3. Create new secrets with appropriate prefixes"
echo "  4. Copy secret values"
echo "  5. Verify migration"
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

# Function to determine if secret belongs to Argo or Alpine
determine_entity() {
    local secret_name=$1
    
    # Check path first - alpine-backend/ or alpine-frontend/ = Alpine
    if [[ "$secret_name" == *"alpine-backend"* ]] || \
       [[ "$secret_name" == *"alpine-frontend"* ]]; then
        echo "alpine"
    # Argo secrets typically contain: alpaca, trading, argo-specific services
    elif [[ "$secret_name" == *"alpaca"* ]] || \
         [[ "$secret_name" == *"trading"* ]] || \
         [[ "$secret_name" == *"argo/"* ]] || \
         [[ "$secret_name" == *"anthropic"* ]] || \
         [[ "$secret_name" == *"perplexity"* ]] || \
         [[ "$secret_name" == *"sonar"* ]] || \
         [[ "$secret_name" == *"xai"* ]] || \
         [[ "$secret_name" == *"alphavantage"* ]] || \
         [[ "$secret_name" == *"tradervue"* ]] || \
         [[ "$secret_name" == *"figma"* ]] || \
         [[ "$secret_name" == *"massive"* ]]; then
        echo "argo"
    # Alpine secrets typically contain: stripe, jwt, database, alpine-specific services
    elif [[ "$secret_name" == *"stripe"* ]] || \
         [[ "$secret_name" == *"jwt"* ]] || \
         [[ "$secret_name" == *"database"* ]] || \
         [[ "$secret_name" == *"postgres"* ]] || \
         [[ "$secret_name" == *"redis"* ]] || \
         [[ "$secret_name" == *"nextauth"* ]] || \
         [[ "$secret_name" == *"domain"* ]] || \
         [[ "$secret_name" == *"frontend-url"* ]]; then
        echo "alpine"
    else
        # Default: check if it's in argo/ path
        if [[ "$secret_name" == *"/argo/"* ]]; then
            echo "argo"
        else
            echo "alpine"
        fi
    fi
}

# Function to get new secret name
get_new_secret_name() {
    local old_name=$1
    local entity=$2
    
    # Remove argo-alpine prefix and add new prefix
    new_name="${old_name#argo-alpine/}"
    
    if [ "$entity" == "argo" ]; then
        echo "argo-capital/$new_name"
    else
        echo "alpine-analytics/$new_name"
    fi
}

# List all secrets with argo-alpine prefix
echo "📋 Step 1: Listing secrets with argo-alpine/* prefix..."
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

echo "📋 Step 2: Analyzing secrets..."
echo ""

# Create migration plan
MIGRATION_PLAN=()
while IFS= read -r secret_name; do
    if [ -z "$secret_name" ]; then
        continue
    fi
    
    entity=$(determine_entity "$secret_name")
    new_name=$(get_new_secret_name "$secret_name" "$entity")
    
    MIGRATION_PLAN+=("$secret_name|$new_name|$entity")
    
    echo "  $secret_name"
    echo "    → $new_name ($entity)"
    echo ""
done <<< "$SECRET_NAMES"

echo "📋 Step 3: Migrating secrets..."
echo ""

MIGRATED=0
FAILED=0

for migration in "${MIGRATION_PLAN[@]}"; do
    IFS='|' read -r old_name new_name entity <<< "$migration"
    
    echo "Migrating: $old_name → $new_name"
    
    # Get secret value
    SECRET_VALUE=$(aws secretsmanager get-secret-value \
        --secret-id "$old_name" \
        --query 'SecretString' \
        --output text 2>&1)
    
    if [ $? -ne 0 ]; then
        echo -e "  ${RED}❌ Failed to get secret value${NC}"
        echo "  Error: $SECRET_VALUE"
        FAILED=$((FAILED + 1))
        echo ""
        continue
    fi
    
    # Check if new secret already exists
    EXISTS=$(aws secretsmanager describe-secret \
        --secret-id "$new_name" \
        --query 'ARN' \
        --output text 2>&1)
    
    if [ $? -eq 0 ] && [ -n "$EXISTS" ]; then
        echo -e "  ${YELLOW}⚠️  Secret already exists, updating...${NC}"
        
        # Update existing secret
        UPDATE_RESULT=$(aws secretsmanager put-secret-value \
            --secret-id "$new_name" \
            --secret-string "$SECRET_VALUE" 2>&1)
        
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✅ Updated existing secret${NC}"
            MIGRATED=$((MIGRATED + 1))
        else
            echo -e "  ${RED}❌ Failed to update secret${NC}"
            echo "  Error: $UPDATE_RESULT"
            FAILED=$((FAILED + 1))
        fi
    else
        # Create new secret
        CREATE_RESULT=$(aws secretsmanager create-secret \
            --name "$new_name" \
            --secret-string "$SECRET_VALUE" \
            --description "Migrated from $old_name" 2>&1)
        
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✅ Created new secret${NC}"
            MIGRATED=$((MIGRATED + 1))
        else
            echo -e "  ${RED}❌ Failed to create secret${NC}"
            echo "  Error: $CREATE_RESULT"
            FAILED=$((FAILED + 1))
        fi
    fi
    
    echo ""
done

echo "📋 Step 4: Migration Summary"
echo "====================================="
echo ""
echo -e "${GREEN}✅ Successfully migrated: $MIGRATED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ Failed: $FAILED${NC}"
fi
echo ""

if [ $MIGRATED -gt 0 ]; then
    echo "✅ Migration complete!"
    echo ""
    echo "📝 Next steps:"
    echo "  1. Verify secrets are accessible with new prefixes"
    echo "  2. Test system functionality"
    echo "  3. After verification, you can optionally delete old secrets:"
    echo "     aws secretsmanager delete-secret --secret-id <old-secret-name> --force-delete-without-recovery"
    echo ""
    echo "⚠️  Old secrets are kept for safety. Delete them only after confirming"
    echo "   everything works with the new prefixes."
else
    echo -e "${YELLOW}⚠️  No secrets were migrated${NC}"
fi

echo ""

