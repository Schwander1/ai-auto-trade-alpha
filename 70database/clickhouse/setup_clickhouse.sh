#!/bin/bash
# ARGO Capital ClickHouse Professional Setup

echo "🚀 ARGO Capital ClickHouse Integration Setup"

# Install ClickHouse via Homebrew
if ! command -v clickhouse &> /dev/null; then
    echo "📦 Installing ClickHouse..."
    brew install clickhouse
else
    echo "✅ ClickHouse already installed"
fi

# Create ClickHouse configuration
mkdir -p config data logs

# Professional ClickHouse configuration for trading data
cat > config/config.xml << 'CLICKHOUSE_CONFIG'
<?xml version="1.0"?>
<clickhouse>
    <logger>
        <level>information</level>
        <log>/Users/dylanneuenschwander/projects/ARGO-Master-Unified/70database/clickhouse/logs/clickhouse-server.log</log>
        <errorlog>/Users/dylanneuenschwander/projects/ARGO-Master-Unified/70database/clickhouse/logs/clickhouse-server.err.log</errorlog>
        <size>1000M</size>
        <count>3</count>
    </logger>
    
    <http_port>8123</http_port>
    <tcp_port>9000</tcp_port>
    
    <path>/Users/dylanneuenschwander/projects/ARGO-Master-Unified/70database/clickhouse/data/</path>
    <tmp_path>/tmp/</tmp_path>
    
    <users>
        <argo_user>
            <password>ArgoCapital2025!</password>
            <networks>
                <ip>::1</ip>
                <ip>127.0.0.1</ip>
            </networks>
            <profile>default</profile>
            <quota>default</quota>
        </argo_user>
    </users>
    
    <profiles>
        <default>
            <max_memory_usage>10000000000</max_memory_usage>
            <use_uncompressed_cache>0</use_uncompressed_cache>
            <load_balancing>random</load_balancing>
        </default>
    </profiles>
</clickhouse>
CLICKHOUSE_CONFIG

echo "✅ ClickHouse configuration created"
echo "🔧 Starting ClickHouse server..."

# Start ClickHouse server
clickhouse-server --config-file=config/config.xml --daemon

sleep 5

echo "🎯 Creating ARGO Capital database schema..."
