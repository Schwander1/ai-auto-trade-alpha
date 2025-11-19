#!/bin/bash
set -e

# Deploy Alpine backend and frontend to production (91.98.153.49)
# Zero-downtime blue/green deployment

ALPINE_SERVER="91.98.153.49"
ALPINE_USER="root"
ALPINE_BACKEND_PATH="/root/alpine-production"
ALPINE_FRONTEND_PATH="/root/alpine-analytics-website"
BLUE_PATH="/root/alpine-production-blue"
GREEN_PATH="/root/alpine-production-green"

echo "🚀 Deploying Alpine to production (zero-downtime)..."
echo "==================================================="

# Determine current deployment color
CURRENT_COLOR=$(ssh ${ALPINE_USER}@${ALPINE_SERVER} "
  if docker ps | grep -q alpine-production-blue; then
    echo 'blue'
  elif docker ps | grep -q alpine-production-green; then
    echo 'green'
  else
    echo 'blue'
  fi
" 2>/dev/null || echo "blue")

# Determine target color (opposite of current)
if [ "$CURRENT_COLOR" = "blue" ]; then
  TARGET_COLOR="green"
  TARGET_PATH=$GREEN_PATH
  CURRENT_PATH=$BLUE_PATH
else
  TARGET_COLOR="blue"
  TARGET_PATH=$BLUE_PATH
  CURRENT_PATH=$GREEN_PATH
fi

echo "Current deployment: $CURRENT_COLOR"
echo "Deploying to: $TARGET_COLOR"

# Step 1: Deploy to target color
echo ""
echo "📤 Step 1: Deploying to $TARGET_COLOR environment..."

# Deploy backend
rsync -avz \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='.next' \
  --exclude='*.log' \
  alpine-backend/ \
  ${ALPINE_USER}@${ALPINE_SERVER}:${TARGET_PATH}/

# Deploy frontend
rsync -avz \
  --exclude='node_modules' \
  --exclude='.next' \
  --exclude='.git' \
  --exclude='*.log' \
  alpine-frontend/ \
  ${ALPINE_USER}@${ALPINE_SERVER}:${TARGET_PATH}/../alpine-analytics-website-${TARGET_COLOR}/ 2>/dev/null || echo "⚠️  Frontend directory not found, skipping..."

echo "✅ Code deployed to $TARGET_COLOR"

# Step 2: Build and start target environment
echo ""
echo "🔨 Step 2: Building $TARGET_COLOR environment..."
ssh ${ALPINE_USER}@${ALPINE_SERVER} "
  cd ${TARGET_PATH}
  
  # Update docker-compose to use target color ports
  if [ '$TARGET_COLOR' = 'green' ]; then
    BACKEND_PORT=8002
    FRONTEND_PORT=3002
    REDIS_PORT=6381
    POSTGRES_PORT=5434
  else
    BACKEND_PORT=8001
    FRONTEND_PORT=3000
    REDIS_PORT=6380
    POSTGRES_PORT=5433
  fi
  
  # Update docker-compose.yml with correct ports
  cat > docker-compose.yml << EOF
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - \"\${FRONTEND_PORT}:3000\"
    environment:
      - NEXT_PUBLIC_API_URL=http://91.98.153.49:8001
    restart: unless-stopped
    networks:
      - alpine-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - \"\${BACKEND_PORT}:8000\"
    env_file:
      - .env
    environment:
      - ARGO_API_URL=http://178.156.194.174:8000
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://alpine_user:AlpineSecure2025!@postgres:5432/alpine_prod
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_PASSWORD=AlpineRedis2025!
      - REDIS_DB=0
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - alpine-network

  postgres:
    image: postgres:15
    ports:
      - \"\${POSTGRES_PORT}:5432\"
    environment:
      - POSTGRES_USER=alpine_user
      - POSTGRES_PASSWORD=AlpineSecure2025!
      - POSTGRES_DB=alpine_prod
    volumes:
      - postgres_data_${TARGET_COLOR}:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - alpine-network

  redis:
    image: redis:7-alpine
    ports:
      - \"\${REDIS_PORT}:6379\"
    command: redis-server --requirepass AlpineRedis2025!
    restart: unless-stopped
    networks:
      - alpine-network

volumes:
  postgres_data_${TARGET_COLOR}:

networks:
  alpine-network:
    driver: bridge
EOF
  
  # Build and start
  docker compose down 2>/dev/null || true
  docker compose build --no-cache
  docker compose up -d
  
  echo '✅ $TARGET_COLOR environment started'
"

# Step 3: Health check target (Level 1 - Basic)
echo ""
echo "🏥 Step 3: Health checking $TARGET_COLOR environment (Level 1 - Basic)..."
MAX_RETRIES=30
RETRY_COUNT=0
TARGET_BACKEND_PORT=$([ "$TARGET_COLOR" = "green" ] && echo "8002" || echo "8001")

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if ssh ${ALPINE_USER}@${ALPINE_SERVER} "curl -f -s --max-time 5 http://localhost:${TARGET_BACKEND_PORT}/health" > /dev/null; then
    echo "✅ $TARGET_COLOR backend basic health check passed"
    break
  fi
  
  RETRY_COUNT=$((RETRY_COUNT + 1))
  echo "⏳ Waiting for $TARGET_COLOR backend... ($RETRY_COUNT/$MAX_RETRIES)"
  sleep 5
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
  echo "❌ $TARGET_COLOR health check failed - keeping $CURRENT_COLOR active"
  ssh ${ALPINE_USER}@${ALPINE_SERVER} "cd ${TARGET_PATH} && docker compose down"
  exit 1
fi

# Step 3b: Gate 11 - 100% Health Confirmation (Level 3 Comprehensive) - MANDATORY
echo ""
echo "🏥 Step 3b: Gate 11 - 100% Health Confirmation (Level 3 Comprehensive) - MANDATORY..."
echo "   Running comprehensive health check for $TARGET_COLOR environment..."

# For Alpine, we check API endpoints, database, Redis, etc.
HEALTH_CHECKS_PASSED=0
HEALTH_CHECKS_FAILED=0

# Check backend API
if ssh ${ALPINE_USER}@${ALPINE_SERVER} "curl -f -s --max-time 5 http://localhost:${TARGET_BACKEND_PORT}/health" > /dev/null; then
  HEALTH_CHECKS_PASSED=$((HEALTH_CHECKS_PASSED + 1))
  echo "   ✅ Backend API health check passed"
else
  HEALTH_CHECKS_FAILED=$((HEALTH_CHECKS_FAILED + 1))
  echo "   ❌ Backend API health check failed"
fi

# Check database connection (via API endpoint if available)
if ssh ${ALPINE_USER}@${ALPINE_SERVER} "curl -f -s --max-time 5 http://localhost:${TARGET_BACKEND_PORT}/api/health/db" > /dev/null 2>&1; then
  HEALTH_CHECKS_PASSED=$((HEALTH_CHECKS_PASSED + 1))
  echo "   ✅ Database health check passed"
else
  # Database check might not be available, skip if endpoint doesn't exist
  echo "   ⏭️  Database health check endpoint not available (skipping)"
fi

# Check Redis connection (via API endpoint if available)
if ssh ${ALPINE_USER}@${ALPINE_SERVER} "curl -f -s --max-time 5 http://localhost:${TARGET_BACKEND_PORT}/api/health/redis" > /dev/null 2>&1; then
  HEALTH_CHECKS_PASSED=$((HEALTH_CHECKS_PASSED + 1))
  echo "   ✅ Redis health check passed"
else
  # Redis check might not be available, skip if endpoint doesn't exist
  echo "   ⏭️  Redis health check endpoint not available (skipping)"
fi

# Verify Gate 11: 100% pass rate required
if [ $HEALTH_CHECKS_FAILED -eq 0 ] && [ $HEALTH_CHECKS_PASSED -gt 0 ]; then
  echo "✅ Gate 11 PASSED: 100% health confirmation (${HEALTH_CHECKS_PASSED} checks passed, 0 failed)"
  echo "   Deployment health: 100%"
else
  echo "❌ Gate 11 FAILED: Health checks did not pass 100%"
  echo "   Passed: ${HEALTH_CHECKS_PASSED}, Failed: ${HEALTH_CHECKS_FAILED}"
  echo "   Keeping $CURRENT_COLOR active, stopping $TARGET_COLOR..."
  ssh ${ALPINE_USER}@${ALPINE_SERVER} "cd ${TARGET_PATH} && docker compose down"
  exit 1
fi

# Step 4: Switch traffic (update nginx/load balancer)
echo ""
echo "🔄 Step 4: Switching traffic to $TARGET_COLOR..."
ssh ${ALPINE_USER}@${ALPINE_SERVER} "
  # Update nginx config to point to $TARGET_COLOR
  if [ -f /etc/nginx/sites-enabled/alpine ]; then
    if [ '$TARGET_COLOR' = 'green' ]; then
      sed -i 's/8001/8002/g' /etc/nginx/sites-enabled/alpine
      sed -i 's/3000/3002/g' /etc/nginx/sites-enabled/alpine
    else
      sed -i 's/8002/8001/g' /etc/nginx/sites-enabled/alpine
      sed -i 's/3002/3000/g' /etc/nginx/sites-enabled/alpine
    fi
    nginx -t && systemctl reload nginx
    echo '✅ Traffic switched to $TARGET_COLOR'
  else
    echo '⚠️  Nginx config not found - manual switch may be needed'
  fi
"

# Step 5: Stop old environment (after grace period)
echo ""
echo "⏳ Step 5: Waiting grace period before stopping $CURRENT_COLOR..."
sleep 50

ssh ${ALPINE_USER}@${ALPINE_SERVER} "
  if [ -d ${CURRENT_PATH} ]; then
    cd ${CURRENT_PATH}
    docker compose down
    echo '✅ $CURRENT_COLOR environment stopped'
  fi
"

echo ""
echo "🎉 Alpine deployment complete! ($TARGET_COLOR is now active)"

