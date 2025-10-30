#!/bin/bash
# ARGO Capital ClickHouse Setup - macOS ARM64 Fixed Version

echo "🚀 ARGO Capital ClickHouse Integration Setup"

# Create directories
mkdir -p config data logs

# Create ClickHouse configuration optimized for macOS ARM64
cat > config/config.xml << 'CLICKHOUSE_CONFIG'
<?xml version="1.0"?>
<clickhouse>
    <logger>
        <level>information</level>
        <log>./logs/clickhouse-server.log</log>
        <errorlog>./logs/clickhouse-server.err.log</errorlog>
        <size>1000M</size>
        <count>3</count>
    </logger>
    
    <http_port>8123</http_port>
    <tcp_port>9000</tcp_port>
    
    <path>./data/</path>
    <tmp_path>/tmp/clickhouse/</tmp_path>
    <user_files_path>./user_files/</user_files_path>
    
    <users>
        <default>
            <password>ArgoCapital2025!</password>
            <networks>
                <ip>::1</ip>
                <ip>127.0.0.1</ip>
            </networks>
            <profile>default</profile>
            <quota>default</quota>
        </default>
    </users>
    
    <profiles>
        <default>
            <max_memory_usage>10000000000</max_memory_usage>
            <use_uncompressed_cache>0</use_uncompressed_cache>
            <load_balancing>random</load_balancing>
        </default>
    </profiles>
    
    <quotas>
        <default>
            <interval>
                <duration>3600</duration>
                <queries>0</queries>
                <errors>0</errors>
                <result_rows>0</result_rows>
                <read_rows>0</read_rows>
                <execution_time>0</execution_time>
            </interval>
        </default>
    </quotas>
    
    <listen_host>127.0.0.1</listen_host>
    
    <!-- Disable system tables that might cause issues on macOS -->
    <system_profile>default</system_profile>
    
</clickhouse>
CLICKHOUSE_CONFIG

# Create user files directory
mkdir -p user_files

echo "✅ ClickHouse configuration created"

# Start ClickHouse server in background
echo "🔧 Starting ClickHouse server..."

# Create startup script for ClickHouse
cat > start_clickhouse.sh << 'START_SCRIPT'
#!/bin/bash
cd "$(dirname "$0")"
mkdir -p /tmp/clickhouse
clickhouse-server --config-file=config/config.xml --daemon --pid-file=clickhouse-server.pid
START_SCRIPT

chmod +x start_clickhouse.sh
./start_clickhouse.sh

# Wait for server to start
echo "⏳ Waiting for ClickHouse to start..."
sleep 10

# Test connection
echo "🔍 Testing ClickHouse connection..."
if clickhouse-client --password ArgoCapital2025! --query "SELECT 1" > /dev/null 2>&1; then
    echo "✅ ClickHouse server running successfully on port 8123"
    echo "🎯 ARGO Capital ClickHouse ready"
    echo "📝 Connection command: clickhouse-client --password ArgoCapital2025!"
else
    echo "❌ ClickHouse connection test failed"
    echo "📋 Check logs: tail -f logs/clickhouse-server.log"
fi

