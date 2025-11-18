"""
Database migration script to add performance indexes
Run this after deploying the updated models
"""
from sqlalchemy import text
from backend.core.database import engine
import logging

logger = logging.getLogger(__name__)

def add_indexes():
    """Add all performance indexes"""
    with engine.connect() as conn:
        # Signal indexes
        logger.info("Adding signal indexes...")
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_signal_active_confidence_created 
                ON signals(is_active, confidence, created_at DESC)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_signal_symbol_created 
                ON signals(symbol, created_at DESC)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_signal_confidence 
                ON signals(confidence)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_signal_is_active 
                ON signals(is_active)
            """))
            conn.commit()
            logger.info("✅ Signal indexes added")
        except Exception as e:
            logger.error(f"⚠️ Signal indexes error: {e}")
            conn.rollback()
        
        # User indexes
        logger.info("Adding user indexes...")
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_user_tier_active 
                ON users(tier, is_active)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_user_created_at 
                ON users(created_at DESC)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_user_tier 
                ON users(tier)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_user_is_active 
                ON users(is_active)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_user_stripe_customer_id 
                ON users(stripe_customer_id)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_user_stripe_subscription_id 
                ON users(stripe_subscription_id)
            """))
            conn.commit()
            logger.info("✅ User indexes added")
        except Exception as e:
            logger.error(f"⚠️ User indexes error: {e}")
            conn.rollback()
        
        # Notification indexes
        logger.info("Adding notification indexes...")
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_notif_user_read_created 
                ON notifications(user_id, is_read, created_at DESC)
            """))
            conn.commit()
            logger.info("✅ Notification indexes added")
        except Exception as e:
            logger.error(f"⚠️ Notification indexes error: {e}")
            conn.rollback()
        
        logger.info("✅ All indexes migration complete!")

if __name__ == "__main__":
    add_indexes()

