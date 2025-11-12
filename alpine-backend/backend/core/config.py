"""Configuration management"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_WEBHOOK_SECRET: str = "whsec_WILL_GET_LATER"
    
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
    
    # Optional
    SENDGRID_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
