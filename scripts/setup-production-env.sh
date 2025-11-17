#!/bin/bash
# Setup production environment variables

set -e

echo "🔧 Setting up production environment variables"
echo "=============================================="
echo ""

# Generate secure random strings
generate_secret() {
    openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))"
}

# Argo server
ARGO_SERVER="178.156.194.174"
ARGO_USER="root"

# Alpine server
ALPINE_SERVER="91.98.153.49"
ALPINE_USER="root"

echo "📝 Generating secure secrets..."
JWT_SECRET=$(generate_secret)
ARGO_API_SECRET=$(generate_secret)
ARGO_ALPINE_API_KEY=$(generate_secret)

echo "✅ Secrets generated"
echo ""

# Setup Argo .env
echo "📤 Setting up Argo environment..."
ssh ${ARGO_USER}@${ARGO_SERVER} << EOF
cd /root/argo-production
cat > .env << EOL
# Argo Trading Engine Environment Variables
ARGO_API_SECRET=${ARGO_API_SECRET}

# Alpine Backend Sync Configuration
ALPINE_API_URL=http://91.98.153.49:8001
ARGO_API_KEY=${ARGO_ALPINE_API_KEY}
ALPINE_SYNC_ENABLED=true
EOL
echo "✅ Argo .env created"
EOF

# Setup Alpine .env
echo "📤 Setting up Alpine environment..."
ssh ${ALPINE_USER}@${ALPINE_SERVER} << EOF
cd /root/alpine-production
cat > .env << EOL
# Alpine Backend Environment Variables

# Database
DATABASE_URL=postgresql://alpine_user:AlpineSecure2025!@postgres:5432/alpine_prod

# Stripe (UPDATE WITH REAL KEYS)
STRIPE_SECRET_KEY=sk_test_placeholder
STRIPE_PUBLISHABLE_KEY=pk_test_placeholder
STRIPE_WEBHOOK_SECRET=whsec_WILL_GET_LATER

# JWT Authentication
JWT_SECRET=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Domain & URLs
DOMAIN=91.98.153.49
FRONTEND_URL=http://91.98.153.49:3000

# Argo API
ARGO_API_URL=http://178.156.194.174:8000

# External Signal Provider (Argo) API Key
EXTERNAL_SIGNAL_API_KEY=${ARGO_ALPINE_API_KEY}

# Optional: Email (SendGrid)
SENDGRID_API_KEY=
EOL
echo "✅ Alpine .env created"
EOF

echo ""
echo "✅ Production environment variables configured!"
echo ""
echo "⚠️  IMPORTANT: Update Stripe keys in Alpine .env file:"
echo "   ssh ${ALPINE_USER}@${ALPINE_SERVER} 'cd /root/alpine-production && nano .env'"

