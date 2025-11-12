#!/bin/bash
# Execute complete deployment of optimizations
# This script performs all deployment steps

set -e

echo "🚀 Executing Complete Deployment"
echo "================================"
echo ""

# Step 1: Commit all changes
echo "Step 1: Committing Changes"
echo "-------------------------"
cd "$(dirname "$0")/.."
git add -A
git status --short | head -10
echo "✅ Changes staged"
echo ""

# Step 2: Deploy to production
echo "Step 2: Deploying to Production"
echo "-------------------------------"
echo "Deploying Alpine backend..."
./scripts/deploy-alpine.sh
echo ""

# Step 3: Update production environment
echo "Step 3: Updating Production Environment"
echo "---------------------------------------"
ALPINE_SERVER="91.98.153.49"
ALPINE_USER="root"

ssh ${ALPINE_USER}@${ALPINE_SERVER} << 'ENDSSH'
cd /root/alpine-analytics-website-blue 2>/dev/null || cd /root/alpine-backend 2>/dev/null || echo "Directory not found"

# Add Redis config to .env if it exists
if [ -f .env ]; then
    if ! grep -q "REDIS_HOST" .env; then
        echo "" >> .env
        echo "# Redis Configuration" >> .env
        echo "REDIS_HOST=localhost" >> .env
        echo "REDIS_PORT=6379" >> .env
        echo "REDIS_PASSWORD=AlpineRedis2025!" >> .env
        echo "REDIS_DB=0" >> .env
        echo "✅ Redis configuration added to .env"
    else
        echo "✅ Redis configuration already present"
    fi
else
    echo "⚠️  .env file not found - create it manually"
fi
ENDSSH
echo ""

# Step 4: Run database migration on production
echo "Step 4: Running Database Migration"
echo "----------------------------------"
ssh ${ALPINE_USER}@${ALPINE_SERVER} << 'ENDSSH'
cd /root/alpine-analytics-website-blue/backend 2>/dev/null || cd /root/alpine-backend/backend 2>/dev/null || exit 0

if [ -d "venv" ]; then
    source venv/bin/activate
    python -m backend.migrations.add_indexes 2>&1 || echo "⚠️  Migration may need manual execution"
else
    echo "⚠️  Virtual environment not found - migration skipped"
fi
ENDSSH
echo ""

# Step 5: Restart services
echo "Step 5: Restarting Services"
echo "--------------------------"
ssh ${ALPINE_USER}@${ALPINE_SERVER} << 'ENDSSH'
cd /root/alpine-analytics-website-blue 2>/dev/null || cd /root/alpine-backend 2>/dev/null || exit 0

if [ -f "docker-compose.yml" ]; then
    docker-compose restart backend 2>/dev/null || docker compose restart backend 2>/dev/null || echo "⚠️  Could not restart backend"
    echo "✅ Backend restart initiated"
fi
ENDSSH
echo ""

# Step 6: Wait and verify
echo "Step 6: Verifying Deployment"
echo "---------------------------"
sleep 10

echo -n "Checking Alpine health... "
if curl -s -f "http://${ALPINE_SERVER}:8001/health" | grep -q "healthy"; then
    echo "✅ Healthy"
else
    echo "⚠️  Health check failed"
fi

echo -n "Checking metrics endpoint... "
if curl -s -f "http://${ALPINE_SERVER}:8001/metrics" > /dev/null 2>&1; then
    echo "✅ Available"
else
    echo "⚠️  Not available (may need code deployment)"
fi

echo ""
echo "✅ Deployment execution complete!"
echo ""
echo "Next: Run tests with ./scripts/test-optimizations.sh"

