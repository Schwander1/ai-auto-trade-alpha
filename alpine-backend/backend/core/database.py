"""Database connection with connection pooling"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings

# Lazy initialization - create engine on first access
_engine = None
_SessionLocal = None

def get_engine():
    """Get or create database engine (lazy initialization)"""
    global _engine
    if _engine is None:
        # Validate DATABASE_URL before creating engine
        if not settings.DATABASE_URL or not settings.DATABASE_URL.strip():
            raise ValueError(
                "DATABASE_URL is not set. Please ensure it's configured in AWS Secrets Manager "
                "or environment variables."
            )
        
        # Use DATABASE_URL as-is (Docker networking handles hostname resolution)
        # Inside Docker containers, 'postgres' hostname resolves to the postgres service
        # For local development, use localhost:5433 in DATABASE_URL
        db_url = settings.DATABASE_URL
        
        # Optimized connection pooling
        _engine = create_engine(
            db_url,
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
    return _engine

def get_session_local():
    """Get or create session maker (lazy initialization)"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

# For backward compatibility, create engine and SessionLocal on import
# But only if DATABASE_URL is available
try:
    if settings.DATABASE_URL and settings.DATABASE_URL.strip():
        engine = get_engine()
        SessionLocal = get_session_local()
    else:
        # Create placeholder that will be initialized on first use
        engine = None
        SessionLocal = None
except Exception:
    # If settings aren't loaded yet, create placeholders
    engine = None
    SessionLocal = None

Base = declarative_base()

def get_db():
    """Database session dependency with proper cleanup"""
    global engine, SessionLocal
    # Ensure engine and SessionLocal are initialized
    if engine is None or SessionLocal is None:
        # Lazy initialization
        engine = get_engine()
        SessionLocal = get_session_local()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
