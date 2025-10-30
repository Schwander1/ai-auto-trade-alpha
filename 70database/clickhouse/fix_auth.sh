#!/bin/bash
# Fix ClickHouse Authentication Issue

echo "🔧 Fixing ARGO Capital ClickHouse Authentication"

# Stop existing ClickHouse server
echo "🛑 Stopping existing ClickHouse server..."
pkill -f clickhouse-server
sleep 2

# Remove old PID file if exists
rm -f clickhouse-server.pid

# Clean up old data (optional - comment out if you want to keep data)
# rm -rf data/*

# Remove temporary directory and recreate
rm -rf /tmp/clickhouse
mkdir -p /tmp/clickhouse

# Recreate directories
mkdir -p config data logs user_files

# Start with the fixed configuration
echo "🚀 Starting ClickHouse with corrected configuration..."
./start_clickhouse.sh

# Wait for server to start
echo "⏳ Waiting for ClickHouse to initialize..."
sleep 10

# Test connection with password
echo "🔍 Testing connection..."
if clickhouse-client --password ArgoCapital2025! --query "SELECT 'Authentication Fixed!' as status"; then
    echo "✅ ClickHouse authentication working!"
    echo ""
    echo "📝 Use this command to connect:"
    echo "   clickhouse-client --password ArgoCapital2025!"
    echo ""
    echo "📝 Or create database schema:"
    echo "   clickhouse-client --password ArgoCapital2025! < create_argo_schema.sql"
else
    echo "❌ Connection still failing"
    echo "📋 Check logs: tail -f logs/clickhouse-server.log"
    exit 1
fi
