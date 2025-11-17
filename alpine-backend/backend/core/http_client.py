"""
HTTP Client Factory
Centralized HTTP client creation with optimized settings for connection pooling
"""
from typing import Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    httpx = None
    HTTPX_AVAILABLE = False


class HTTPClientFactory:
    """Factory for creating optimized HTTP clients with connection pooling"""
    
    # Default timeout settings
    DEFAULT_CONNECT_TIMEOUT = 5.0
    DEFAULT_READ_TIMEOUT = 10.0
    DEFAULT_WRITE_TIMEOUT = 5.0
    DEFAULT_POOL_TIMEOUT = 5.0
    
    # Default connection pool settings
    DEFAULT_MAX_KEEPALIVE_CONNECTIONS = 50
    DEFAULT_MAX_CONNECTIONS = 200
    DEFAULT_KEEPALIVE_EXPIRY = 60.0
    
    @staticmethod
    def create_client(
        connect_timeout: float = None,
        read_timeout: float = None,
        write_timeout: float = None,
        pool_timeout: float = None,
        max_keepalive_connections: int = None,
        max_connections: int = None,
        keepalive_expiry: float = None,
        http2: bool = True,
        follow_redirects: bool = True
    ) -> Optional[httpx.AsyncClient]:
        """
        Create an optimized HTTP client with connection pooling
        
        Args:
            connect_timeout: Connection timeout in seconds
            read_timeout: Read timeout in seconds
            write_timeout: Write timeout in seconds
            pool_timeout: Pool timeout in seconds
            max_keepalive_connections: Maximum keepalive connections
            max_connections: Maximum total connections
            keepalive_expiry: Keepalive expiry in seconds
            http2: Enable HTTP/2
            follow_redirects: Follow redirects automatically
        
        Returns:
            Configured httpx.AsyncClient or None if httpx not available
        """
        if not HTTPX_AVAILABLE:
            logger.warning("httpx not available, cannot create HTTP client")
            return None
        
        return httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=connect_timeout or HTTPClientFactory.DEFAULT_CONNECT_TIMEOUT,
                read=read_timeout or HTTPClientFactory.DEFAULT_READ_TIMEOUT,
                write=write_timeout or HTTPClientFactory.DEFAULT_WRITE_TIMEOUT,
                pool=pool_timeout or HTTPClientFactory.DEFAULT_POOL_TIMEOUT
            ),
            limits=httpx.Limits(
                max_keepalive_connections=max_keepalive_connections or HTTPClientFactory.DEFAULT_MAX_KEEPALIVE_CONNECTIONS,
                max_connections=max_connections or HTTPClientFactory.DEFAULT_MAX_CONNECTIONS,
                keepalive_expiry=keepalive_expiry or HTTPClientFactory.DEFAULT_KEEPALIVE_EXPIRY
            ),
            http2=http2,
            follow_redirects=follow_redirects
        )
    
    @staticmethod
    def get_default_client() -> Optional[httpx.AsyncClient]:
        """Get a client with default optimized settings"""
        return HTTPClientFactory.create_client()


class SingletonHTTPClient:
    """Thread-safe singleton HTTP client with lazy initialization"""
    
    _client: Optional[httpx.AsyncClient] = None
    _lock: Optional[asyncio.Lock] = None
    
    @classmethod
    async def get_client(cls) -> Optional[httpx.AsyncClient]:
        """
        Get or create singleton HTTP client (thread-safe)
        
        Returns:
            Shared httpx.AsyncClient instance or None if httpx not available
        """
        if not HTTPX_AVAILABLE:
            return None
        
        # Initialize lock if needed
        if cls._lock is None:
            try:
                cls._lock = asyncio.Lock()
            except RuntimeError:
                # No event loop available - use simple check (safe due to GIL)
                pass
        
        # Use lock if available, otherwise rely on double-check pattern
        if cls._lock is not None:
            async with cls._lock:
                if cls._client is None:
                    cls._client = HTTPClientFactory.get_default_client()
        else:
            # Fallback: double-check without lock (safe due to GIL)
            if cls._client is None:
                cls._client = HTTPClientFactory.get_default_client()
        
        return cls._client
    
    @classmethod
    async def close_client(cls):
        """Close and cleanup the singleton HTTP client"""
        if cls._client:
            try:
                await cls._client.aclose()
            except Exception as e:
                logger.debug(f"Error closing HTTP client: {e}")
            finally:
                cls._client = None
    
    @classmethod
    def reset_client(cls):
        """Reset the client (useful for testing)"""
        cls._client = None
        cls._lock = None

