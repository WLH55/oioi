"""
Unified response wrapper to match Go backend format
"""
from typing import Optional, Any
from datetime import datetime


class APIResponse:
    """统一的 API 响应格式，与 Go 后端保持一致"""

    @staticmethod
    def success(data: Any = None, message: Optional[str] = None) -> dict:
        """
        成功响应
        对应 Go: response.Success(c, data)
        """
        return {
            "success": True,
            "data": data,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    @staticmethod
    def created(data: Any = None) -> dict:
        """
        创建成功响应 (HTTP 201)
        对应 Go: response.Created(c, data)
        """
        return {
            "success": True,
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    @staticmethod
    def success_with_pagination(
        items: Any,
        total: int,
        page: int,
        page_size: int
    ) -> dict:
        """
        分页响应
        对应 Go: response.SuccessWithPagination(c, items, total, page, pageSize)
        """
        total_pages = (total + page_size - 1) // page_size
        return {
            "success": True,
            "data": {
                "items": items,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": total_pages
                }
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    @staticmethod
    def error(code: str, message: str, details: Optional[Any] = None) -> dict:
        """
        错误响应
        对应 Go: response.Error(c, statusCode, errCode, message)
        """
        error_obj = {
            "code": code,
            "message": message
        }
        if details is not None:
            error_obj["details"] = details

        return {
            "success": False,
            "error": error_obj,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    @staticmethod
    def bad_request(message: str) -> dict:
        """400 Bad Request"""
        return APIResponse.error("BAD_REQUEST", message)

    @staticmethod
    def unauthorized(message: str = "Unauthorized") -> dict:
        """401 Unauthorized"""
        return APIResponse.error("UNAUTHORIZED", message)

    @staticmethod
    def forbidden(message: str = "Forbidden") -> dict:
        """403 Forbidden"""
        return APIResponse.error("FORBIDDEN", message)

    @staticmethod
    def not_found(message: str = "Resource not found") -> dict:
        """404 Not Found"""
        return APIResponse.error("NOT_FOUND", message)

    @staticmethod
    def internal_error(message: str = "Internal server error") -> dict:
        """500 Internal Server Error"""
        return APIResponse.error("INTERNAL_ERROR", message)
