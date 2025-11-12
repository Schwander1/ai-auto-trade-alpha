#!/bin/bash
# Setup environment variables for Alpine Backend
# Copies .env.example to .env if it doesn't exist

set -e

ENV_FILE="alpine-backend/.env"
ENV_EXAMPLE="alpine-backend/.env.example"

echo "⚙️  Setting up Environment Variables"
echo "===================================="
echo ""

if [ ! -f "$ENV_EXAMPLE" ]; then
    echo "❌ Error: $ENV_EXAMPLE not found"
    exit 1
fi

if [ -f "$ENV_FILE" ]; then
    echo "⚠️  $ENV_FILE already exists"
    echo "Checking for missing Redis variables..."
    
    # Check if Redis variables are missing
    if ! grep -q "REDIS_HOST" "$ENV_FILE"; then
        echo "Adding Redis configuration..."
        cat >> "$ENV_FILE" << EOF

# Redis Configuration (Added by setup script)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=AlpineRedis2025!
REDIS_DB=0
EOF
        echo "✅ Redis configuration added to existing .env"
    else
        echo "✅ Redis configuration already present"
    fi
else
    echo "Creating $ENV_FILE from $ENV_EXAMPLE..."
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    echo "✅ Environment file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit $ENV_FILE and update the following:"
    echo "  - DATABASE_URL (if different)"
    echo "  - JWT_SECRET (use a strong secret)"
    echo "  - STRIPE keys (if using Stripe)"
    echo "  - REDIS_PASSWORD (match your Redis setup)"
fi

echo ""
echo "📋 Current Redis Configuration:"
grep -E "^REDIS_" "$ENV_FILE" || echo "  (Not found - check .env file)"

echo ""
echo "✅ Environment setup complete!"

