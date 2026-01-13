"""
Caching Middleware
Implements response caching for expensive operations
"""
from typing import Callable, Optional
import hashlib
import json
import logging
from datetime import datetime, timedelta

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from redis import Redis

logger = logging.getLogger(__name__)


class CacheMiddleware(BaseHTTPMiddleware):
    """
    Response caching middleware using Redis
    
    Caches GET requests to reduce load on expensive operations
    """
    
    def __init__(self,
                 app: ASGIApp,
                 redis_client: Optional[Redis] = None,
                 default_ttl: int = 300,
                 cache_enabled: bool = True):
        """
        Initialize cache middleware
        
        Args:
            app: ASGI application
            redis_client: Redis client instance
            default_ttl: Default cache TTL in seconds
            cache_enabled: Whether caching is enabled
        """
        super().__init__(app)
        self.redis_client = redis_client
        self.default_ttl = default_ttl
        self.cache_enabled = cache_enabled and redis_client is not None
        
        if self.cache_enabled:
            logger.info(f"Cache middleware initialized with {default_ttl}s TTL")
        else:
            logger.info("Cache middleware disabled (no Redis client)")
    
    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process request with caching
        
        Args:
            request: HTTP request
            call_next: Next middleware/handler
        
        Returns:
            HTTP response (cached or fresh)
        """
        # Only cache GET requests
        if request.method != "GET" or not self.cache_enabled:
            return await call_next(request)
        
        # Skip caching for certain paths
        if self._should_skip_cache(request.url.path):
            return await call_next(request)
        
        # Generate cache key
        cache_key = self._generate_cache_key(request)
        
        # Try to get from cache
        cached_response = self._get_from_cache(cache_key)
        if cached_response:
            logger.debug(f"Cache HIT: {cache_key}")
            return Response(
                content=cached_response["content"],
                status_code=cached_response["status_code"],
                headers={
                    **cached_response["headers"],
                    "X-Cache": "HIT",
                    "X-Cache-Key": cache_key
                },
                media_type=cached_response.get("media_type", "application/json")
            )
        
        # Cache miss - process request
        logger.debug(f"Cache MISS: {cache_key}")
        response = await call_next(request)
        
        # Cache successful responses
        if 200 <= response.status_code < 300:
            await self._store_in_cache(cache_key, response)
        
        # Add cache headers
        response.headers["X-Cache"] = "MISS"
        response.headers["X-Cache-Key"] = cache_key
        
        return response
    
    def _should_skip_cache(self, path: str) -> bool:
        """
        Determine if path should skip caching
        
        Args:
            path: Request path
        
        Returns:
            True if should skip cache
        """
        skip_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/admin"
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    def _generate_cache_key(self, request: Request) -> str:
        """
        Generate cache key from request
        
        Args:
            request: HTTP request
        
        Returns:
            Cache key
        """
        # Include path and query parameters
        key_parts = [
            request.url.path,
            str(sorted(request.query_params.items()))
        ]
        
        # Include API key if present (for user-specific caching)
        api_key = request.headers.get("X-API-Key")
        if api_key:
            key_parts.append(api_key)
        
        # Generate hash
        key_string = "|".join(key_parts)
        cache_key = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"cache:{cache_key}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[dict]:
        """
        Get response from cache
        
        Args:
            cache_key: Cache key
        
        Returns:
            Cached response or None
        """
        if not self.redis_client:
            return None
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None
    
    async def _store_in_cache(self, cache_key: str, response: Response):
        """
        Store response in cache
        
        Args:
            cache_key: Cache key
            response: Response to cache
        """
        if not self.redis_client:
            return
        
        try:
            # Read response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Prepare cache data
            cache_data = {
                "content": body.decode("utf-8"),
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "media_type": response.media_type,
                "cached_at": datetime.utcnow().isoformat()
            }
            
            # Store in Redis with TTL
            self.redis_client.setex(
                cache_key,
                self.default_ttl,
                json.dumps(cache_data)
            )
            
            logger.debug(f"Cached response: {cache_key} (TTL: {self.default_ttl}s)")
            
        except Exception as e:
            logger.error(f"Cache write error: {e}")


def cache_response(ttl: int = 300):
    """
    Decorator for caching specific endpoint responses
    
    Args:
        ttl: Cache TTL in seconds
    
    Returns:
        Decorator function
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This is a simplified version
            # In production, integrate with Redis properly
            return await func(*args, **kwargs)
        
        wrapper._cache_ttl = ttl
        return wrapper
    
    return decorator
