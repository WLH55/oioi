"""
Global exception handlers to convert exceptions to unified response format
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Union

from .exceptions import APIException
from .response import APIResponse

logger = logging.getLogger(__name__)


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle custom API exceptions"""
    logger.error(
        f"API exception: {exc.code} - {exc.message}",
        extra={"path": request.url.path, "method": request.method}
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error(exc.code, exc.message, exc.details)
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions"""
    logger.error(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={"path": request.url.path, "method": request.method}
    )

    # Map HTTP status codes to error codes
    error_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        500: "INTERNAL_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }

    error_code = error_code_map.get(exc.status_code, "UNKNOWN_ERROR")

    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error(error_code, str(exc.detail))
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors"""
    logger.error(
        f"Validation error: {exc.errors()}",
        extra={"path": request.url.path, "method": request.method}
    )

    # Format validation errors
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=APIResponse.error("VALIDATION_ERROR", "Request validation failed", errors)
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other unhandled exceptions"""
    logger.error(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
        extra={"path": request.url.path, "method": request.method},
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse.error("INTERNAL_ERROR", "An unexpected error occurred")
    )
