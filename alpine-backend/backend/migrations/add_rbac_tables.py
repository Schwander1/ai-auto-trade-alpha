"""Database migration: Add RBAC tables (roles, permissions, user_roles, role_permissions)"""
from sqlalchemy import text, create_engine
from backend.core.database import get_engine
from backend.core.config import settings
import logging

logger = logging.getLogger(__name__)


def upgrade():
    """Add RBAC tables"""
    # Use get_engine if available, otherwise create from settings
    try:
        engine = get_engine()
    except (ImportError, AttributeError, Exception) as e:
        logger.warning(f"Could not get engine from get_engine(), creating new engine: {e}")
        engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Create permissions table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS permissions (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        
        # Create roles table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS roles (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                description TEXT,
                is_system BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE
            )
        """))
        
        # Create user_roles association table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_roles (
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
                PRIMARY KEY (user_id, role_id)
            )
        """))
        
        # Create role_permissions association table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS role_permissions (
                role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
                permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
                PRIMARY KEY (role_id, permission_id)
            )
        """))
        
        # Create indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_permissions_name ON permissions(name)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles(role_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_role_permissions_role_id ON role_permissions(role_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_role_permissions_permission_id ON role_permissions(permission_id)"))
        
        conn.commit()
        logger.info("✅ RBAC tables created successfully")


def downgrade():
    """Remove RBAC tables"""
    # Use get_engine if available, otherwise create from settings
    try:
        engine = get_engine()
    except (ImportError, AttributeError, Exception) as e:
        logger.warning(f"Could not get engine from get_engine(), creating new engine: {e}")
        engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS role_permissions CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS user_roles CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS roles CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS permissions CASCADE"))
        conn.commit()
        logger.info("✅ RBAC tables removed")


if __name__ == "__main__":
    upgrade()

