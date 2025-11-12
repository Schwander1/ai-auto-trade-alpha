"""Database migration to add 2FA fields to users table"""
from sqlalchemy import text
from backend.core.database import engine

def add_2fa_fields():
    """Add 2FA fields to users table"""
    with engine.connect() as conn:
        print("Adding 2FA fields to users table...")
        try:
            # Add totp_secret column
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS totp_secret VARCHAR(255)
            """))
            
            # Add totp_enabled column
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS totp_enabled BOOLEAN DEFAULT FALSE
            """))
            
            # Add backup_codes column
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS backup_codes TEXT
            """))
            
            # Add last_totp_used column
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS last_totp_used TIMESTAMP WITH TIME ZONE
            """))
            
            conn.commit()
            print("✅ 2FA fields added successfully")
        except Exception as e:
            print(f"⚠️ Error adding 2FA fields: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    add_2fa_fields()

