#!/usr/bin/env python3
"""
Database Index Creation Script
Creates optimized indexes for common query patterns to improve performance.

Run this script after database migrations to ensure all indexes are created.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, Index
from backend.core.database import get_engine, Base
from backend.models.signal import Signal
from backend.models.user import User
from backend.models.notification import Notification
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_indexes():
    """Create all database indexes for optimal query performance"""
    engine = get_engine()

    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()

        try:
            logger.info("Creating database indexes...")

            # Signal table indexes
            logger.info("Creating Signal table indexes...")

            # Composite index for active signals by confidence and date (already in model)
            # idx_signal_active_confidence_created - already defined in model

            # Composite index for symbol-based queries (already in model)
            # idx_signal_symbol_created - already defined in model

            # Additional index for confidence filtering
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_signal_confidence
                    ON signals(confidence DESC)
                """))
                logger.info("✅ Created idx_signal_confidence")
            except Exception as e:
                logger.warning(f"Index idx_signal_confidence may already exist: {e}")

            # Index for is_active filtering
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_signal_is_active
                    ON signals(is_active) WHERE is_active = true
                """))
                logger.info("✅ Created idx_signal_is_active (partial index)")
            except Exception as e:
                logger.warning(f"Index idx_signal_is_active may already exist: {e}")

            # User table indexes
            logger.info("Creating User table indexes...")

            # Composite index for tier and active status (already in model)
            # idx_user_tier_active - already defined in model

            # Index for created_at (already in model)
            # idx_user_created_at - already defined in model

            # Additional index for email lookups (already has unique index)
            # email column already has unique index

            # Notification table indexes
            logger.info("Creating Notification table indexes...")

            # Composite index for user notifications by read status and date
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_notif_user_read_created
                    ON notifications(user_id, is_read, created_at DESC)
                """))
                logger.info("✅ Created idx_notif_user_read_created")
            except Exception as e:
                logger.warning(f"Index idx_notif_user_read_created may already exist: {e}")

            # Index for unread notifications
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_notif_unread
                    ON notifications(user_id, created_at DESC)
                    WHERE is_read = false
                """))
                logger.info("✅ Created idx_notif_unread (partial index)")
            except Exception as e:
                logger.warning(f"Index idx_notif_unread may already exist: {e}")

            # Commit transaction
            trans.commit()
            logger.info("✅ All indexes created successfully!")

        except Exception as e:
            trans.rollback()
            logger.error(f"❌ Error creating indexes: {e}")
            raise


def verify_indexes():
    """Verify that indexes were created successfully"""
    engine = get_engine()

    with engine.connect() as conn:
        # Get all indexes for signals table
        result = conn.execute(text("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'signals'
            ORDER BY indexname
        """))

        logger.info("\n📊 Signal table indexes:")
        for row in result:
            logger.info(f"  - {row[0]}")

        # Get all indexes for users table
        result = conn.execute(text("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'users'
            ORDER BY indexname
        """))

        logger.info("\n📊 User table indexes:")
        for row in result:
            logger.info(f"  - {row[0]}")

        # Get all indexes for notifications table
        result = conn.execute(text("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'notifications'
            ORDER BY indexname
        """))

        logger.info("\n📊 Notification table indexes:")
        for row in result:
            logger.info(f"  - {row[0]}")


if __name__ == "__main__":
    try:
        create_indexes()
        verify_indexes()
        logger.info("\n✅ Database index creation complete!")
    except Exception as e:
        logger.error(f"\n❌ Failed to create indexes: {e}")
        sys.exit(1)
