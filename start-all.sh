#!/bin/bash

echo "🚀 Starting Argo → Alpine Dev Environment..."

# Start databases
docker-compose -f alpine-backend/docker-compose.local.yml up -d

# Start Argo in background
cd ~/argo-alpine-workspace/argo
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &

# Start Alpine Backend in background
cd ~/argo-alpine-workspace/alpine-backend
source venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 9001 &

# Start Alpine Frontend
cd ~/argo-alpine-workspace/alpine-frontend
npm run dev

echo "✅ All services started!"
echo "   Argo:     http://localhost:8000"
echo "   Backend:  http://localhost:9001"
echo "   Frontend: http://localhost:3001"
