# Argo → Alpine Quick Start Guide

## Daily Startup

1. Open Cursor: cd ~/argo-alpine-workspace && open -a Cursor .
2. Press Cmd+L and say: "Start all services"

## Service URLs
- Argo: http://localhost:8000
- Backend: http://localhost:9001
- Frontend: http://localhost:3001

## Test Commands
curl http://localhost:8000/health
curl http://localhost:9001/health
open http://localhost:3001

## Cursor Commands (Cmd+L)
- "Start all services"
- "Test health endpoints"
- "Show Argo signals"
- "Restart backend"

## Manual Start
Terminal 1: cd ~/argo-alpine-workspace/argo && source venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000
Terminal 2: cd ~/argo-alpine-workspace/alpine-backend && source venv/bin/activate && uvicorn backend.main:app --reload --host 0.0.0.0 --port 9001
Terminal 3: cd ~/argo-alpine-workspace/alpine-frontend && npm run dev
