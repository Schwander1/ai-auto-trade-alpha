#!/bin/bash
# Update Stripe configuration with live keys and price IDs

set -e

ALPINE_SERVER="91.98.153.49"
ALPINE_USER="root"
ENV_FILE="/root/alpine-production/.env"

echo "🔑 Updating Stripe Configuration with Live Keys"
echo "================================================"
echo ""

# Stripe configuration
STRIPE_PUBLISHABLE_KEY="pk_live_51SRKOLLoDEAt72V2WabxQnfaaStUVJQ1W6fERkRfqKOgzz5QWVSFLdnxi6t7IXq7Zh6lthwzzeslPVD7BjJPJShQ00HaL3Opj1"
STRIPE_SECRET_KEY="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"
STRIPE_WEBHOOK_SECRET="whsec_84b696fd63f217fe9c75ad2d9b2e46be2cd1f175fa6daab6905f458127319f85"
STRIPE_ACCOUNT_ID="acct_1SRKOLLoDEAt72V2"

# Price IDs
STRIPE_STARTER_PRICE_ID="price_1SSNCpLoDEAt72V24jylX5T0"  # Founder
STRIPE_PRO_PRICE_ID="price_1SSNRdLoDEAt72V2LIS5cbRI"  # Professional
STRIPE_ELITE_PRICE_ID="price_1SSNXhLoDEAt72V2Y2uQarct"  # Institutional

echo "📤 Updating Alpine .env file on production server..."

ssh ${ALPINE_USER}@${ALPINE_SERVER} << EOF
cd /root/alpine-production

# Backup existing .env
if [ -f .env ]; then
    cp .env .env.backup.\$(date +%Y%m%d_%H%M%S)
    echo "✅ Backed up existing .env"
fi

# Update or add Stripe configuration
if [ -f .env ]; then
    # Update existing values
    sed -i "s|STRIPE_SECRET_KEY=.*|STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}|" .env
    sed -i "s|STRIPE_PUBLISHABLE_KEY=.*|STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY}|" .env
    sed -i "s|STRIPE_WEBHOOK_SECRET=.*|STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}|" .env
    
    # Add or update account ID
    if grep -q "STRIPE_ACCOUNT_ID" .env; then
        sed -i "s|STRIPE_ACCOUNT_ID=.*|STRIPE_ACCOUNT_ID=${STRIPE_ACCOUNT_ID}|" .env
    else
        echo "STRIPE_ACCOUNT_ID=${STRIPE_ACCOUNT_ID}" >> .env
    fi
    
    # Add or update price IDs
    if grep -q "STRIPE_STARTER_PRICE_ID" .env; then
        sed -i "s|STRIPE_STARTER_PRICE_ID=.*|STRIPE_STARTER_PRICE_ID=${STRIPE_STARTER_PRICE_ID}|" .env
    else
        echo "" >> .env
        echo "# Stripe Price IDs" >> .env
        echo "STRIPE_STARTER_PRICE_ID=${STRIPE_STARTER_PRICE_ID}" >> .env
    fi
    
    if grep -q "STRIPE_PRO_PRICE_ID" .env; then
        sed -i "s|STRIPE_PRO_PRICE_ID=.*|STRIPE_PRO_PRICE_ID=${STRIPE_PRO_PRICE_ID}|" .env
    else
        echo "STRIPE_PRO_PRICE_ID=${STRIPE_PRO_PRICE_ID}" >> .env
    fi
    
    if grep -q "STRIPE_ELITE_PRICE_ID" .env; then
        sed -i "s|STRIPE_ELITE_PRICE_ID=.*|STRIPE_ELITE_PRICE_ID=${STRIPE_ELITE_PRICE_ID}|" .env
    else
        echo "STRIPE_ELITE_PRICE_ID=${STRIPE_ELITE_PRICE_ID}" >> .env
    fi
else
    echo "❌ .env file not found! Creating new one..."
    cat > .env << EOL
# Alpine Backend Environment Variables

# Database
DATABASE_URL=postgresql://alpine_user:AlpineSecure2025!@postgres:5432/alpine_prod

# Stripe
STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE_KEY}
STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
STRIPE_ACCOUNT_ID=${STRIPE_ACCOUNT_ID}

# Stripe Price IDs
STRIPE_STARTER_PRICE_ID=${STRIPE_STARTER_PRICE_ID}
STRIPE_PRO_PRICE_ID=${STRIPE_PRO_PRICE_ID}
STRIPE_ELITE_PRICE_ID=${STRIPE_ELITE_PRICE_ID}

# JWT Authentication
JWT_SECRET=\$(grep JWT_SECRET .env 2>/dev/null | cut -d'=' -f2 || echo "change_me")
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Domain & URLs
DOMAIN=91.98.153.49
FRONTEND_URL=http://91.98.153.49:3000

# Argo API
ARGO_API_URL=http://178.156.194.174:8000
EOL
fi

echo ""
echo "✅ Stripe configuration updated!"
echo ""
echo "Updated Stripe settings:"
grep "STRIPE" .env | grep -v "^#"
EOF

echo ""
echo "✅ Stripe configuration updated successfully!"
echo ""
echo "📋 Configuration Summary:"
echo "  - Publishable Key: ${STRIPE_PUBLISHABLE_KEY:0:20}..."
echo "  - Secret Key: ${STRIPE_SECRET_KEY:0:20}..."
echo "  - Account ID: ${STRIPE_ACCOUNT_ID}"
echo "  - Founder Price ID: ${STRIPE_STARTER_PRICE_ID}"
echo "  - Professional Price ID: ${STRIPE_PRO_PRICE_ID}"
echo "  - Institutional Price ID: ${STRIPE_ELITE_PRICE_ID}"

