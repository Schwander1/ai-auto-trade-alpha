#!/bin/bash
set -e

echo "🚀 Setting up optimized local dev environment..."
echo ""

# Create directory structure
mkdir -p argo alpine-backend alpine-frontend

# ===== DOWNLOAD CODE FROM SERVERS =====
echo "📥 Downloading Argo from production..."
rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' \
  root@178.156.194.174:/root/argo-production/ ./argo/ || echo "⚠️ Argo download failed (check SSH access)"

echo "📥 Downloading Alpine Backend..."
rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' \
  root@91.98.153.49:/root/alpine-production/ ./alpine-backend/ || echo "⚠️ Backend download failed"

echo "📥 Downloading Alpine Frontend..."
rsync -avz --exclude='node_modules' --exclude='.next' --exclude='.git' \
  root@91.98.153.49:/root/alpine-analytics-website/ ./alpine-frontend/ || echo "⚠️ Frontend download failed"

# ===== ARGO SETUP =====
echo ""
echo "📊 Setting up Argo..."
cd argo

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel --quiet
pip install -r requirements.txt --quiet

cat > .env.local << 'ENVEOF'
ALPACA_API_KEY_ID=PKVFBDORPHOCX5NEOVEZNDTWVT
ALPACA_SECRET_KEY=ErscqTCdo21raoiFFyDzASzHpfgWB8L7xWVWKFukVa6b
ALPACA_PAPER=true
ALPACA_BASE_URL=https://paper-api.alpaca.markets
DATABASE_PATH=./data/signals_local.db
BRIDGE_API_URL=http://localhost:9001/bridge/signals
BRIDGE_API_SECRET=local_dev_secret
DEBUG=true
LOG_LEVEL=INFO
PORT=8000
ENVEOF

mkdir -p data
deactivate
cd ..

# ===== ALPINE BACKEND SETUP =====
echo "🏔️ Setting up Alpine Backend..."
cd alpine-backend

cat > docker-compose.local.yml << 'DOCKEREOF'
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    container_name: alpine-postgres-local
    environment:
      POSTGRES_USER: alpine
      POSTGRES_PASSWORD: alpine_pass
      POSTGRES_DB: alpine_db_local
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    container_name: alpine-redis-local
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
DOCKEREOF

docker-compose -f docker-compose.local.yml up -d
echo "⏳ Waiting for databases..."
sleep 8

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel --quiet
pip install -r requirements.txt --quiet

cat > .env.local << 'ENVEOF'
DATABASE_URL=postgresql://alpine:alpine_pass@localhost:5432/alpine_db_local
REDIS_URL=redis://localhost:6379
STRIPE_SECRET_KEY=sk_test_placeholder
STRIPE_PUBLISHABLE_KEY=pk_test_placeholder
JWT_SECRET=local_dev_secret
JWT_ALGORITHM=HS256
ARGO_BRIDGE_SECRET=local_dev_secret
DEBUG=true
ENVIRONMENT=development
PORT=9001
ENVEOF

deactivate
cd ..

# ===== ALPINE FRONTEND SETUP =====
echo "🎨 Setting up Alpine Frontend..."
cd alpine-frontend

npm install --prefer-offline --no-audit --quiet

cat > .env.local << 'ENVEOF'
NEXT_PUBLIC_API_URL=http://localhost:9001
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:9001/ws
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=local_dev_secret
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_placeholder
NEXT_PUBLIC_DEBUG=true
NEXT_PUBLIC_ENV=development
NEXT_TELEMETRY_DISABLED=1
ENVEOF

cd ..

# ===== CREATE RUN SCRIPTS =====
cat > run_argo.sh << 'RUNEOF'
#!/bin/bash
cd ~/argo-alpine-workspace/argo
source venv/bin/activate
python main.py
RUNEOF

cat > run_backend.sh << 'RUNEOF'
#!/bin/bash
cd ~/argo-alpine-workspace/alpine-backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 9001
RUNEOF

cat > run_frontend.sh << 'RUNEOF'
#!/bin/bash
cd ~/argo-alpine-workspace/alpine-frontend
npm run dev
RUNEOF

chmod +x run_*.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Open Cursor: open -a Cursor ~/argo-alpine-workspace"
echo "  2. In Cursor, open 3 terminals and run:"
echo "     - Terminal 1: ./run_argo.sh"
echo "     - Terminal 2: ./run_backend.sh"
echo "     - Terminal 3: ./run_frontend.sh"
