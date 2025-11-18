#!/bin/bash
# Reusable dependency checking utility for startup scripts
# Usage: source this file and call wait_for_redis, wait_for_database, wait_for_service

set -e

# Configuration
MAX_RETRIES=${MAX_RETRIES:-30}
RETRY_DELAY=${RETRY_DELAY:-2}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

wait_for_redis() {
    local redis_host="${REDIS_HOST:-localhost}"
    local redis_port="${REDIS_PORT:-6379}"
    local redis_password="${REDIS_PASSWORD:-}"
    local service_name="${1:-Redis}"
    
    log_info "Waiting for $service_name at $redis_host:$redis_port..."
    
    local retry_count=0
    while [ $retry_count -lt $MAX_RETRIES ]; do
        if python3 -c "
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
" 2>/dev/null; then
            log_success "$service_name is ready"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $MAX_RETRIES ]; then
            log_info "  Retry $retry_count/$MAX_RETRIES..."
            sleep $RETRY_DELAY
        fi
    done
    
    log_error "$service_name did not become ready after $MAX_RETRIES attempts"
    return 1
}

wait_for_database() {
    local db_path="${1:-}"
    local service_name="${2:-Database}"
    
    log_info "Waiting for $service_name..."
    
    local retry_count=0
    while [ $retry_count -lt $MAX_RETRIES ]; do
        if python3 -c "
import sys
import sqlite3
from pathlib import Path
import os

# Determine database path
db_path = os.environ.get('DB_PATH', '')
if db_path:
    db_path = Path(db_path)
elif os.path.exists('/root/argo-production-prop-firm'):
    db_path = Path('/root/argo-production-prop-firm') / 'data' / 'signals.db'
elif os.path.exists('/root/argo-production-green'):
    db_path = Path('/root/argo-production-green') / 'data' / 'signals.db'
elif os.path.exists('/root/argo-production'):
    db_path = Path('/root/argo-production') / 'data' / 'signals.db'
else:
    # Fallback to workspace location
    db_path = Path('$(pwd)') / 'argo' / 'data' / 'signals.db'

# Ensure data directory exists
db_path.parent.mkdir(parents=True, exist_ok=True)

try:
    conn = sqlite3.connect(str(db_path), timeout=5.0)
    conn.execute('SELECT 1')
    conn.close()
    print('✅ Database is ready')
    sys.exit(0)
except Exception as e:
    print(f'⏳ Database not ready yet: {e}')
    sys.exit(1)
" 2>/dev/null; then
            log_success "$service_name is ready"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $MAX_RETRIES ]; then
            log_info "  Retry $retry_count/$MAX_RETRIES..."
            sleep $RETRY_DELAY
        fi
    done
    
    log_error "$service_name did not become ready after $MAX_RETRIES attempts"
    return 1
}

wait_for_service() {
    local url="${1:-http://localhost:8000/health}"
    local service_name="${2:-Service}"
    local max_retries="${3:-15}"
    
    log_info "Waiting for $service_name at $url..."
    
    local retry_count=0
    while [ $retry_count -lt $max_retries ]; do
        if curl -sf --max-time 5 "$url" > /dev/null 2>&1; then
            log_success "$service_name is ready"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            log_info "  Retry $retry_count/$max_retries..."
            sleep $RETRY_DELAY
        fi
    done
    
    log_warning "$service_name did not become ready after $max_retries attempts (may still be starting)"
    return 0  # Non-fatal
}

wait_for_postgres() {
    local host="${POSTGRES_HOST:-localhost}"
    local port="${POSTGRES_PORT:-5432}"
    local user="${POSTGRES_USER:-postgres}"
    local db="${POSTGRES_DB:-postgres}"
    local service_name="${1:-PostgreSQL}"
    
    log_info "Waiting for $service_name at $host:$port..."
    
    local retry_count=0
    while [ $retry_count -lt $MAX_RETRIES ]; do
        if python3 -c "
import sys
import psycopg2
import os

host = os.environ.get('POSTGRES_HOST', 'localhost')
port = int(os.environ.get('POSTGRES_PORT', 5432))
user = os.environ.get('POSTGRES_USER', 'postgres')
db = os.environ.get('POSTGRES_DB', 'postgres')
password = os.environ.get('POSTGRES_PASSWORD', '')

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db,
        connect_timeout=5
    )
    conn.close()
    print('✅ PostgreSQL is ready')
    sys.exit(0)
except Exception as e:
    print(f'⏳ PostgreSQL not ready yet: {e}')
    sys.exit(1)
" 2>/dev/null; then
            log_success "$service_name is ready"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $MAX_RETRIES ]; then
            log_info "  Retry $retry_count/$MAX_RETRIES..."
            sleep $RETRY_DELAY
        fi
    done
    
    log_error "$service_name did not become ready after $MAX_RETRIES attempts"
    return 1
}

# Export functions for use in other scripts
export -f wait_for_redis
export -f wait_for_database
export -f wait_for_service
export -f wait_for_postgres

