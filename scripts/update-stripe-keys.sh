#!/bin/bash
# Update Stripe keys in Alpine production environment

set -e

ALPINE_SERVER="91.98.153.49"
ALPINE_USER="root"
ENV_FILE="/root/alpine-production/.env"

echo "🔑 Updating Stripe Configuration"
echo "================================="
echo ""

# Prompt for Stripe keys
read -p "Enter Stripe Publishable Key (pk_live_...): " STRIPE_PUBLISHABLE_KEY
read -p "Enter Stripe Secret Key (sk_live_...): " STRIPE_SECRET_KEY
read -p "Enter Stripe Webhook Secret (whsec_...): " STRIPE_WEBHOOK_SECRET
read -p "Enter Stripe Account ID (optional): " STRIPE_ACCOUNT_ID
read -p "Enter Starter Price ID (price_...): " STARTER_PRICE_ID
read -p "Enter Pro Price ID (price_...): " PRO_PRICE_ID
read -p "Enter Elite Price ID (price_...): " ELITE_PRICE_ID

echo ""
echo "📤 Updating Alpine .env file..."

ssh ${ALPINE_USER}@${ALPINE_SERVER} << EOF
cd /root/alpine-production

# Read existing .env
if [ -f .env ]; then
    # Backup existing .env
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    
    # Update Stripe keys
    sed -i "s|STRIPE_SECRET_KEY=.*|STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}|" .env
    sed -i "s|STRIPE_PUBLISHABLE_KEY=.*|STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY}|" .env
    sed -i "s|STRIPE_WEBHOOK_SECRET=.*|STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}|" .env
    
    # Add price IDs if not present
    if ! grep -q "STRIPE_STARTER_PRICE_ID" .env; then
        echo "" >> .env
        echo "# Stripe Price IDs" >> .env
    fi
    sed -i "s|STRIPE_STARTER_PRICE_ID=.*|STRIPE_STARTER_PRICE_ID=${STARTER_PRICE_ID}|" .env || echo "STRIPE_STARTER_PRICE_ID=${STARTER_PRICE_ID}" >> .env
    sed -i "s|STRIPE_PRO_PRICE_ID=.*|STRIPE_PRO_PRICE_ID=${PRO_PRICE_ID}|" .env || echo "STRIPE_PRO_PRICE_ID=${PRO_PRICE_ID}" >> .env
    sed -i "s|STRIPE_ELITE_PRICE_ID=.*|STRIPE_ELITE_PRICE_ID=${ELITE_PRICE_ID}|" .env || echo "STRIPE_ELITE_PRICE_ID=${ELITE_PRICE_ID}" >> .env
    
    if [ ! -z "${STRIPE_ACCOUNT_ID}" ]; then
        sed -i "s|STRIPE_ACCOUNT_ID=.*|STRIPE_ACCOUNT_ID=${STRIPE_ACCOUNT_ID}|" .env || echo "STRIPE_ACCOUNT_ID=${STRIPE_ACCOUNT_ID}" >> .env
    fi
    
    echo "✅ Stripe keys updated in .env"
    echo ""
    echo "Updated values:"
    grep "STRIPE" .env | grep -v "^#"
else
    echo "❌ .env file not found!"
    exit 1
fi
EOF

echo ""
echo "✅ Stripe configuration updated successfully!"

