"""
Database migration: Add enum columns and new constraints
Converts string columns to enums and adds validation constraints

Run: python -m backend.migrations.add_enum_columns_and_constraints
"""
from sqlalchemy import text, create_engine
from backend.core.database import get_engine
from backend.core.config import settings
import logging

logger = logging.getLogger(__name__)


def upgrade():
    """Add enum types and constraints, migrate existing data"""
    try:
        engine = get_engine()
    except Exception:
        engine = create_engine(settings.DATABASE_URL)
    
    with engine.begin() as conn:
        logger.info("🔧 Starting enum columns and constraints migration...")
        
        # Create enum types
        logger.info("Creating enum types...")
        try:
            # SignalAction enum
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE signalaction AS ENUM ('BUY', 'SELL');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            
            # NotificationType enum
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE notificationtype AS ENUM ('info', 'warning', 'success', 'error', 'system');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            
            # BacktestStatus enum
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE backteststatus AS ENUM ('running', 'completed', 'failed', 'cancelled');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            
            logger.info("✅ Enum types created")
        except Exception as e:
            logger.warning(f"⚠️  Enum types may already exist: {e}")
        
        # Migrate signals.action to enum
        logger.info("Migrating signals.action to enum...")
        try:
            # Check if column is already enum type
            result = conn.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'signals' AND column_name = 'action';
            """))
            row = result.fetchone()
            
            if row and 'enum' not in row[0].lower():
                # Add temporary column
                conn.execute(text("""
                    ALTER TABLE signals 
                    ADD COLUMN IF NOT EXISTS action_enum signalaction;
                """))
                
                # Migrate data
                conn.execute(text("""
                    UPDATE signals 
                    SET action_enum = CASE 
                        WHEN UPPER(action) = 'BUY' THEN 'BUY'::signalaction
                        WHEN UPPER(action) = 'SELL' THEN 'SELL'::signalaction
                        ELSE 'BUY'::signalaction
                    END
                    WHERE action_enum IS NULL;
                """))
                
                # Drop old column and rename new one
                conn.execute(text("ALTER TABLE signals DROP COLUMN IF EXISTS action CASCADE"))
                conn.execute(text("ALTER TABLE signals RENAME COLUMN action_enum TO action"))
                conn.execute(text("ALTER TABLE signals ALTER COLUMN action SET NOT NULL"))
                logger.info("✅ signals.action migrated to enum")
            else:
                logger.info("✅ signals.action already enum type")
        except Exception as e:
            logger.error(f"❌ Error migrating signals.action: {e}")
            raise
        
        # Migrate notifications.type to enum
        logger.info("Migrating notifications.type to enum...")
        try:
            result = conn.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'notifications' AND column_name = 'type';
            """))
            row = result.fetchone()
            
            if row and 'enum' not in row[0].lower():
                # Add temporary column
                conn.execute(text("""
                    ALTER TABLE notifications 
                    ADD COLUMN IF NOT EXISTS type_enum notificationtype;
                """))
                
                # Migrate data (default to 'info' if invalid)
                conn.execute(text("""
                    UPDATE notifications 
                    SET type_enum = CASE 
                        WHEN LOWER(type) = 'info' THEN 'info'::notificationtype
                        WHEN LOWER(type) = 'warning' THEN 'warning'::notificationtype
                        WHEN LOWER(type) = 'success' THEN 'success'::notificationtype
                        WHEN LOWER(type) = 'error' THEN 'error'::notificationtype
                        WHEN LOWER(type) = 'system' THEN 'system'::notificationtype
                        ELSE 'info'::notificationtype
                    END
                    WHERE type_enum IS NULL;
                """))
                
                # Set default for new rows
                conn.execute(text("""
                    ALTER TABLE notifications 
                    ALTER COLUMN type_enum SET DEFAULT 'info'::notificationtype;
                """))
                
                # Drop old column and rename new one
                conn.execute(text("ALTER TABLE notifications DROP COLUMN IF EXISTS type CASCADE"))
                conn.execute(text("ALTER TABLE notifications RENAME COLUMN type_enum TO type"))
                conn.execute(text("ALTER TABLE notifications ALTER COLUMN type SET NOT NULL"))
                logger.info("✅ notifications.type migrated to enum")
            else:
                logger.info("✅ notifications.type already enum type")
        except Exception as e:
            logger.error(f"❌ Error migrating notifications.type: {e}")
            raise
        
        # Migrate backtests.status to enum
        logger.info("Migrating backtests.status to enum...")
        try:
            result = conn.execute(text("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'backtests' AND column_name = 'status';
            """))
            row = result.fetchone()
            
            if row and 'enum' not in row[0].lower():
                # Add temporary column
                conn.execute(text("""
                    ALTER TABLE backtests 
                    ADD COLUMN IF NOT EXISTS status_enum backteststatus;
                """))
                
                # Migrate data (default to 'running' if invalid)
                conn.execute(text("""
                    UPDATE backtests 
                    SET status_enum = CASE 
                        WHEN LOWER(status) = 'running' THEN 'running'::backteststatus
                        WHEN LOWER(status) = 'completed' THEN 'completed'::backteststatus
                        WHEN LOWER(status) = 'failed' THEN 'failed'::backteststatus
                        WHEN LOWER(status) = 'cancelled' THEN 'cancelled'::backteststatus
                        ELSE 'running'::backteststatus
                    END
                    WHERE status_enum IS NULL;
                """))
                
                # Set default for new rows
                conn.execute(text("""
                    ALTER TABLE backtests 
                    ALTER COLUMN status_enum SET DEFAULT 'running'::backteststatus;
                """))
                
                # Drop old column and rename new one
                conn.execute(text("ALTER TABLE backtests DROP COLUMN IF EXISTS status CASCADE"))
                conn.execute(text("ALTER TABLE backtests RENAME COLUMN status_enum TO status"))
                conn.execute(text("ALTER TABLE backtests ALTER COLUMN status SET NOT NULL"))
                logger.info("✅ backtests.status migrated to enum")
            else:
                logger.info("✅ backtests.status already enum type")
        except Exception as e:
            logger.error(f"❌ Error migrating backtests.status: {e}")
            raise
        
        # Add string length constraints
        logger.info("Adding string length constraints...")
        try:
            # Users table
            conn.execute(text("""
                ALTER TABLE users 
                ALTER COLUMN email TYPE VARCHAR(255),
                ALTER COLUMN hashed_password TYPE VARCHAR(255),
                ALTER COLUMN full_name TYPE VARCHAR(255),
                ALTER COLUMN totp_secret TYPE VARCHAR(32),
                ALTER COLUMN backup_codes TYPE VARCHAR(1000),
                ALTER COLUMN stripe_customer_id TYPE VARCHAR(255),
                ALTER COLUMN stripe_subscription_id TYPE VARCHAR(255);
            """))
            
            # Signals table
            conn.execute(text("""
                ALTER TABLE signals 
                ALTER COLUMN symbol TYPE VARCHAR(20),
                ALTER COLUMN verification_hash TYPE VARCHAR(64),
                ALTER COLUMN previous_hash TYPE VARCHAR(64);
            """))
            
            # Notifications table
            conn.execute(text("""
                ALTER TABLE notifications 
                ALTER COLUMN title TYPE VARCHAR(255);
            """))
            
            # Backtests table
            conn.execute(text("""
                ALTER TABLE backtests 
                ALTER COLUMN backtest_id TYPE VARCHAR(255),
                ALTER COLUMN symbol TYPE VARCHAR(20),
                ALTER COLUMN strategy TYPE VARCHAR(100);
            """))
            
            # Roles table
            conn.execute(text("""
                ALTER TABLE roles 
                ALTER COLUMN name TYPE VARCHAR(100),
                ALTER COLUMN description TYPE VARCHAR(500);
            """))
            
            # Permissions table
            conn.execute(text("""
                ALTER TABLE permissions 
                ALTER COLUMN name TYPE VARCHAR(100),
                ALTER COLUMN description TYPE VARCHAR(500);
            """))
            
            logger.info("✅ String length constraints added")
        except Exception as e:
            logger.warning(f"⚠️  Some string constraints may already exist: {e}")
        
        # Add check constraints
        logger.info("Adding check constraints...")
        try:
            # Signals constraints
            conn.execute(text("""
                ALTER TABLE signals 
                DROP CONSTRAINT IF EXISTS check_confidence_range,
                ADD CONSTRAINT check_confidence_range 
                    CHECK (confidence >= 0 AND confidence <= 1);
            """))
            
            conn.execute(text("""
                ALTER TABLE signals 
                DROP CONSTRAINT IF EXISTS check_price_positive,
                ADD CONSTRAINT check_price_positive 
                    CHECK (price > 0);
            """))
            
            conn.execute(text("""
                ALTER TABLE signals 
                DROP CONSTRAINT IF EXISTS check_target_price_positive,
                ADD CONSTRAINT check_target_price_positive 
                    CHECK (target_price IS NULL OR target_price > 0);
            """))
            
            conn.execute(text("""
                ALTER TABLE signals 
                DROP CONSTRAINT IF EXISTS check_stop_loss_positive,
                ADD CONSTRAINT check_stop_loss_positive 
                    CHECK (stop_loss IS NULL OR stop_loss > 0);
            """))
            
            # Backtests constraints
            conn.execute(text("""
                ALTER TABLE backtests 
                DROP CONSTRAINT IF EXISTS check_date_range,
                ADD CONSTRAINT check_date_range 
                    CHECK (end_date > start_date);
            """))
            
            conn.execute(text("""
                ALTER TABLE backtests 
                DROP CONSTRAINT IF EXISTS check_initial_capital_positive,
                ADD CONSTRAINT check_initial_capital_positive 
                    CHECK (initial_capital > 0);
            """))
            
            conn.execute(text("""
                ALTER TABLE backtests 
                DROP CONSTRAINT IF EXISTS check_risk_per_trade_range,
                ADD CONSTRAINT check_risk_per_trade_range 
                    CHECK (risk_per_trade >= 0 AND risk_per_trade <= 1);
            """))
            
            logger.info("✅ Check constraints added")
        except Exception as e:
            logger.warning(f"⚠️  Some check constraints may already exist: {e}")
        
        # Add missing indexes
        logger.info("Adding missing indexes...")
        try:
            # Signal indexes
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_signal_action 
                ON signals(action);
            """))
            
            # Notification indexes
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_notif_type_created 
                ON notifications(type, created_at DESC);
            """))
            
            # Role indexes
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_role_system 
                ON roles(is_system);
            """))
            
            logger.info("✅ Missing indexes added")
        except Exception as e:
            logger.warning(f"⚠️  Some indexes may already exist: {e}")
        
        logger.info("✅ Enum columns and constraints migration completed successfully")


def downgrade():
    """Reverse migration (converts enums back to strings)"""
    try:
        engine = get_engine()
    except Exception:
        engine = create_engine(settings.DATABASE_URL)
    
    with engine.begin() as conn:
        logger.warning("⚠️  Reversing enum migration (converting enums back to strings)")
        
        # Convert signals.action back to string
        try:
            conn.execute(text("""
                ALTER TABLE signals 
                ADD COLUMN IF NOT EXISTS action_str VARCHAR(10);
            """))
            conn.execute(text("""
                UPDATE signals SET action_str = action::text;
            """))
            conn.execute(text("ALTER TABLE signals DROP COLUMN IF EXISTS action CASCADE"))
            conn.execute(text("ALTER TABLE signals RENAME COLUMN action_str TO action"))
            logger.info("✅ signals.action reverted to string")
        except Exception as e:
            logger.error(f"❌ Error reverting signals.action: {e}")
        
        # Convert notifications.type back to string
        try:
            conn.execute(text("""
                ALTER TABLE notifications 
                ADD COLUMN IF NOT EXISTS type_str VARCHAR(20);
            """))
            conn.execute(text("""
                UPDATE notifications SET type_str = type::text;
            """))
            conn.execute(text("ALTER TABLE notifications DROP COLUMN IF EXISTS type CASCADE"))
            conn.execute(text("ALTER TABLE notifications RENAME COLUMN type_str TO type"))
            logger.info("✅ notifications.type reverted to string")
        except Exception as e:
            logger.error(f"❌ Error reverting notifications.type: {e}")
        
        # Convert backtests.status back to string
        try:
            conn.execute(text("""
                ALTER TABLE backtests 
                ADD COLUMN IF NOT EXISTS status_str VARCHAR(20);
            """))
            conn.execute(text("""
                UPDATE backtests SET status_str = status::text;
            """))
            conn.execute(text("ALTER TABLE backtests DROP COLUMN IF EXISTS status CASCADE"))
            conn.execute(text("ALTER TABLE backtests RENAME COLUMN status_str TO status"))
            logger.info("✅ backtests.status reverted to string")
        except Exception as e:
            logger.error(f"❌ Error reverting backtests.status: {e}")
        
        # Drop enum types
        try:
            conn.execute(text("DROP TYPE IF EXISTS signalaction CASCADE"))
            conn.execute(text("DROP TYPE IF EXISTS notificationtype CASCADE"))
            conn.execute(text("DROP TYPE IF EXISTS backteststatus CASCADE"))
            logger.info("✅ Enum types dropped")
        except Exception as e:
            logger.warning(f"⚠️  Error dropping enum types: {e}")
        
        logger.info("✅ Migration reversed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    upgrade()
