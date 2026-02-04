"""
健康检查路由

提供应用健康状态检查的 API 端点。
"""
from fastapi import APIRouter

from src.config import settings
from src.schemas import ApiResponse

router = APIRouter()


@router.get("/health", summary="健康检查", response_model=ApiResponse)
async def health_check() -> ApiResponse:
    """
    应用健康状态检查端点

    返回应用的基本状态信息，用于负载均衡器健康检查和监控。

    Returns:
        ApiResponse: 包含应用状态、名称和版本的响应
    """
    return ApiResponse.success(data={
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    })
