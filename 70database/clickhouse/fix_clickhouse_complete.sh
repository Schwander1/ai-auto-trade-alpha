#!/usr/bin/env bash
set -e

echo "🧹 Cleaning up old ClickHouse processes and files..."
pkill -f clickhouse || true
rm -rf data/ logs/ config/ *.pid

mkdir -p data logs config

echo "📝 Creating minimal ClickHouse config..."
cat > config/simple_config.xml << 'CFG'
<clickhouse>
  <logger>
    <log>logs/server.log</log>
    <errorlog>logs/error.log</errorlog>
    <level>debug</level>
  </logger>
  <http_port>8123</http_port>
  <tcp_port>9000</tcp_port>
  <path>data/</path>
  <tmp_path>data/tmp/</tmp_path>
  <user_files_path>data/user_files/</user_files_path>
  <format_schema_path>data/format_schemas/</format_schema_path>
  <listen_host>::</listen_host>
  <max_connections>100</max_connections>
  <keep_alive_timeout>3</keep_alive_timeout>
  <max_concurrent_queries>100</max_concurrent_queries>
  <uncompressed_cache_size>8589934592</uncompressed_cache_size>
  <mark_cache_size>5368709120</mark_cache_size>
  <users>
    <default>
      <password></password>
      <networks><ip>::/0</ip></networks>
      <profile>default</profile>
      <quota>default</quota>
    </default>
  </users>
  <profiles>
    <default><max_memory_usage>10000000000</max_memory_usage></default>
  </profiles>
  <quotas>
    <default><interval><duration>3600</duration></interval></default>
  </quotas>
</clickhouse>
CFG

echo "🚀 Starting ClickHouse on port 8123..."
nohup clickhouse-server --config-file=config/simple_config.xml > logs/startup.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > clickhouse.pid

echo "⏳ Waiting for ClickHouse to start..."
sleep 15

echo "🔍 Testing ClickHouse connection..."
if clickhouse-client --port 9000 --query "SELECT 'ARGO Capital ClickHouse Ready!' as status"; then
  echo "✅ ClickHouse is working (PID=$SERVER_PID)"
  exit 0
else
  echo "❌ Connection failed. Recent logs:"
  tail -50 logs/startup.log || true
  tail -50 logs/server.log || true
  exit 1
fi
