#!/bin/bash
# ARGO Capital Redis Professional Setup

echo "🚀 ARGO Capital Redis Cache Integration Setup"

# Install Redis via Homebrew
if ! command -v redis-server &> /dev/null; then
    echo "📦 Installing Redis..."
    brew install redis
else
    echo "✅ Redis already installed"
fi

# Create Redis configuration directory
mkdir -p config

# Professional Redis configuration for trading data
cat > config/redis.conf << 'REDIS_CONFIG'
# ARGO Capital Redis Configuration - Optimized for Trading Data

# Network
bind 127.0.0.1
port 6379
timeout 300

# Memory Management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence (for critical trading data)
save 900 1
save 300 10
save 60 10000

# Logging
loglevel notice
logfile /Users/dylanneuenschwander/projects/ARGO-Master-Unified/70database/redis/redis.log

# Performance
tcp-keepalive 300
tcp-backlog 511

# Database
databases 16

# Append Only File (for data persistence)
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec

# Security
requirepass ArgoCapital2025!

# Key expiration for cache optimization
notify-keyspace-events Ex
REDIS_CONFIG

echo "✅ Redis configuration created"

# Start Redis server with ARGO configuration
echo "🔧 Starting Redis server with ARGO Capital configuration..."
redis-server config/redis.conf --daemonize yes

sleep 3

# Test Redis connection
redis-cli -a ArgoCapital2025! ping > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Redis server running successfully"
    echo "🎯 ARGO Capital Redis cache ready on port 6379"
else
    echo "❌ Redis connection failed"
fi

