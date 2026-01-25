"""
Rate limiting middleware for API protection
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from app.core.exceptions import TooManyRequestsException
import time


def get_user_id(request: Request) -> str:
    """
    Get user identifier for rate limiting
    Falls back to IP address if no user ID is available
    """
    # Try to get user ID from headers (e.g., from JWT token)
    user_id = request.headers.get("X-User-ID")
    if user_id:
        return f"user:{user_id}"

    # Fall back to IP address
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_user_id,
    default_limits=["200/hour"],  # Default limit if not specified
    storage_uri="memory://",  # Use in-memory storage (for production, use Redis)
    headers_enabled=True,  # Enable rate limit headers in response
)


class RateLimiter:
    """Rate limiter wrapper with configurable limits"""

    def __init__(self):
        self.limiter = limiter

    def limit(self, limit_string: str):
        """
        Apply a rate limit to an endpoint

        Args:
            limit_string: Rate limit string (e.g., "10/minute", "100/hour")

        Example:
            @rate_limiter.limit("10/minute")
            async def my_endpoint(request: Request):
                return {"message": "Hello"}
        """
        return self.limiter.limit(limit_string)

    def check_request_limit(self, request: Request) -> bool:
        """
        Check if request is within rate limit without raising error

        Returns:
            True if within limit, False otherwise
        """
        try:
            # Try to consume from the default limit
            key = self.limiter.key_func(request)
            # This will raise RateLimitExceeded if limit is hit
            self.limiter._limiter.check()
            return True
        except RateLimitExceeded:
            return False


# Global rate limiter instance
rate_limiter = RateLimiter()


# Custom error handler for rate limit exceeded
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom error handler for rate limit exceeded"""
    raise TooManyRequestsException(
        message=f"Rate limit exceeded. Please try again later.",
        details={
            "limit": exc.detail,
            "retry_after": str(int(exc.retry_after) if hasattr(exc, 'retry_after') else 60)
        }
    )


# Configure default error handler
limiter.limiter._rate_limit_exceeded_handler = rate_limit_exceeded_handler
