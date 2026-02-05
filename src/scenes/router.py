"""
Scenes 模块路由

提供场景相关的 API 端点
"""
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dramas.dependencies import valid_drama_id
from src.episodes.dependencies import valid_episode_id
from src.core.schemas import ApiResponse, ListResponse

from src.dramas.models import Drama
from src.episodes.models import Episode

from .dependencies import get_scene_service
from .schemas import (
    SceneDetailResponse,
    SceneImageGenerationResponse,
    ScenePromptUpdate,
    SceneResponse,
    SceneUpdate,
)
from .service import SceneService

router = APIRouter()


# ============================================================================
# 场景管理端点
# ============================================================================

@router.get(
    "/list",
    summary="获取场景列表",
    description="获取场景列表，支持按剧目或集数筛选，支持分页",
    response_model=ApiResponse[ListResponse[SceneResponse]]
)
async def list_scenes(
    drama_id: int = Query(None, description="剧目ID"),
    episode_id: int = Query(None, description="集数ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: SceneService = Depends(get_scene_service)
) -> ApiResponse[ListResponse[SceneResponse]]:
    """
    获取场景列表

    - **drama_id**: 可选，筛选指定剧目的场景
    - **episode_id**: 可选，筛选指定集数的场景
    - **page**: 页码，从1开始
    - **page_size**: 每页数量，最大100
    """
    skip = (page - 1) * page_size
    scenes, total = await service.get_list(
        drama_id=drama_id,
        episode_id=episode_id,
        skip=skip,
        limit=page_size
    )

    items = [
        SceneResponse.model_validate(scene) for scene in scenes
    ]

    return ApiResponse.success(data=ListResponse(total=total, items=items))


@router.get(
    "/info",
    summary="获取场景详情",
    description="根据ID获取场景的详细信息",
    response_model=ApiResponse[SceneDetailResponse]
)
async def get_scene_info(
    scene_id: int = Query(..., description="场景ID"),
    service: SceneService = Depends(get_scene_service)
) -> ApiResponse[SceneDetailResponse]:
    """
    获取场景详情

    - **scene_id**: 场景ID
    """
    detail = await service.get_detail(scene_id)
    return ApiResponse.success(data=SceneDetailResponse(**detail))


@router.post(
    "/update",
    summary="更新场景",
    description="更新指定场景的信息",
    response_model=ApiResponse[SceneResponse]
)
async def update_scene(
    scene_id: int = Query(..., description="场景ID"),
    update_data: SceneUpdate = None,
    service: SceneService = Depends(get_scene_service)
) -> ApiResponse[SceneResponse]:
    """
    更新场景信息

    - **scene_id**: 场景ID
    - **update_data**: 要更新的字段（JSON body）
    """
    if update_data is None:
        from src.exceptions import BusinessValidationException
        raise BusinessValidationException("请提供更新数据")

    # 转换为字典，过滤 None 值
    data_dict = update_data.model_dump(exclude_unset=True)
    if not data_dict:
        from src.exceptions import BusinessValidationException
        raise BusinessValidationException("没有提供任何要更新的字段")

    scene = await service.update(scene_id, data_dict)
    return ApiResponse.success(data=SceneResponse.model_validate(scene))


@router.post(
    "/update-prompt",
    summary="更新场景提示词",
    description="更新场景的 AI 提示词",
    response_model=ApiResponse[SceneResponse]
)
async def update_scene_prompt(
    scene_id: int = Query(..., description="场景ID"),
    request: ScenePromptUpdate = None,
    service: SceneService = Depends(get_scene_service)
) -> ApiResponse[SceneResponse]:
    """
    更新场景提示词

    - **scene_id**: 场景ID
    - **request**: 包含新提示词的请求体
    """
    if request is None:
        from src.exceptions import BusinessValidationException
        raise BusinessValidationException("请提供提示词")

    scene = await service.update_prompt(scene_id, request.prompt)
    return ApiResponse.success(data=SceneResponse.model_validate(scene))


@router.post(
    "/delete",
    summary="删除场景",
    description="删除指定的场景",
    response_model=ApiResponse[dict[str, Any]]
)
async def delete_scene(
    scene_id: int = Query(..., description="场景ID"),
    service: SceneService = Depends(get_scene_service)
) -> ApiResponse[dict[str, Any]]:
    """
    删除场景

    - **scene_id**: 场景ID
    """
    await service.delete(scene_id)
    return ApiResponse.success(data={"scene_id": scene_id})


@router.post(
    "/generate-image",
    summary="生成场景图片",
    description="为场景生成 AI 图片",
    response_model=ApiResponse[SceneImageGenerationResponse]
)
async def generate_scene_image(
    scene_id: int = Query(..., description="场景ID"),
    background_tasks: BackgroundTasks = None,
    service: SceneService = Depends(get_scene_service),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[SceneImageGenerationResponse]:
    """
    生成场景图片

    创建后台任务来生成场景的 AI 图片

    - **scene_id**: 场景ID
    """
    from .tasks import process_scene_image_generation

    # 更新状态并获取任务ID
    task_id = await service.generate_image(scene_id)

    # 添加后台任务
    if background_tasks:
        background_tasks.add_task(process_scene_image_generation, scene_id, task_id)

    return ApiResponse.success(data=SceneImageGenerationResponse(
        message="场景图片生成已开始",
        scene_id=scene_id,
        task_id=task_id,
        status="pending"
    ))


# ============================================================================
# 剧目/集数关联端点
# ============================================================================

@router.get(
    "/by-drama",
    summary="获取剧目的所有场景",
    description="获取指定剧目的所有场景（不分页）",
    response_model=ApiResponse[list[SceneResponse]]
)
async def list_scenes_by_drama(
    drama: Drama = Depends(valid_drama_id),
    service: SceneService = Depends(get_scene_service)
) -> ApiResponse[list[SceneResponse]]:
    """
    获取指定剧目的所有场景

    - **drama_id**: 剧目ID（通过依赖注入验证）
    """
    scenes, _ = await service.get_list(drama_id=drama.id, skip=0, limit=1000)

    items = [
        SceneResponse.model_validate(scene) for scene in scenes
    ]

    return ApiResponse.success(data=items)


@router.get(
    "/by-episode",
    summary="获取集数的所有场景",
    description="获取指定集数的所有场景（不分页）",
    response_model=ApiResponse[list[SceneResponse]]
)
async def list_scenes_by_episode(
    episode: Episode = Depends(valid_episode_id),
    service: SceneService = Depends(get_scene_service)
) -> ApiResponse[list[SceneResponse]]:
    """
    获取指定集数的所有场景

    - **episode_id**: 集数ID（通过依赖注入验证）
    """
    scenes, _ = await service.get_list(episode_id=episode.id, skip=0, limit=1000)

    items = [
        SceneResponse.model_validate(scene) for scene in scenes
    ]

    return ApiResponse.success(data=items)
