"""Configuration management for Argo"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
import sys
from pathlib import Path

# Add shared package to path
shared_path = Path(__file__).parent.parent.parent.parent / "packages" / "shared"
if shared_path.exists():
    sys.path.insert(0, str(shared_path))

try:
    from utils.secrets_manager import get_secret
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
                from utils.secrets_manager import get_secrets_manager
                self.secrets = get_secrets_manager(
                    fallback_to_env=True,
                    secret_prefix="argo-alpine"
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
        if self.secrets:
            return self.secrets.get_secret(
                "api-secret",
                service="argo",
                default="argo_secret_key_change_in_production"
            )
        return os.getenv("ARGO_API_SECRET", "argo_secret_key_change_in_production")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Allow properties to be accessed
        arbitrary_types_allowed = True


settings = Settings()

