"""Configuration management for Argo"""
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions or missing dependency
    try:
        from pydantic import BaseSettings
    except ImportError:
        # Ultimate fallback - use a simple class
        class BaseSettings:
            pass

from typing import Optional
import os
import sys
from pathlib import Path

# Use Argo-specific secrets manager
try:
    from argo.utils.secrets_manager import get_secret
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False
    import logging
    logging.warning("AWS Secrets Manager not available - using environment variables only")


class Settings(BaseSettings):
    """Argo API settings with AWS Secrets Manager support"""
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    USE_AWS_SECRETS: bool = os.getenv("USE_AWS_SECRETS", "true").lower() == "true"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize secrets manager if enabled
        if self.USE_AWS_SECRETS and SECRETS_MANAGER_AVAILABLE:
            try:
                from argo.utils.secrets_manager import get_secrets_manager
                self.secrets = get_secrets_manager(
                    fallback_to_env=True,
                    secret_prefix="argo-capital"
                )
            except Exception as e:
                import logging
                logging.warning(f"Failed to initialize AWS Secrets Manager: {e}")
                self.secrets = None
        else:
            self.secrets = None
    
    @property
    def REDIS_HOST(self) -> str:
        """Redis host from AWS Secrets Manager or environment"""
        if self.secrets:
            return self.secrets.get_secret("redis-host", service="argo", default="localhost")
        return os.getenv("REDIS_HOST", "localhost")
    
    @property
    def REDIS_PORT(self) -> int:
        """Redis port from AWS Secrets Manager or environment"""
        if self.secrets:
            port = self.secrets.get_secret("redis-port", service="argo", default="6379")
            return int(port)
        return int(os.getenv("REDIS_PORT", "6379"))
    
    @property
    def REDIS_PASSWORD(self) -> Optional[str]:
        """Redis password from AWS Secrets Manager or environment"""
        if self.secrets:
            return self.secrets.get_secret("redis-password", service="argo", default=None)
        return os.getenv("REDIS_PASSWORD", None)
    
    @property
    def REDIS_DB(self) -> int:
        """Redis database number from AWS Secrets Manager or environment"""
        if self.secrets:
            db = self.secrets.get_secret("redis-db", service="argo", default="0")
            return int(db)
        return int(os.getenv("REDIS_DB", "0"))
    
    @property
    def ARGO_API_SECRET(self) -> str:
        """Argo API secret from AWS Secrets Manager or environment"""
        default_secret = "argo_secret_key_change_in_production"
        
        if self.secrets:
            secret = self.secrets.get_secret(
                "api-secret",
                service="argo",
                default=default_secret
            )
        else:
            secret = os.getenv("ARGO_API_SECRET", default_secret)
        
        # SECURITY: Fail fast in production if using default secret
        if self.ENVIRONMENT == "production" and secret == default_secret:
            import logging
            logger = logging.getLogger(__name__)
            logger.critical("CRITICAL: Using default API secret in production! This is a security risk.")
            raise ValueError(
                "ARGO_API_SECRET must be set to a non-default value in production. "
                "Set it in AWS Secrets Manager or environment variables."
            )
        
        return secret
    
    @property
    def SIGNAL_GENERATION_INTERVAL(self) -> int:
        """Signal generation interval in seconds"""
        if self.secrets:
            interval = self.secrets.get_secret("signal-generation-interval", service="argo", default="5")
            return int(interval)
        return int(os.getenv("SIGNAL_GENERATION_INTERVAL", "5"))
    
    @property
    def RATE_LIMIT_MAX_REQUESTS(self) -> int:
        """Maximum requests per rate limit window"""
        if self.secrets:
            max_req = self.secrets.get_secret("rate-limit-max-requests", service="argo", default="100")
            return int(max_req)
        return int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100"))
    
    @property
    def RATE_LIMIT_WINDOW(self) -> int:
        """Rate limit window in seconds"""
        if self.secrets:
            window = self.secrets.get_secret("rate-limit-window", service="argo", default="60")
            return int(window)
        return int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    @property
    def CACHE_TTL_SIGNALS(self) -> int:
        """Cache TTL for signals in seconds"""
        if self.secrets:
            ttl = self.secrets.get_secret("cache-ttl-signals", service="argo", default="10")
            return int(ttl)
        return int(os.getenv("CACHE_TTL_SIGNALS", "10"))
    
    @property
    def CACHE_TTL_STATS(self) -> int:
        """Cache TTL for stats in seconds"""
        if self.secrets:
            ttl = self.secrets.get_secret("cache-ttl-stats", service="argo", default="30")
            return int(ttl)
        return int(os.getenv("CACHE_TTL_STATS", "30"))
    
    @property
    def ALLOWED_ORIGINS(self) -> list:
        """CORS allowed origins"""
        if self.secrets:
            origins_str = self.secrets.get_secret("cors-allowed-origins", service="argo", default="")
            if origins_str:
                return [origin.strip() for origin in origins_str.split(",") if origin.strip()]
        
        env_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
        if env_origins:
            return [origin.strip() for origin in env_origins.split(",") if origin.strip()]
        
        # Default origins
        return [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://91.98.153.49:3000",
            "http://91.98.153.49:8001",
            "https://91.98.153.49:3000",
        ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Allow properties to be accessed
        arbitrary_types_allowed = True
        extra = "allow"  # Allow extra fields from .env


settings = Settings()

