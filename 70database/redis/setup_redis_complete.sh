#!/bin/bash
# ARGO Capital Redis Complete Setup

echo "🚀 ARGO Capital Redis Cache Integration Setup"

# Install Redis if not present
if ! command -v redis-server &> /dev/null; then
    echo "📦 Installing Redis..."
    brew install redis
else
    echo "✅ Redis already installed"
fi

# Create configuration directory
mkdir -p config

# Redis configuration optimized for trading data
cat > config/redis.conf << 'REDIS_CONFIG'
# ARGO Capital Redis Configuration - Trading Optimized

# Network
bind 127.0.0.1
port 6379
timeout 300
tcp-keepalive 300
tcp-backlog 511

# General
daemonize yes
pidfile ./redis.pid

# Memory Management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000
dir ./

# Logging
loglevel notice
logfile ./redis.log

# Database
databases 16

# Append Only File
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec

# Security
requirepass ArgoCapital2025!

# Key expiration notifications
notify-keyspace-events Ex

# Performance tuning for trading data
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64

REDIS_CONFIG

echo "✅ Redis configuration created"

# Start Redis server
echo "🔧 Starting Redis server with ARGO Capital configuration..."
redis-server config/redis.conf

sleep 3

# Test connection
echo "🔍 Testing Redis connection..."
if redis-cli -a ArgoCapital2025! ping > /dev/null 2>&1; then
    echo "✅ Redis server running successfully"
    echo "🎯 ARGO Capital Redis cache ready on port 6379"
else
    echo "❌ Redis connection failed"
    echo "📋 Check logs: tail -f redis.log"
fi

