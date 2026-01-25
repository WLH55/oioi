"""
Unified exception classes to match Go backend error handling
"""
from typing import Optional, Any
from fastapi import HTTPException, status


class APIException(HTTPException):
    """基础 API 异常类"""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Any] = None
    ):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(status_code=status_code, detail=message)


class BadRequestException(APIException):
    """400 Bad Request"""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__("BAD_REQUEST", message, status.HTTP_400_BAD_REQUEST, details)


class UnauthorizedException(APIException):
    """401 Unauthorized"""

    def __init__(self, message: str = "Unauthorized", details: Optional[Any] = None):
        super().__init__("UNAUTHORIZED", message, status.HTTP_401_UNAUTHORIZED, details)


class ForbiddenException(APIException):
    """403 Forbidden"""

    def __init__(self, message: str = "Forbidden", details: Optional[Any] = None):
        super().__init__("FORBIDDEN", message, status.HTTP_403_FORBIDDEN, details)


class NotFoundException(APIException):
    """404 Not Found"""

    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__("NOT_FOUND", message, status.HTTP_404_NOT_FOUND, details)


class ConflictException(APIException):
    """409 Conflict"""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__("CONFLICT", message, status.HTTP_409_CONFLICT, details)


class InternalErrorException(APIException):
    """500 Internal Server Error"""

    def __init__(self, message: str = "Internal server error", details: Optional[Any] = None):
        super().__init__(
            "INTERNAL_ERROR",
            message,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            details
        )


class ServiceUnavailableException(APIException):
    """503 Service Unavailable"""

    def __init__(self, message: str = "Service unavailable", details: Optional[Any] = None):
        super().__init__(
            "SERVICE_UNAVAILABLE",
            message,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            details
        )


class TooManyRequestsException(APIException):
    """429 Too Many Requests"""

    def __init__(self, message: str = "Too many requests", details: Optional[Any] = None):
        super().__init__(
            "TOO_MANY_REQUESTS",
            message,
            status.HTTP_429_TOO_MANY_REQUESTS,
            details
        )
