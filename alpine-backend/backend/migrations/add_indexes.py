"""
Database migration script to add performance indexes
Run this after deploying the updated models
"""
from sqlalchemy import text
from backend.core.database import engine

def add_indexes():
    """Add all performance indexes"""
    with engine.connect() as conn:
        # Signal indexes
        print("Adding signal indexes...")
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
            print("✅ Signal indexes added")
        except Exception as e:
            print(f"⚠️ Signal indexes error: {e}")
            conn.rollback()
        
        # User indexes
        print("Adding user indexes...")
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
            print("✅ User indexes added")
        except Exception as e:
            print(f"⚠️ User indexes error: {e}")
            conn.rollback()
        
        # Notification indexes
        print("Adding notification indexes...")
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_notif_user_read_created 
                ON notifications(user_id, is_read, created_at DESC)
            """))
            conn.commit()
            print("✅ Notification indexes added")
        except Exception as e:
            print(f"⚠️ Notification indexes error: {e}")
            conn.rollback()
        
        print("\n✅ All indexes migration complete!")

if __name__ == "__main__":
    add_indexes()

