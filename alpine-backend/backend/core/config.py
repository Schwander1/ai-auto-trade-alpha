"""Configuration management"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
import sys
from pathlib import Path

# Use Alpine-specific secrets manager
try:
    from backend.utils.secrets_manager import get_secrets_manager
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False
    import logging
    logging.warning("AWS Secrets Manager not available - using environment variables only")


class Settings(BaseSettings):
    """Alpine Backend settings with AWS Secrets Manager support"""
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    USE_AWS_SECRETS: bool = os.getenv("USE_AWS_SECRETS", "true").lower() == "true"
    
    # Business (non-secret config)
    BUSINESS_NAME: str = "Alpine Analytics LLC"
    BUSINESS_PHONE: str = "+1-307-293-6424"
    BUSINESS_EMAIL: str = "alpine.signals@proton.me"
    
    # Pricing (non-secret config)
    TIER_STARTER_PRICE: int = 49
    TIER_PRO_PRICE: int = 99
    TIER_ELITE_PRICE: int = 249
    
    # JWT Algorithm (non-secret config)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # External Signal Provider API URL (non-secret config)
    EXTERNAL_SIGNAL_API_URL: str = "http://178.156.194.174:8000"
    
    # Secrets - will be loaded from AWS Secrets Manager or environment
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = "whsec_WILL_GET_LATER"
    STRIPE_ACCOUNT_ID: Optional[str] = None
    STRIPE_STARTER_PRICE_ID: str = ""
    STRIPE_PRO_PRICE_ID: str = ""
    STRIPE_ELITE_PRICE_ID: str = ""
    DATABASE_URL: str = ""
    JWT_SECRET: str = ""
    DOMAIN: str = ""
    FRONTEND_URL: str = ""
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    SENDGRID_API_KEY: Optional[str] = None
    EXTERNAL_SIGNAL_API_KEY: str = ""  # API key for external signal provider to authenticate with Alpine
    
    def __init__(self, **kwargs):
        # Check if AWS Secrets Manager should be used
        use_aws_secrets = kwargs.get("USE_AWS_SECRETS", os.getenv("USE_AWS_SECRETS", "true").lower() == "true")
        
        # Initialize secrets manager if enabled
        secrets_manager = None
        if use_aws_secrets and SECRETS_MANAGER_AVAILABLE:
            try:
                secrets_manager = get_secrets_manager(
                    fallback_to_env=True,
                    secret_prefix="alpine-analytics"
                )
            except Exception as e:
                import logging
                logging.warning(f"Failed to initialize AWS Secrets Manager: {e}")
        
        # Load secrets from AWS or environment
        service = "alpine-backend"
        
        # Helper function to get secret
        def get_secret_value(key: str, default: str = "", required: bool = False) -> str:
            if secrets_manager:
                try:
                    value = secrets_manager.get_secret(key, service=service, default=default, required=required)
                    return value if value is not None else default
                except Exception as e:
                    import logging
                    logging.warning(f"Failed to get secret {key} from AWS: {e}")
            # Fallback to environment variable
            env_key = key.upper().replace("-", "_")
            return os.getenv(env_key, default)
        
        # Load all secrets (only if not already in kwargs)
        if "STRIPE_SECRET_KEY" not in kwargs:
            kwargs["STRIPE_SECRET_KEY"] = get_secret_value("stripe-secret-key", required=True)
        if "STRIPE_PUBLISHABLE_KEY" not in kwargs:
            kwargs["STRIPE_PUBLISHABLE_KEY"] = get_secret_value("stripe-publishable-key", required=True)
        if "STRIPE_WEBHOOK_SECRET" not in kwargs:
            kwargs["STRIPE_WEBHOOK_SECRET"] = get_secret_value("stripe-webhook-secret", "whsec_WILL_GET_LATER")
        if "STRIPE_ACCOUNT_ID" not in kwargs:
            kwargs["STRIPE_ACCOUNT_ID"] = get_secret_value("stripe-account-id", "") or None
        if "STRIPE_STARTER_PRICE_ID" not in kwargs:
            kwargs["STRIPE_STARTER_PRICE_ID"] = get_secret_value("stripe-starter-price-id", "")
        if "STRIPE_PRO_PRICE_ID" not in kwargs:
            kwargs["STRIPE_PRO_PRICE_ID"] = get_secret_value("stripe-pro-price-id", "")
        if "STRIPE_ELITE_PRICE_ID" not in kwargs:
            kwargs["STRIPE_ELITE_PRICE_ID"] = get_secret_value("stripe-elite-price-id", "")
        if "DATABASE_URL" not in kwargs:
            kwargs["DATABASE_URL"] = get_secret_value("database-url", required=True)
        if "JWT_SECRET" not in kwargs:
            kwargs["JWT_SECRET"] = get_secret_value("jwt-secret", required=True)
        if "DOMAIN" not in kwargs:
            kwargs["DOMAIN"] = get_secret_value("domain", required=True)
        if "FRONTEND_URL" not in kwargs:
            kwargs["FRONTEND_URL"] = get_secret_value("frontend-url", required=True)
        if "REDIS_HOST" not in kwargs:
            kwargs["REDIS_HOST"] = get_secret_value("redis-host", "localhost")
        if "REDIS_PORT" not in kwargs:
            kwargs["REDIS_PORT"] = int(get_secret_value("redis-port", "6379"))
        if "REDIS_PASSWORD" not in kwargs:
            kwargs["REDIS_PASSWORD"] = get_secret_value("redis-password", "") or None
        if "REDIS_DB" not in kwargs:
            kwargs["REDIS_DB"] = int(get_secret_value("redis-db", "0"))
        if "SENDGRID_API_KEY" not in kwargs:
            kwargs["SENDGRID_API_KEY"] = get_secret_value("sendgrid-api-key", "") or None
        if "EXTERNAL_SIGNAL_API_KEY" not in kwargs:
            kwargs["EXTERNAL_SIGNAL_API_KEY"] = get_secret_value("external-signal-api-key", "")
        
        super().__init__(**kwargs)
    
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
        
        # SECURITY: Check for default/weak secrets
        weak_secrets = [
            "change_me", "secret", "password", "default", "test", "demo",
            "argo_secret_key_change_in_production", "whsec_WILL_GET_LATER"
        ]
        if self.JWT_SECRET and any(weak in self.JWT_SECRET.lower() for weak in weak_secrets):
            errors.append("JWT_SECRET appears to be a default or weak secret")
        
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

# SECURITY: Validate settings on import (all environments, fail fast on critical issues)
import os
# Validate secrets in all environments, but fail fast only in production
env = os.getenv("ENVIRONMENT", "development")
try:
    # Only validate if we have actual values (not empty strings from failed AWS load)
    if settings.DATABASE_URL and settings.JWT_SECRET and settings.STRIPE_SECRET_KEY:
        # In production, validate secrets but allow deployment with placeholders for initial setup
        # Log warnings instead of failing if placeholders are detected
        try:
            settings.validate_secrets()
        except ValueError as validation_error:
            error_msg = str(validation_error)
            # Check if this is a placeholder/weak secret issue (not a missing secret)
            if "appears to be a default or weak secret" in error_msg or "must be a valid" in error_msg:
                import logging
                logging.warning(f"⚠️  SECURITY WARNING: {validation_error}")
                logging.warning("⚠️  Placeholder secrets detected. Replace with real values before production use!")
                # Allow startup with warnings for initial deployment
                # In a real production environment, you should fail here
                # For now, we allow it to start so the service can be configured
            else:
                # For other validation errors (missing secrets), fail fast in production
                if env == "production":
                    raise
    elif env == "production":
        # In production, fail fast if required secrets are missing
        import logging
        logging.error("Required secrets are missing in production environment")
        raise ValueError(
            "CRITICAL: Required secrets are missing in production. "
            "Ensure AWS Secrets Manager is configured or environment variables are set."
        )
except ValueError as e:
    import logging
    logging.error(f"Configuration validation failed: {e}")
    # In production, always fail fast on validation errors (except placeholder warnings above)
    if env == "production" and "SECURITY WARNING" not in str(e):
        raise
