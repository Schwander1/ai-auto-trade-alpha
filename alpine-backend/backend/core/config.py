"""Configuration management"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_WEBHOOK_SECRET: str = "whsec_WILL_GET_LATER"
    STRIPE_ACCOUNT_ID: Optional[str] = None
    
    # Stripe Price IDs
    STRIPE_STARTER_PRICE_ID: str = ""  # Founder tier
    STRIPE_PRO_PRICE_ID: str = ""  # Professional tier
    STRIPE_ELITE_PRICE_ID: str = ""  # Institutional tier
    
    # Database
    DATABASE_URL: str
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Business
    BUSINESS_NAME: str = "Alpine Analytics LLC"
    BUSINESS_PHONE: str = "+1-307-293-6424"
    BUSINESS_EMAIL: str = "alpine.signals@proton.me"
    
    # Pricing
    TIER_STARTER_PRICE: int = 49
    TIER_PRO_PRICE: int = 99
    TIER_ELITE_PRICE: int = 249
    
    # Domain
    DOMAIN: str
    FRONTEND_URL: str
    
    # Argo API
    ARGO_API_URL: str = "http://178.156.194.174:8000"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # Optional
    SENDGRID_API_KEY: Optional[str] = None
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env
    
    def validate_secrets(self):
        """Validate that required secrets are set and meet security requirements"""
        errors = []
        
        # JWT Secret validation
        if not self.JWT_SECRET or len(self.JWT_SECRET) < 32:
            errors.append("JWT_SECRET must be at least 32 characters long")
        
        # Stripe keys validation
        if not self.STRIPE_SECRET_KEY or not self.STRIPE_SECRET_KEY.startswith(("sk_test_", "sk_live_")):
            errors.append("STRIPE_SECRET_KEY must be a valid Stripe secret key")
        
        if not self.STRIPE_WEBHOOK_SECRET or self.STRIPE_WEBHOOK_SECRET == "whsec_WILL_GET_LATER":
            errors.append("STRIPE_WEBHOOK_SECRET must be set to a valid webhook secret")
        
        # Database URL validation
        if not self.DATABASE_URL or "postgresql://" not in self.DATABASE_URL:
            errors.append("DATABASE_URL must be a valid PostgreSQL connection string")
        
        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

settings = Settings()

# Validate settings on import (only in production)
import os
if os.getenv("ENVIRONMENT") == "production" or not settings.DEBUG:
    try:
        settings.validate_secrets()
    except ValueError as e:
        import logging
        logging.error(f"Configuration validation failed: {e}")
        # In production, fail fast
        if os.getenv("ENVIRONMENT") == "production":
            raise
