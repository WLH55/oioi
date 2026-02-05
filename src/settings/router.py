"""
系统设置路由

提供系统配置和设置的查询、更新接口。
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.core.config import settings
from src.core.schemas import ApiResponse

router = APIRouter()


# ========== 请求模型 ==========

class UpdateLanguageRequest(BaseModel):
    """更新语言设置请求"""
    language: str = Field(..., description="语言代码，如 zh-CN, en-US")


# ========== GET 接口 ==========

@router.get("/language", summary="获取语言设置", response_model=ApiResponse)
async def get_language() -> ApiResponse:
    """
    获取系统语言设置

    Returns:
        ApiResponse: 包含当前语言设置的响应
    """
    return ApiResponse.success(data={
        "language": settings.LANGUAGE
    })


@router.get("/all", summary="获取所有系统设置", response_model=ApiResponse)
async def get_all_settings() -> ApiResponse:
    """
    获取所有系统设置（不包含敏感信息）

    返回系统的公开配置信息。

    Returns:
        ApiResponse: 包含系统设置的响应
    """
    return ApiResponse.success(data={
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "language": settings.LANGUAGE,
        "storage_type": settings.STORAGE_TYPE,
        "default_ai_provider": settings.DEFAULT_AI_PROVIDER,
        "cors_origins": settings.CORS_ORIGINS
    })


# ========== POST 接口 ==========

@router.post("/update-language", summary="更新语言设置", response_model=ApiResponse)
async def update_language(request: UpdateLanguageRequest) -> ApiResponse:
    """
    更新系统语言设置

    注意：当前实现仅返回更新确认，实际应用中需要持久化设置。

    Args:
        request: 包含新语言代码的请求

    Returns:
        ApiResponse: 更新结果
    """
    # 实际实现中，这里需要更新持久化存储
    # 目前仅返回确认响应
    return ApiResponse.success(data={
        "language": request.language
    }, message="语言设置已更新")
