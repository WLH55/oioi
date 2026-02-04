"""
AI 配置路由

提供 AI 服务配置的 CRUD 接口。
"""
from fastapi import APIRouter, Query, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.schemas import ApiResponse, ResponseCode
from src.ai_configs.schemas import (
    AIServiceConfigCreate,
    AIServiceConfigUpdate,
    AIServiceConfigResponse,
    TestConnectionRequest,
)
from src.ai_configs.service import AIConfigService
from src.ai_configs.dependencies import valid_config_id
from src.ai_configs.exceptions import AIConfigNotFound

router = APIRouter()


# ========== GET 接口 ==========

@router.get("/list", summary="获取 AI 配置列表", response_model=ApiResponse)
async def list_ai_configs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse:
    """
    获取 AI 服务配置列表（分页）

    Args:
        page: 页码
        page_size: 每页数量
        db: 数据库会话

    Returns:
        ApiResponse: 包含配置列表和分页信息的响应
    """
    skip = (page - 1) * page_size
    configs = await AIConfigService.list_configs(db, skip=skip, limit=page_size)

    # 获取总数（简化实现，实际应该单独查询）
    total = len(configs)

    return ApiResponse.success(data={
        "list": [AIServiceConfigResponse.model_validate(c) for c in configs],
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.get("/info", summary="获取 AI 配置详情", response_model=ApiResponse)
async def get_ai_config(
    config: AIServiceConfigResponse = Depends(valid_config_id)
) -> ApiResponse:
    """
    获取指定 AI 配置的详细信息

    Args:
        config: 通过依赖注入验证的配置对象

    Returns:
        ApiResponse: 配置详情
    """
    return ApiResponse.success(data=config)


# ========== POST 接口 ==========

@router.post("/create", summary="创建 AI 配置", response_model=ApiResponse)
async def create_ai_config(
    config_data: AIServiceConfigCreate,
    db: AsyncSession = Depends(get_db)
) -> ApiResponse:
    """
    创建新的 AI 服务配置

    Args:
        config_data: 配置数据
        db: 数据库会话

    Returns:
        ApiResponse: 创建的配置信息
    """
    config = await AIConfigService.create_config(config_data.model_dump(), db)
    return ApiResponse.success(
        data=AIServiceConfigResponse.model_validate(config),
        message="AI 配置创建成功"
    )


@router.post("/update", summary="更新 AI 配置", response_model=ApiResponse)
async def update_ai_config(
    config: AIServiceConfigResponse = Depends(valid_config_id),
    update_data: AIServiceConfigUpdate = None,
    db: AsyncSession = Depends(get_db)
) -> ApiResponse:
    """
    更新 AI 服务配置

    Args:
        config: 通过依赖注入验证的配置对象
        update_data: 更新数据
        db: 数据库会话

    Returns:
        ApiResponse: 更新后的配置信息
    """
    if update_data:
        update_dict = update_data.model_dump(exclude_unset=True)
        if update_dict:
            # 获取原始模型对象
            from src.ai_configs.models import AIServiceConfig
            from sqlalchemy import select

            result = await db.execute(
                select(AIServiceConfig).where(AIServiceConfig.id == config.id)
            )
            db_config = result.scalar_one_or_none()

            if db_config:
                config = await AIConfigService.update_config(db_config, update_dict, db)

    return ApiResponse.success(
        data=AIServiceConfigResponse.model_validate(config),
        message="AI 配置更新成功"
    )


@router.post("/delete", summary="删除 AI 配置", response_model=ApiResponse)
async def delete_ai_config(
    config: AIServiceConfigResponse = Depends(valid_config_id),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse:
    """
    删除 AI 服务配置

    Args:
        config: 通过依赖注入验证的配置对象
        db: 数据库会话

    Returns:
        ApiResponse: 删除结果
    """
    from src.ai_configs.models import AIServiceConfig
    from sqlalchemy import select

    result = await db.execute(
        select(AIServiceConfig).where(AIServiceConfig.id == config.id)
    )
    db_config = result.scalar_one_or_none()

    if db_config:
        await AIConfigService.delete_config(db_config, db)

    return ApiResponse.success(message="AI 配置删除成功")


@router.post("/test-connection", summary="测试 AI 服务连接", response_model=ApiResponse)
async def test_connection(
    request: TestConnectionRequest,
    background_tasks: BackgroundTasks
) -> ApiResponse:
    """
    测试 AI 服务连接

    Args:
        request: 测试连接请求
        background_tasks: 后台任务

    Returns:
        ApiResponse: 测试结果
    """
    # 这里是一个占位实现
    # 实际应用中应该调用 AI 服务进行测试

    return ApiResponse.success(data={
        "status": "success",
        "message": "连接测试已发起",
        "provider": request.provider,
        "note": "这是占位实现，实际应用中需要真实调用 AI 服务"
    }, message="连接测试已发起")
