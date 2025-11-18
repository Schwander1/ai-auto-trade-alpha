#!/bin/bash
# Wait for dependencies (Redis, database) to be ready before starting Argo service
# This script is used as ExecStartPre in systemd services

set -e

SERVICE_NAME="${1:-argo-trading}"
MAX_RETRIES=30
RETRY_DELAY=2

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Waiting for dependencies for $SERVICE_NAME..."

# Determine Redis configuration from environment or defaults
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"

# Wait for Redis
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Checking Redis at $REDIS_HOST:$REDIS_PORT..."
RETRY_COUNT=0
until python3 -c "
import sys
import redis
import os

redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
redis_password = os.environ.get('REDIS_PASSWORD', '')

try:
    r = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password if redis_password else None,
        socket_connect_timeout=5,
        socket_timeout=5,
        decode_responses=True
    )
    r.ping()
    print('✅ Redis is ready')
    sys.exit(0)
except Exception as e:
    print(f'⏳ Redis not ready yet: {e}')
    sys.exit(1)
" 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] ❌ ERROR: Redis did not become ready after $MAX_RETRIES attempts"
        exit 1
    fi
    echo "[$(date +'%Y-%m-%d %H:%M:%S')]   Retry $RETRY_COUNT/$MAX_RETRIES..."
    sleep $RETRY_DELAY
done

# Wait for database (SQLite file should exist and be writable)
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Checking database..."
RETRY_COUNT=0
until python3 -c "
import sys
import sqlite3
from pathlib import Path
import os

# Determine database path
if os.path.exists('/root/argo-production-prop-firm'):
    db_path = Path('/root/argo-production-prop-firm') / 'data' / 'signals.db'
elif os.path.exists('/root/argo-production-green'):
    db_path = Path('/root/argo-production-green') / 'data' / 'signals.db'
elif os.path.exists('/root/argo-production'):
    db_path = Path('/root/argo-production') / 'data' / 'signals.db'
else:
    # Fallback to workspace location
    db_path = Path('/root/argo-alpine-workspace/argo/data/signals.db')

# Ensure data directory exists
db_path.parent.mkdir(parents=True, exist_ok=True)

try:
    # Try to connect and write to database
    conn = sqlite3.connect(str(db_path), timeout=5.0)
    conn.execute('SELECT 1')
    conn.close()
    print('✅ Database is ready')
    sys.exit(0)
except Exception as e:
    print(f'⏳ Database not ready yet: {e}')
    sys.exit(1)
" 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] ❌ ERROR: Database did not become ready after $MAX_RETRIES attempts"
        exit 1
    fi
    echo "[$(date +'%Y-%m-%d %H:%M:%S')]   Retry $RETRY_COUNT/$MAX_RETRIES..."
    sleep $RETRY_DELAY
done

echo "[$(date +'%Y-%m-%d %H:%M:%S')] ✅ All dependencies are ready for $SERVICE_NAME"
exit 0

