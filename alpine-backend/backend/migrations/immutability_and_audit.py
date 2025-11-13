"""
Database migration: Immutability and Audit Trail System
Implements comprehensive signal immutability, audit logging, retention tracking,
hash chains, latency tracking, and merkle roots for compliance and patent claims.

PATENT CLAIMS SUPPORTED:
- SHA-256 signal verification
- Immutable audit trail (database + backup + verification)
- Real-time delivery (<500ms latency tracking)
- CLI verification tools for independent auditing

COMPLIANCE REQUIREMENTS:
- 7-year data retention
- Append-only audit logs
- Tamper-evident storage
- Cryptographic verification

Run: python -m backend.migrations.immutability_and_audit
"""
from sqlalchemy import text
from backend.core.database import get_engine
import logging

logger = logging.getLogger(__name__)


def upgrade():
    """Apply all immutability and audit enhancements"""
    import os
    from urllib.parse import urlparse, urlunparse
    
    # Try to get engine, but handle connection issues
    try:
        engine = get_engine()
        # Test connection
        with engine.connect() as test_conn:
            test_conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.warning(f"Could not connect with get_engine(): {e}")
        logger.info("Attempting direct connection with hostname fix...")
        
        # Get DATABASE_URL and fix Docker hostname
        from backend.core.config import settings
        db_url = getattr(settings, 'DATABASE_URL', None) or os.getenv('DATABASE_URL')
        
        if not db_url:
            raise ValueError("DATABASE_URL not found in settings or environment")
        
        # Parse and fix hostname (Docker 'postgres' -> 'localhost')
        parsed = urlparse(db_url)
        if parsed.hostname == 'postgres':
            # Replace Docker hostname with localhost and use port 5433
            new_netloc = f"{parsed.username}:{parsed.password}@localhost:5433"
            db_url = urlunparse((
                parsed.scheme,
                new_netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            logger.info(f"Fixed DATABASE_URL: {parsed.scheme}://{parsed.username}:***@localhost:5433{parsed.path}")
        
        # Create new engine with fixed URL
        from sqlalchemy import create_engine
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as test_conn:
            test_conn.execute(text("SELECT 1"))
        logger.info("✅ Connection successful with fixed URL")
    
    logger.info("🔒 Starting immutability and audit migration...")
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            logger.info("🔒 Starting immutability and audit migration...")
            
            # 1. Create audit log table
            _create_audit_log_table(conn)
            
            # 2. Add new columns to signals table
            _add_signal_columns(conn)
            
            # 3. Create immutability trigger functions
            _create_immutability_triggers(conn)
            
            # 4. Create merkle roots table
            _create_merkle_roots_table(conn)
            
            # 5. Create integrity checksum log table
            _create_integrity_checksum_log(conn)
            
            # 6. Revoke UPDATE/DELETE permissions
            _revoke_modification_permissions(conn)
            
            # 7. Update existing signals with retention dates
            _update_retention_dates(conn)
            
            # 8. Initialize hash chain
            _initialize_hash_chain(conn)
            
            trans.commit()
            logger.info("✅ Immutability and audit migration completed successfully")
            
        except Exception as e:
            trans.rollback()
            logger.error(f"❌ Migration failed: {e}")
            raise


def downgrade():
    """Reverse migration (WARNING: Loses audit data)"""
    engine = get_engine()
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            logger.warning("⚠️  Reversing immutability migration (audit data will be lost)")
            
            # Drop triggers
            conn.execute(text("DROP TRIGGER IF EXISTS prevent_signal_modification_trigger ON signals"))
            conn.execute(text("DROP TRIGGER IF EXISTS log_signal_creation_trigger ON signals"))
            conn.execute(text("DROP TRIGGER IF EXISTS prevent_audit_log_modification_trigger ON signal_audit_log"))
            
            # Drop functions
            conn.execute(text("DROP FUNCTION IF EXISTS prevent_signal_modification() CASCADE"))
            conn.execute(text("DROP FUNCTION IF EXISTS log_signal_creation() CASCADE"))
            
            # Drop tables
            conn.execute(text("DROP TABLE IF EXISTS integrity_checksum_log CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS merkle_roots CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS signal_audit_log CASCADE"))
            
            # Remove columns from signals (if they exist)
            try:
                conn.execute(text("ALTER TABLE signals DROP COLUMN IF EXISTS retention_expires_at"))
                conn.execute(text("ALTER TABLE signals DROP COLUMN IF EXISTS previous_hash"))
                conn.execute(text("ALTER TABLE signals DROP COLUMN IF EXISTS chain_index"))
                conn.execute(text("ALTER TABLE signals DROP COLUMN IF EXISTS generation_latency_ms"))
                conn.execute(text("ALTER TABLE signals DROP COLUMN IF EXISTS delivery_latency_ms"))
                conn.execute(text("ALTER TABLE signals DROP COLUMN IF EXISTS server_timestamp"))
            except Exception as e:
                logger.warning(f"Error dropping columns (may not exist): {e}")
            
            # Restore permissions
            conn.execute(text("GRANT UPDATE, DELETE ON signals TO PUBLIC"))
            
            trans.commit()
            logger.info("✅ Migration reversed")
            
        except Exception as e:
            trans.rollback()
            logger.error(f"❌ Reversal failed: {e}")
            raise


def _create_audit_log_table(conn):
    """Create append-only audit log table"""
    logger.info("Creating signal_audit_log table...")
    
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS signal_audit_log (
            id BIGSERIAL PRIMARY KEY,
            signal_id INTEGER NOT NULL REFERENCES signals(id) ON DELETE CASCADE,
            action TEXT NOT NULL CHECK (action IN ('INSERT', 'UPDATE_ATTEMPT', 'DELETE_ATTEMPT', 'VERIFICATION')),
            old_data JSONB,
            new_data JSONB,
            verification_hash TEXT,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            user_id TEXT,
            ip_address TEXT,
            session_id TEXT,
            request_id TEXT,
            CONSTRAINT valid_action CHECK (action IN ('INSERT', 'UPDATE_ATTEMPT', 'DELETE_ATTEMPT', 'VERIFICATION'))
        )
    """))
    
    # Create indexes
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_audit_log_signal_id 
        ON signal_audit_log(signal_id)
    """))
    
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp 
        ON signal_audit_log(timestamp DESC)
    """))
    
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_audit_log_action 
        ON signal_audit_log(action)
    """))
    
    # Make audit log itself immutable
    conn.execute(text("""
        CREATE OR REPLACE FUNCTION prevent_audit_log_modification()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'Audit log is append-only. Modifications are not permitted for compliance and patent requirements.'
                USING ERRCODE = 'P0001';
        END;
        $$ LANGUAGE plpgsql;
    """))
    
    conn.execute(text("""
        CREATE TRIGGER prevent_audit_log_modification_trigger
        BEFORE UPDATE OR DELETE ON signal_audit_log
        FOR EACH ROW
        EXECUTE FUNCTION prevent_audit_log_modification()
    """))
    
    logger.info("✅ Audit log table created")


def _add_signal_columns(conn):
    """Add new columns to signals table"""
    logger.info("Adding new columns to signals table...")
    
    # Retention tracking
    conn.execute(text("""
        ALTER TABLE signals 
        ADD COLUMN IF NOT EXISTS retention_expires_at TIMESTAMP WITH TIME ZONE
    """))
    
    # Hash chain (blockchain-style)
    conn.execute(text("""
        ALTER TABLE signals 
        ADD COLUMN IF NOT EXISTS previous_hash VARCHAR(64)
    """))
    
    conn.execute(text("""
        ALTER TABLE signals 
        ADD COLUMN IF NOT EXISTS chain_index INTEGER
    """))
    
    # Latency tracking
    conn.execute(text("""
        ALTER TABLE signals 
        ADD COLUMN IF NOT EXISTS generation_latency_ms INTEGER
    """))
    
    conn.execute(text("""
        ALTER TABLE signals 
        ADD COLUMN IF NOT EXISTS delivery_latency_ms INTEGER
    """))
    
    conn.execute(text("""
        ALTER TABLE signals 
        ADD COLUMN IF NOT EXISTS server_timestamp DOUBLE PRECISION
    """))
    
    # Create indexes
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_signal_retention_expires 
        ON signals(retention_expires_at)
    """))
    
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_signal_chain_index 
        ON signals(chain_index)
    """))
    
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_signal_previous_hash 
        ON signals(previous_hash)
    """))
    
    logger.info("✅ Signal columns added")


def _create_immutability_triggers(conn):
    """Create trigger functions to prevent signal modification"""
    logger.info("Creating immutability triggers...")
    
    # Function to prevent signal modification
    conn.execute(text("""
        CREATE OR REPLACE FUNCTION prevent_signal_modification()
        RETURNS TRIGGER AS $$
        DECLARE
            audit_data JSONB;
            user_identifier TEXT;
            ip_addr TEXT;
            sess_id TEXT;
            req_id TEXT;
        BEGIN
            -- Get context information
            user_identifier := current_setting('app.user_id', TRUE);
            ip_addr := current_setting('app.ip_address', TRUE);
            sess_id := current_setting('app.session_id', TRUE);
            req_id := current_setting('app.request_id', TRUE);
            
            -- Log attempt to audit log
            audit_data := jsonb_build_object(
                'old_data', to_jsonb(OLD),
                'new_data', to_jsonb(NEW),
                'operation', TG_OP,
                'timestamp', NOW()
            );
            
            INSERT INTO signal_audit_log (
                signal_id, action, old_data, new_data, 
                user_id, ip_address, session_id, request_id, timestamp
            ) VALUES (
                OLD.id,
                CASE 
                    WHEN TG_OP = 'UPDATE' THEN 'UPDATE_ATTEMPT'
                    WHEN TG_OP = 'DELETE' THEN 'DELETE_ATTEMPT'
                END,
                to_jsonb(OLD),
                CASE WHEN TG_OP = 'UPDATE' THEN to_jsonb(NEW) ELSE NULL END,
                COALESCE(user_identifier, 'system'),
                COALESCE(ip_addr, 'unknown'),
                COALESCE(sess_id, 'unknown'),
                COALESCE(req_id, 'unknown'),
                NOW()
            );
            
            -- Raise exception to prevent modification
            RAISE EXCEPTION 
                'Signals are immutable for compliance and patent requirements. '
                'UPDATE/DELETE operations are not permitted. '
                'This action has been logged in the audit trail. '
                'Reference: Patent Claim - Immutable Audit Trail'
                USING ERRCODE = 'P0001';
        END;
        $$ LANGUAGE plpgsql;
    """))
    
    # Trigger to prevent UPDATE/DELETE
    conn.execute(text("""
        DROP TRIGGER IF EXISTS prevent_signal_modification_trigger ON signals
    """))
    
    conn.execute(text("""
        CREATE TRIGGER prevent_signal_modification_trigger
        BEFORE UPDATE OR DELETE ON signals
        FOR EACH ROW
        EXECUTE FUNCTION prevent_signal_modification()
    """))
    
    # Function to auto-log signal creation
    conn.execute(text("""
        CREATE OR REPLACE FUNCTION log_signal_creation()
        RETURNS TRIGGER AS $$
        DECLARE
            user_identifier TEXT;
            ip_addr TEXT;
            sess_id TEXT;
            req_id TEXT;
        BEGIN
            -- Get context information
            user_identifier := current_setting('app.user_id', TRUE);
            ip_addr := current_setting('app.ip_address', TRUE);
            sess_id := current_setting('app.session_id', TRUE);
            req_id := current_setting('app.request_id', TRUE);
            
            -- Log signal creation
            INSERT INTO signal_audit_log (
                signal_id, action, new_data, verification_hash,
                user_id, ip_address, session_id, request_id, timestamp
            ) VALUES (
                NEW.id,
                'INSERT',
                to_jsonb(NEW),
                NEW.verification_hash,
                COALESCE(user_identifier, 'system'),
                COALESCE(ip_addr, 'unknown'),
                COALESCE(sess_id, 'unknown'),
                COALESCE(req_id, 'unknown'),
                NOW()
            );
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """))
    
    # Trigger to auto-log INSERT
    conn.execute(text("""
        DROP TRIGGER IF EXISTS log_signal_creation_trigger ON signals
    """))
    
    conn.execute(text("""
        CREATE TRIGGER log_signal_creation_trigger
        AFTER INSERT ON signals
        FOR EACH ROW
        EXECUTE FUNCTION log_signal_creation()
    """))
    
    logger.info("✅ Immutability triggers created")


def _create_merkle_roots_table(conn):
    """Create merkle roots table for batch verification"""
    logger.info("Creating merkle_roots table...")
    
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS merkle_roots (
            id SERIAL PRIMARY KEY,
            batch_date DATE NOT NULL UNIQUE,
            merkle_root TEXT NOT NULL,
            signal_count INTEGER NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        )
    """))
    
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_merkle_roots_batch_date 
        ON merkle_roots(batch_date DESC)
    """))
    
    logger.info("✅ Merkle roots table created")


def _create_integrity_checksum_log(conn):
    """Create integrity checksum log table"""
    logger.info("Creating integrity_checksum_log table...")
    
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS integrity_checksum_log (
            id SERIAL PRIMARY KEY,
            check_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            total_signals INTEGER NOT NULL,
            table_checksum TEXT,
            sample_size INTEGER,
            failed_verifications INTEGER DEFAULT 0,
            status TEXT NOT NULL CHECK (status IN ('PASS', 'FAIL', 'WARNING')),
            notes TEXT
        )
    """))
    
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_integrity_check_timestamp 
        ON integrity_checksum_log(check_timestamp DESC)
    """))
    
    logger.info("✅ Integrity checksum log table created")


def _revoke_modification_permissions(conn):
    """Revoke UPDATE/DELETE permissions from PUBLIC"""
    logger.info("Revoking modification permissions...")
    
    try:
        conn.execute(text("REVOKE UPDATE, DELETE ON signals FROM PUBLIC"))
        conn.execute(text("REVOKE UPDATE, DELETE ON signal_audit_log FROM PUBLIC"))
        logger.info("✅ Permissions revoked")
    except Exception as e:
        logger.warning(f"⚠️  Permission revocation warning (may not be applicable): {e}")


def _update_retention_dates(conn):
    """Update existing signals with retention expiration dates"""
    logger.info("Updating retention dates for existing signals...")
    
    conn.execute(text("""
        UPDATE signals 
        SET retention_expires_at = created_at + INTERVAL '7 years'
        WHERE retention_expires_at IS NULL
    """))
    
    result = conn.execute(text("SELECT COUNT(*) FROM signals WHERE retention_expires_at IS NOT NULL"))
    count = result.scalar()
    logger.info(f"✅ Updated {count} signals with retention dates")


def _initialize_hash_chain(conn):
    """Initialize hash chain for existing signals"""
    logger.info("Initializing hash chain...")
    
    # Get all signals ordered by creation time
    result = conn.execute(text("""
        SELECT id, verification_hash, created_at 
        FROM signals 
        ORDER BY created_at ASC, id ASC
    """))
    
    signals = result.fetchall()
    previous_hash = None
    
    for idx, (signal_id, verification_hash, created_at) in enumerate(signals):
        conn.execute(text("""
            UPDATE signals 
            SET chain_index = :chain_index,
                previous_hash = :previous_hash
            WHERE id = :signal_id
        """), {
            'chain_index': idx,
            'previous_hash': previous_hash,
            'signal_id': signal_id
        })
        
        previous_hash = verification_hash
    
    logger.info(f"✅ Initialized hash chain for {len(signals)} signals")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()

