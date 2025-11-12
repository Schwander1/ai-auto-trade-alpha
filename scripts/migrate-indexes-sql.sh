#!/bin/bash
# Direct SQL migration script for database indexes
# Can be run via psql or docker exec

set -e

echo "🗄️  Creating Database Indexes (Direct SQL)"
echo "=========================================="
echo ""

# Database connection details
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5433}"
DB_NAME="${DB_NAME:-alpine_prod}"
DB_USER="${DB_USER:-alpine_user}"
DB_PASSWORD="${DB_PASSWORD:-AlpineSecure2025!}"

export PGPASSWORD="$DB_PASSWORD"

SQL_COMMANDS="
-- Signal indexes
CREATE INDEX IF NOT EXISTS idx_signal_active_confidence_created 
ON signals(is_active, confidence, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_signal_symbol_created 
ON signals(symbol, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_signal_confidence 
ON signals(confidence);

CREATE INDEX IF NOT EXISTS idx_signal_is_active 
ON signals(is_active);

-- User indexes
CREATE INDEX IF NOT EXISTS idx_user_tier_active 
ON users(tier, is_active);

CREATE INDEX IF NOT EXISTS idx_user_created_at 
ON users(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_user_tier 
ON users(tier);

CREATE INDEX IF NOT EXISTS idx_user_is_active 
ON users(is_active);

CREATE INDEX IF NOT EXISTS idx_user_stripe_customer_id 
ON users(stripe_customer_id);

CREATE INDEX IF NOT EXISTS idx_user_stripe_subscription_id 
ON users(stripe_subscription_id);

-- Notification indexes
CREATE INDEX IF NOT EXISTS idx_notif_user_read_created 
ON notifications(user_id, is_read, created_at DESC);
"

echo "Connecting to database: $DB_NAME@$DB_HOST:$DB_PORT"
echo ""

psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" << EOF
$SQL_COMMANDS

-- Verify indexes were created
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'public'
  AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;
EOF

echo ""
echo "✅ Index migration complete!"

