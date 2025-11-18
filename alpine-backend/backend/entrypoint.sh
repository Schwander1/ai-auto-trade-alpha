#!/bin/bash
set -e

echo "🚀 Starting Alpine Backend..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0
until python3 -c "
import sys
import psycopg2
import os
from urllib.parse import urlparse

db_url = os.environ.get('DATABASE_URL', '')
if not db_url:
    print('ERROR: DATABASE_URL not set')
    sys.exit(1)

# Parse DATABASE_URL
parsed = urlparse(db_url)
try:
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path[1:] if parsed.path else 'postgres',
        connect_timeout=5
    )
    conn.close()
    print('✅ PostgreSQL is ready')
    sys.exit(0)
except Exception as e:
    print(f'⏳ PostgreSQL not ready yet: {e}')
    sys.exit(1)
" 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "❌ ERROR: PostgreSQL did not become ready after $MAX_RETRIES attempts"
        exit 1
    fi
    echo "   Retry $RETRY_COUNT/$MAX_RETRIES..."
    sleep 2
done

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
RETRY_COUNT=0
REDIS_HOST=${REDIS_HOST:-redis}
REDIS_PORT=${REDIS_PORT:-6379}
REDIS_PASSWORD=${REDIS_PASSWORD:-}

until python3 -c "
import sys
import redis
import os

redis_host = os.environ.get('REDIS_HOST', 'redis')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
redis_password = os.environ.get('REDIS_PASSWORD', '')

try:
    r = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password if redis_password else None,
        socket_connect_timeout=5,
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
        echo "❌ ERROR: Redis did not become ready after $MAX_RETRIES attempts"
        exit 1
    fi
    echo "   Retry $RETRY_COUNT/$MAX_RETRIES..."
    sleep 2
done

echo "✅ All dependencies are ready!"
echo "🚀 Starting application..."

# Execute the main command
exec "$@"

