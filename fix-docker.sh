#!/bin/bash

# Script to fix Docker Desktop corruption on macOS
# Run with: bash fix-docker.sh

set -e

echo "🔧 Docker Desktop Fix Script for macOS"
echo "======================================"
echo ""

# Step 1: Quit Docker Desktop completely
echo "Step 1: Quitting Docker Desktop..."
osascript -e 'quit app "Docker"' 2>/dev/null || echo "Docker Desktop was not running"
sleep 2

# Step 2: Kill any remaining Docker processes
echo "Step 2: Killing remaining Docker processes..."
killall Docker 2>/dev/null || echo "No Docker processes found"
killall com.docker.backend 2>/dev/null || echo "No Docker backend processes found"
sleep 2

# Step 3: Reset Docker Desktop (Option 1 - Recommended)
echo ""
echo "Choose an option:"
echo "1. Reset Docker Desktop to factory defaults (recommended)"
echo "2. Clear all Docker data (containers, images, volumes)"
echo "3. Both (nuclear option)"
echo ""
read -p "Enter option (1-3): " option

case $option in
  1)
    echo ""
    echo "Resetting Docker Desktop to factory defaults..."
    rm -rf ~/Library/Group\ Containers/group.com.docker/settings.json 2>/dev/null || true
    rm -rf ~/Library/Containers/com.docker.docker/Data/settings.json 2>/dev/null || true
    echo "✅ Docker Desktop settings reset"
    ;;
  2)
    echo ""
    echo "Clearing all Docker data..."
    rm -rf ~/Library/Containers/com.docker.docker/Data/vms 2>/dev/null || true
    rm -rf ~/.docker 2>/dev/null || true
    echo "✅ Docker data cleared"
    ;;
  3)
    echo ""
    echo "Performing full reset..."
    rm -rf ~/Library/Group\ Containers/group.com.docker 2>/dev/null || true
    rm -rf ~/Library/Containers/com.docker.docker 2>/dev/null || true
    rm -rf ~/.docker 2>/dev/null || true
    echo "✅ Full reset complete"
    ;;
  *)
    echo "Invalid option. Exiting."
    exit 1
    ;;
esac

echo ""
echo "Step 4: Restarting Docker Desktop..."
open -a Docker

echo ""
echo "⏳ Waiting for Docker Desktop to start (this may take 30-60 seconds)..."
sleep 10

# Wait for Docker to be ready
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
  if docker info >/dev/null 2>&1; then
    echo "✅ Docker Desktop is running!"
    docker info | grep -E "Server Version|Operating System" | head -2
    break
  fi
  attempt=$((attempt + 1))
  echo "   Waiting... ($attempt/$max_attempts)"
  sleep 2
done

if [ $attempt -eq $max_attempts ]; then
  echo ""
  echo "⚠️  Docker Desktop may still be starting. Please check Docker Desktop manually."
  echo "   If it's still not working, you may need to reinstall Docker Desktop."
else
  echo ""
  echo "🎉 Docker Desktop has been fixed and is ready to use!"
fi

