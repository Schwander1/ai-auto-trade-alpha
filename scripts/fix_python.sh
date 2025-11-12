#!/bin/bash
set -e

echo "🔧 Fixing Python compatibility..."

# Install Python 3.12
brew install python@3.12

# Setup Argo
echo "📊 Setting up Argo with Python 3.12..."
cd ~/argo-alpine-workspace/argo
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel --quiet
pip install -r requirements.txt --quiet
deactivate

# Setup Alpine Backend
echo "🏔️ Setting up Alpine Backend with Python 3.12..."
cd ~/argo-alpine-workspace/alpine-backend
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel --quiet
pip install -r requirements.txt --quiet
deactivate

# Start Docker Desktop
echo "🐳 Starting Docker..."
open -a Docker
echo "Waiting for Docker to start..."
sleep 15

# Start databases
cd ~/argo-alpine-workspace/alpine-backend
docker-compose -f docker-compose.local.yml up -d

echo "⏳ Waiting for databases..."
sleep 10

# Check status
docker ps

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start services:"
echo "  1. open -a Cursor ~/argo-alpine-workspace"
echo "  2. In Cursor terminal 1: cd ~/argo-alpine-workspace/argo && source venv/bin/activate && python main.py"
echo "  3. In Cursor terminal 2: cd ~/argo-alpine-workspace/alpine-backend && source venv/bin/activate && uvicorn backend.main:app --reload --port 9001"
echo "  4. In Cursor terminal 3: cd ~/argo-alpine-workspace/alpine-frontend && npm run dev"
