"""
Rate Limiting Middleware
Implements API rate limiting to prevent abuse
"""
from typing import Callable
import time
from collections import defaultdict
from datetime import datetime, timedelta
import logging

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using token bucket algorithm
    
    Limits requests per IP address and per API key
    """
    
    def __init__(self, 
                 app: ASGIApp,
                 requests_per_minute: int = 60,
                 requests_per_hour: int = 1000,
                 burst_size: int = 10):
        """
        Initialize rate limiter
        
        Args:
            app: ASGI application
            requests_per_minute: Maximum requests per minute
            requests_per_hour: Maximum requests per hour
            burst_size: Maximum burst requests
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size
        
        # Storage for rate limit tracking
        self.minute_buckets = defaultdict(lambda: {'count': 0, 'reset_time': None})
        self.hour_buckets = defaultdict(lambda: {'count': 0, 'reset_time': None})
        
        logger.info(f"Rate limiter initialized: {requests_per_minute}/min, {requests_per_hour}/hour")
    
    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process request with rate limiting
        
        Args:
            request: HTTP request
            call_next: Next middleware/handler
        
        Returns:
            HTTP response
        """
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/health", "/"]:
            return await call_next(request)
        
        # Get client identifier (IP address or API key)
        client_id = self._get_client_identifier(request)
        
        # Check rate limits
        is_allowed, retry_after = self._check_rate_limit(client_id)
        
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please try again in {retry_after} seconds.",
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0"
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self._get_remaining_requests(client_id)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    def _get_client_identifier(self, request: Request) -> str:
        """
        Get unique client identifier
        
        Args:
            request: HTTP request
        
        Returns:
            Client identifier
        """
        # Try to get API key from header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        
        # Check for forwarded IP (behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    def _check_rate_limit(self, client_id: str) -> tuple[bool, int]:
        """
        Check if client has exceeded rate limit
        
        Args:
            client_id: Client identifier
        
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        current_time = datetime.utcnow()
        
        # Check minute bucket
        minute_bucket = self.minute_buckets[client_id]
        if minute_bucket['reset_time'] is None or current_time > minute_bucket['reset_time']:
            # Reset bucket
            minute_bucket['count'] = 0
            minute_bucket['reset_time'] = current_time + timedelta(minutes=1)
        
        # Check hour bucket
        hour_bucket = self.hour_buckets[client_id]
        if hour_bucket['reset_time'] is None or current_time > hour_bucket['reset_time']:
            # Reset bucket
            hour_bucket['count'] = 0
            hour_bucket['reset_time'] = current_time + timedelta(hours=1)
        
        # Check limits
        if minute_bucket['count'] >= self.requests_per_minute:
            retry_after = int((minute_bucket['reset_time'] - current_time).total_seconds())
            return False, max(retry_after, 1)
        
        if hour_bucket['count'] >= self.requests_per_hour:
            retry_after = int((hour_bucket['reset_time'] - current_time).total_seconds())
            return False, max(retry_after, 1)
        
        # Increment counters
        minute_bucket['count'] += 1
        hour_bucket['count'] += 1
        
        return True, 0
    
    def _get_remaining_requests(self, client_id: str) -> int:
        """
        Get remaining requests for client
        
        Args:
            client_id: Client identifier
        
        Returns:
            Remaining requests in current minute
        """
        minute_bucket = self.minute_buckets.get(client_id)
        if not minute_bucket:
            return self.requests_per_minute
        
        return max(0, self.requests_per_minute - minute_bucket['count'])
    
    def cleanup_old_buckets(self):
        """Clean up expired buckets to prevent memory leaks"""
        current_time = datetime.utcnow()
        
        # Clean minute buckets
        expired_minute = [
            client_id for client_id, bucket in self.minute_buckets.items()
            if bucket['reset_time'] and current_time > bucket['reset_time'] + timedelta(minutes=5)
        ]
        for client_id in expired_minute:
            del self.minute_buckets[client_id]
        
        # Clean hour buckets
        expired_hour = [
            client_id for client_id, bucket in self.hour_buckets.items()
            if bucket['reset_time'] and current_time > bucket['reset_time'] + timedelta(hours=2)
        ]
        for client_id in expired_hour:
            del self.hour_buckets[client_id]
        
        if expired_minute or expired_hour:
            logger.debug(f"Cleaned up {len(expired_minute)} minute buckets and {len(expired_hour)} hour buckets")


class EndpointRateLimiter:
    """
    Decorator-based rate limiter for specific endpoints
    
    Usage:
        @app.get("/expensive-operation")
        @rate_limit(requests=10, window=60)
        async def expensive_operation():
            ...
    """
    
    def __init__(self, requests: int = 10, window: int = 60):
        """
        Initialize endpoint rate limiter
        
        Args:
            requests: Maximum requests
            window: Time window in seconds
        """
        self.requests = requests
        self.window = window
        self.buckets = defaultdict(lambda: {'count': 0, 'reset_time': None})
    
    def __call__(self, func):
        """Decorator wrapper"""
        async def wrapper(*args, **kwargs):
            # Get request from kwargs
            request = kwargs.get('request')
            if not request:
                # Try to find request in args
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if request:
                client_id = self._get_client_id(request)
                
                if not self._check_limit(client_id):
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Maximum {self.requests} requests per {self.window} seconds."
                    )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        return request.client.host if request.client else "unknown"
    
    def _check_limit(self, client_id: str) -> bool:
        """Check if request is within rate limit"""
        current_time = time.time()
        bucket = self.buckets[client_id]
        
        if bucket['reset_time'] is None or current_time > bucket['reset_time']:
            bucket['count'] = 0
            bucket['reset_time'] = current_time + self.window
        
        if bucket['count'] >= self.requests:
            return False
        
        bucket['count'] += 1
        return True


# Convenience decorator
def rate_limit(requests: int = 10, window: int = 60):
    """
    Rate limit decorator for endpoints
    
    Args:
        requests: Maximum requests
        window: Time window in seconds
    
    Returns:
        Decorator
    """
    return EndpointRateLimiter(requests, window)
