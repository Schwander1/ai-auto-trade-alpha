#!/bin/bash
# Quick fix for ClickHouse Authentication

echo "🔧 ARGO Capital ClickHouse Quick Fix"

cd "$(dirname "$0")"

# Stop any running ClickHouse
pkill -f clickhouse-server
sleep 2

# Create minimal config that allows no-password access
mkdir -p config data logs user_files /tmp/clickhouse

cat > config/config.xml << 'EOF'
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
    
    <listen_host>127.0.0.1</listen_host>
    
    <users_config>users.xml</users_config>
</clickhouse>
EOF

cat > config/users.xml << 'EOF'
<?xml version="1.0"?>
<clickhouse>
    <profiles>
        <default>
            <max_memory_usage>10000000000</max_memory_usage>
            <use_uncompressed_cache>0</use_uncompressed_cache>
            <load_balancing>random</load_balancing>
        </default>
    </profiles>
    
    <users>
        <default>
            <password></password>
            <networks>
                <ip>::1</ip>
                <ip>127.0.0.1</ip>
            </networks>
            <profile>default</profile>
            <quota>default</quota>
        </default>
    </users>
    
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
</clickhouse>
EOF

echo "✅ Configuration created (no password required)"

# Start server
echo "🚀 Starting ClickHouse server..."
clickhouse-server --config-file=config/config.xml --daemon --pid-file=clickhouse-server.pid

# Wait for startup
echo "⏳ Waiting for server to start..."
sleep 10

# Test connection
echo "🔍 Testing connection..."
if clickhouse-client --query "SELECT 'ClickHouse is running!' as status"; then
    echo "✅ ClickHouse is ready!"
    echo ""
    echo "📝 Connection command (no password needed):"
    echo "   clickhouse-client"
    echo ""
    echo "📝 Create database schema:"
    echo "   clickhouse-client < create_argo_schema.sql"
else
    echo "❌ Failed to connect"
    echo "📋 Check logs:"
    tail -20 logs/clickhouse-server.log
    exit 1
fi
