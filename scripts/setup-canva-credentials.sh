#!/bin/bash
# Setup Canva API credentials in AWS Secrets Manager

set -e

echo "🔧 Setting up Canva API credentials for Alpine Analytics"
echo ""

# Check if AWS CLI is available
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first."
    exit 1
fi

# Client ID (we already have this)
CLIENT_ID="OC-AZqFb4XOryzI"

# Get Client Secret from user
read -sp "Enter Canva Client Secret (full secret): " CLIENT_SECRET
echo ""

if [ -z "$CLIENT_SECRET" ]; then
    echo "❌ Client Secret is required"
    exit 1
fi

# Store Client ID
echo "📦 Storing Client ID..."
aws secretsmanager create-secret \
    --name alpine-analytics/canva-client-id \
    --secret-string "$CLIENT_ID" \
    --description "Canva OAuth Client ID for Alpine Analytics brand automation" \
    2>/dev/null || \
aws secretsmanager update-secret \
    --secret-id alpine-analytics/canva-client-id \
    --secret-string "$CLIENT_ID" \
    >/dev/null

# Store Client Secret
echo "📦 Storing Client Secret..."
aws secretsmanager create-secret \
    --name alpine-analytics/canva-client-secret \
    --secret-string "$CLIENT_SECRET" \
    --description "Canva OAuth Client Secret for Alpine Analytics brand automation" \
    2>/dev/null || \
aws secretsmanager update-secret \
    --secret-id alpine-analytics/canva-client-secret \
    --secret-string "$CLIENT_SECRET" \
    >/dev/null

echo "✅ Credentials stored successfully!"
echo ""
echo "Next steps:"
echo "1. Run: python3 scripts/canva_oauth2.py --auth"
echo "2. Visit the authorization URL and grant access"
echo "3. Use the authorization code with: python3 scripts/canva_oauth2.py --code <CODE> --state <STATE>"

