"""
统一 API 响应模型和响应码定义

该模块定义了项目中所有 API 接口的统一响应格式，
包括 ApiResponse 泛型响应模型和 ResponseCode 响应码常量。
"""
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    统一 API 响应格式

    所有 API 接口都应返回此格式的响应，确保前端处理一致。

    Attributes:
        code: 响应码，200 表示成功
        message: 响应消息
        data: 响应数据，成功时返回具体数据，失败时为 None

    Example:
        >>> ApiResponse.success(data={"id": 1})
        ApiResponse(code=200, message='success', data={'id': 1})

        >>> ApiResponse.error(code=400, message="参数错误")
        ApiResponse(code=400, message='参数错误', data=None)
    """
    code: int = Field(default=200, description="响应码")
    message: str = Field(default="success", description="响应消息")
    data: T | None = Field(default=None, description="响应数据")

    @classmethod
    def success(cls, data: Any = None, message: str = "success") -> "ApiResponse[T]":
        """
        创建成功响应

        Args:
            data: 响应数据
            message: 成功消息

        Returns:
            ApiResponse: 成功响应实例
        """
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, code: int, message: str, data: Any = None) -> "ApiResponse[T]":
        """
        创建错误响应

        Args:
            code: 错误码
            message: 错误消息
            data: 附加数据

        Returns:
            ApiResponse: 错误响应实例
        """
        return cls(code=code, message=message, data=data)


class ListResponse(BaseModel, Generic[T]):
    """
    分页列表响应模型

    用于返回分页列表数据的标准格式。

    Attributes:
        items: 数据项列表
        total: 总数
        page: 当前页码
        page_size: 每页数量

    Example:
        >>> ListResponse(items=[{"id": 1}], total=10, page=1, page_size=20)
    """
    items: list[T] = Field(default_factory=list, description="数据项列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")


# PageResponse 是 ListResponse 的别名，保持向后兼容
PageResponse = ListResponse


class ResponseCode:
    """
    响应码常量

    遵循 HTTP 标准错误码规范，提供统一的响应码定义。

    使用示例:
        >>> ApiResponse.error(code=ResponseCode.NOT_FOUND, message="资源不存在")
    """
    # ========== 成功 ==========
    SUCCESS = 200           # 成功
    CREATED = 201           # 已创建

    # ========== 客户端错误 ==========
    BAD_REQUEST = 400       # 请求参数错误
    UNAUTHORIZED = 401      # 未授权
    FORBIDDEN = 403         # 禁止访问
    NOT_FOUND = 404         # 资源不存在
    CONFLICT = 409          # 资源冲突

    # ========== 服务器错误 ==========
    INTERNAL_ERROR = 500    # 服务器内部错误
    SERVICE_UNAVAILABLE = 503  # 服务不可用
