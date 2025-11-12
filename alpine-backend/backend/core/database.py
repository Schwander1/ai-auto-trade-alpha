"""Database connection with connection pooling"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings

# Optimized connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,              # Increased pool size for better concurrency
    max_overflow=10,           # Allow overflow connections under load
    pool_pre_ping=True,        # Verify connections before use (handles stale connections)
    pool_recycle=3600,         # Recycle connections after 1 hour
    echo=False,                # Disable SQL logging in production
    connect_args={
        "connect_timeout": 10,  # 10 second connection timeout
        "application_name": "alpine_backend"
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Database session dependency with proper cleanup"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
