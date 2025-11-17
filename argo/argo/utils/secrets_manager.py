"""
Argo Capital - AWS Secrets Manager utility
Provides caching, fallback to environment variables, and error handling
"""

import json
import os
import time
from typing import Any, Dict, Optional
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# Try to import boto3, but don't fail if not available
try:
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    logger.warning("boto3 not available - using environment variable fallback only")


class SecretsManager:
    """
    AWS Secrets Manager client with caching and fallback support
    
    Features:
    - Automatic caching (5 minute TTL by default)
    - Fallback to environment variables for local development
    - Error handling and retry logic
    - Support for JSON secrets and plain text secrets
    """
    
    def __init__(
        self,
        region_name: Optional[str] = None,
        cache_ttl: int = 300,  # 5 minutes
        fallback_to_env: bool = True,
        secret_prefix: str = "argo-capital"  # Argo-specific prefix
    ):
        """
        Initialize Secrets Manager client
        
        Args:
            region_name: AWS region (defaults to AWS_DEFAULT_REGION env var)
            cache_ttl: Cache TTL in seconds (default: 300)
            fallback_to_env: Fallback to environment variables if AWS unavailable
            secret_prefix: Prefix for secret names (default: "argo-capital")
        """
        self.region_name = region_name or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.cache_ttl = cache_ttl
        self.fallback_to_env = fallback_to_env
        self.secret_prefix = secret_prefix
        
        # In-memory cache: {secret_name: (value, timestamp)}
        self._cache: Dict[str, tuple[Any, float]] = {}
        
        # Initialize AWS client if available
        self.client = None
        if AWS_AVAILABLE:
            try:
                self.client = boto3.client(
                    'secretsmanager',
                    region_name=self.region_name
                )
                logger.info(f"AWS Secrets Manager initialized (region: {self.region_name})")
            except Exception as e:
                logger.warning(f"Failed to initialize AWS Secrets Manager: {e}")
                if not fallback_to_env:
                    raise
    
    def _get_secret_name(self, key: str, service: Optional[str] = None) -> str:
        """
        Generate full secret name from key and optional service
        
        Args:
            key: Secret key name
            service: Optional service name (e.g., "argo")
        
        Returns:
            Full secret name (e.g., "argo-capital/alpaca/api_key")
        """
        if service:
            return f"{self.secret_prefix}/{service}/{key}"
        return f"{self.secret_prefix}/{key}"
    
    def _is_cache_valid(self, secret_name: str) -> bool:
        """Check if cached secret is still valid"""
        if secret_name not in self._cache:
            return False
        
        _, timestamp = self._cache[secret_name]
        return (time.time() - timestamp) < self.cache_ttl
    
    def _get_from_cache(self, secret_name: str) -> Optional[Any]:
        """Get secret from cache if valid"""
        if self._is_cache_valid(secret_name):
            value, _ = self._cache[secret_name]
            logger.debug(f"Cache hit for secret: {secret_name}")
            return value
        return None
    
    def _set_cache(self, secret_name: str, value: Any):
        """Store secret in cache"""
        self._cache[secret_name] = (value, time.time())
    
    def _get_from_aws(self, secret_name: str) -> Optional[str]:
        """
        Retrieve secret from AWS Secrets Manager
        
        Args:
            secret_name: Full secret name
        
        Returns:
            Secret value as string, or None if not found
        """
        if not self.client:
            return None
        
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            
            # Handle both JSON and plain text secrets
            if 'SecretString' in response:
                return response['SecretString']
            elif 'SecretBinary' in response:
                import base64
                return base64.b64decode(response['SecretBinary']).decode('utf-8')
            
            return None
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                logger.debug(f"Secret not found: {secret_name}")
            elif error_code == 'InvalidRequestException':
                logger.error(f"Invalid request for secret {secret_name}: {e}")
            elif error_code == 'InvalidParameterException':
                logger.error(f"Invalid parameter for secret {secret_name}: {e}")
            elif error_code == 'DecryptionFailureException':
                logger.error(f"Failed to decrypt secret {secret_name}: {e}")
            elif error_code == 'InternalServiceErrorException':
                logger.error(f"AWS internal error for secret {secret_name}: {e}")
            else:
                logger.error(f"Error retrieving secret {secret_name}: {e}")
            return None
            
        except BotoCoreError as e:
            logger.error(f"AWS client error retrieving secret {secret_name}: {e}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error retrieving secret {secret_name}: {e}")
            return None
    
    def _get_from_env(self, key: str) -> Optional[str]:
        """Get secret from environment variable"""
        value = os.getenv(key)
        if value:
            logger.debug(f"Retrieved {key} from environment variable")
        return value
    
    def get_secret(
        self,
        key: str,
        service: Optional[str] = None,
        default: Optional[str] = None,
        required: bool = False,
        parse_json: bool = False
    ) -> Optional[Any]:
        """
        Get secret value with caching and fallback
        
        Args:
            key: Secret key name
            service: Optional service name for namespacing
            default: Default value if secret not found
            required: If True, raise error if secret not found
            parse_json: If True, parse secret as JSON
        
        Returns:
            Secret value (string or dict if parse_json=True)
        
        Raises:
            ValueError: If required=True and secret not found
        """
        secret_name = self._get_secret_name(key, service)
        
        # Try cache first
        cached_value = self._get_from_cache(secret_name)
        if cached_value is not None:
            return cached_value
        
        # Try AWS Secrets Manager with new prefix first
        aws_value = self._get_from_aws(secret_name)
        
        # Backward compatibility: Try old "argo-alpine" prefix if new prefix fails
        if not aws_value and self.secret_prefix == "argo-capital" and service:
            old_secret_name = f"argo-alpine/{service}/{key}"
            logger.debug(f"Trying backward-compatible secret name: {old_secret_name}")
            aws_value = self._get_from_aws(old_secret_name)
            if aws_value:
                logger.info(f"Found secret with old prefix (argo-alpine), consider migrating to new prefix (argo-capital)")
        
        if aws_value:
            try:
                if parse_json:
                    value = json.loads(aws_value)
                else:
                    value = aws_value
                self._set_cache(secret_name, value)
                logger.debug(f"Retrieved {secret_name} from AWS Secrets Manager")
                return value
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON secret: {secret_name}")
                if required:
                    raise ValueError(f"Invalid JSON in secret: {secret_name}")
        
        # Fallback to environment variable
        if self.fallback_to_env:
            env_value = self._get_from_env(key.upper().replace('-', '_'))
            if env_value:
                try:
                    if parse_json:
                        value = json.loads(env_value)
                    else:
                        value = env_value
                    self._set_cache(secret_name, value)
                    return value
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON from env var {key}")
        
        # Use default or raise error
        if default is not None:
            logger.debug(f"Using default value for {secret_name}")
            return default
        
        if required:
            raise ValueError(
                f"Required secret not found: {secret_name} "
                f"(checked AWS Secrets Manager and environment variables)"
            )
        
        return None
    
    def get_secrets_dict(
        self,
        keys: list[str],
        service: Optional[str] = None,
        parse_json: bool = False
    ) -> Dict[str, Any]:
        """
        Get multiple secrets as a dictionary
        
        Args:
            keys: List of secret keys
            service: Optional service name
            parse_json: Parse each secret as JSON
        
        Returns:
            Dictionary of {key: value}
        """
        return {
            key: self.get_secret(key, service=service, parse_json=parse_json)
            for key in keys
        }
    
    def set_secret(
        self,
        key: str,
        value: Any,
        service: Optional[str] = None,
        description: Optional[str] = None,
        force_create: bool = False
    ) -> bool:
        """
        Create or update secret in AWS Secrets Manager
        
        Args:
            key: Secret key name
            value: Secret value (will be JSON-encoded if dict/list)
            service: Optional service name
            description: Optional description for the secret
            force_create: If True, skip existence check and try to create directly
        
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("AWS client not available - cannot set secret")
            return False
        
        secret_name = self._get_secret_name(key, service)
        
        # Convert value to string
        if isinstance(value, (dict, list)):
            secret_string = json.dumps(value)
        else:
            secret_string = str(value)
        
        try:
            if force_create:
                # Try to create directly (will fail if exists, but that's OK)
                try:
                    kwargs = {
                        'Name': secret_name,
                        'SecretString': secret_string
                    }
                    if description:
                        kwargs['Description'] = description
                    
                    self.client.create_secret(**kwargs)
                    logger.info(f"Created secret: {secret_name}")
                except ClientError as e:
                    if e.response['Error']['Code'] == 'ResourceExistsException':
                        # Secret exists - update it
                        self.client.put_secret_value(
                            SecretId=secret_name,
                            SecretString=secret_string
                        )
                        logger.info(f"Updated secret: {secret_name}")
                    else:
                        raise
            else:
                # Try to get existing secret first
                try:
                    self.client.get_secret_value(SecretId=secret_name)
                    # Secret exists - update it
                    self.client.put_secret_value(
                        SecretId=secret_name,
                        SecretString=secret_string
                    )
                    logger.info(f"Updated secret: {secret_name}")
                except ClientError as e:
                    if e.response['Error']['Code'] == 'ResourceNotFoundException':
                        # Secret doesn't exist - create it
                        kwargs = {
                            'Name': secret_name,
                            'SecretString': secret_string
                        }
                        if description:
                            kwargs['Description'] = description
                        
                        self.client.create_secret(**kwargs)
                        logger.info(f"Created secret: {secret_name}")
                    elif e.response['Error']['Code'] == 'AccessDeniedException':
                        # Don't have permission to check - try to create directly
                        try:
                            kwargs = {
                                'Name': secret_name,
                                'SecretString': secret_string
                            }
                            if description:
                                kwargs['Description'] = description
                            
                            self.client.create_secret(**kwargs)
                            logger.info(f"Created secret: {secret_name}")
                        except ClientError as create_error:
                            if create_error.response['Error']['Code'] == 'ResourceExistsException':
                                # Secret exists - update it
                                self.client.put_secret_value(
                                    SecretId=secret_name,
                                    SecretString=secret_string
                                )
                                logger.info(f"Updated secret: {secret_name}")
                            else:
                                raise
                    else:
                        raise
            
            # Invalidate cache
            if secret_name in self._cache:
                del self._cache[secret_name]
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set secret {secret_name}: {e}")
            return False
    
    def clear_cache(self):
        """Clear the in-memory cache"""
        self._cache.clear()
        logger.debug("Secrets cache cleared")


# Global instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager(**kwargs) -> SecretsManager:
    """
    Get or create global SecretsManager instance
    
    Args:
        **kwargs: Arguments to pass to SecretsManager constructor
    
    Returns:
        SecretsManager instance
    """
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager(**kwargs)
    return _secrets_manager


def get_secret(
    key: str,
    service: Optional[str] = None,
    default: Optional[str] = None,
    required: bool = False,
    parse_json: bool = False
) -> Optional[Any]:
    """
    Convenience function to get a secret using global instance
    
    Args:
        key: Secret key name
        service: Optional service name
        default: Default value if not found
        required: If True, raise error if not found
        parse_json: Parse as JSON
    
    Returns:
        Secret value
    """
    return get_secrets_manager().get_secret(
        key=key,
        service=service,
        default=default,
        required=required,
        parse_json=parse_json
    )

