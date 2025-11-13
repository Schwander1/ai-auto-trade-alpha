#!/bin/bash
# Setup secure API-based sync between Argo Capital and Alpine Analytics
# Maintains complete entity separation - no direct database access

set -e

echo "🔐 Setting up Argo → Alpine Secure API Sync"
echo "============================================"
echo ""
echo "This script will:"
echo "  1. Generate a secure API key for Argo to authenticate with Alpine"
echo "  2. Add the key to AWS Secrets Manager for both services"
echo "  3. Configure Alpine API URL for Argo"
echo ""
echo "⚠️  Entity Separation:"
echo "  - Argo Capital: Signal producer (sends via API)"
echo "  - Alpine Analytics: Signal consumer (receives via API)"
echo "  - No direct database access between entities"
echo ""

# Check if AWS CLI is available
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first."
    exit 1
fi

# Generate secure API key (64 characters, URL-safe)
API_KEY=$(openssl rand -hex 32)
echo "✅ Generated secure API key: ${API_KEY:0:16}..."

# Get Alpine API URL
read -p "Enter Alpine Backend API URL [http://localhost:9001]: " ALPINE_API_URL
ALPINE_API_URL=${ALPINE_API_URL:-http://localhost:9001}

echo ""
echo "📋 Configuration:"
echo "  Alpine API URL: $ALPINE_API_URL"
echo "  API Key: ${API_KEY:0:16}..."
echo ""

read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

# Add to AWS Secrets Manager
echo ""
echo "🔐 Adding secrets to AWS Secrets Manager..."

# For Alpine Backend (receives signals)
echo "  Adding ARGO_API_KEY to alpine-backend..."
aws secretsmanager put-secret-value \
    --secret-id "argo-alpine/alpine-backend/argo-api-key" \
    --secret-string "$API_KEY" \
    2>/dev/null || \
aws secretsmanager create-secret \
    --name "argo-alpine/alpine-backend/argo-api-key" \
    --description "API key for Argo Capital to authenticate with Alpine Analytics API" \
    --secret-string "$API_KEY" \
    > /dev/null

# For Argo (sends signals)
echo "  Adding ARGO_API_KEY to argo..."
aws secretsmanager put-secret-value \
    --secret-id "argo-alpine/argo/argo-api-key" \
    --secret-string "$API_KEY" \
    2>/dev/null || \
aws secretsmanager create-secret \
    --name "argo-alpine/argo/argo-api-key" \
    --description "API key for Argo to authenticate with Alpine Analytics API" \
    --secret-string "$API_KEY" \
    > /dev/null

echo "  Adding ALPINE_API_URL to argo..."
aws secretsmanager put-secret-value \
    --secret-id "argo-alpine/argo/alpine-api-url" \
    --secret-string "$ALPINE_API_URL" \
    2>/dev/null || \
aws secretsmanager create-secret \
    --name "argo-alpine/argo/alpine-api-url" \
    --description "Alpine Analytics API URL for Argo to send signals" \
    --secret-string "$ALPINE_API_URL" \
    > /dev/null

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next Steps:"
echo "  1. Restart Alpine Backend to load ARGO_API_KEY"
echo "  2. Restart Argo to load ARGO_API_KEY and ALPINE_API_URL"
echo "  3. Verify sync: Check Argo logs for 'Signal synced to Alpine'"
echo "  4. Verify storage: Check Alpine PostgreSQL for signals"
echo ""
echo "🔍 Verification:"
echo "  Alpine health: curl http://localhost:9001/api/v1/argo/sync/health"
echo "  Argo sync test: Check Argo logs after signal generation"

