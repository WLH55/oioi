"""
Episodes 模块路由

提供集数相关的 API 端点
"""
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dramas.dependencies import valid_drama_id
from src.core.schemas import ApiResponse, ListResponse

from src.dramas.models import Drama

from .dependencies import get_episode_service
from .schemas import (
    EpisodeDetailResponse,
    EpisodeDownloadResponse,
    EpisodeFinalizeRequest,
    EpisodeFinalizeResponse,
    EpisodeResponse,
    EpisodeUpdate,
)
from .service import EpisodeService

router = APIRouter()


# ============================================================================
# 集数管理端点
# ============================================================================

@router.get(
    "/list",
    summary="获取集数列表",
    description="获取指定剧目的集数列表，支持分页",
    response_model=ApiResponse[ListResponse[EpisodeResponse]]
)
async def list_episodes(
    drama_id: int | None = Query(None, description="剧目ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: EpisodeService = Depends(get_episode_service)
) -> ApiResponse[ListResponse[EpisodeResponse]]:
    """
    获取集数列表

    - **drama_id**: 可选，筛选指定剧目的集数
    - **page**: 页码，从1开始
    - **page_size**: 每页数量，最大100
    """
    skip = (page - 1) * page_size
    episodes, total = await service.get_list(drama_id=drama_id, skip=skip, limit=page_size)

    items = [
        EpisodeResponse.model_validate(ep) for ep in episodes
    ]

    return ApiResponse.success(data=ListResponse(total=total, items=items))


@router.get(
    "/info",
    summary="获取集数详情",
    description="根据ID获取集数的详细信息",
    response_model=ApiResponse[EpisodeDetailResponse]
)
async def get_episode_info(
    episode_id: int = Query(..., description="集数ID"),
    service: EpisodeService = Depends(get_episode_service)
) -> ApiResponse[EpisodeDetailResponse]:
    """
    获取集数详情

    - **episode_id**: 集数ID
    """
    detail = await service.get_detail(episode_id)
    return ApiResponse.success(data=EpisodeDetailResponse(**detail))


@router.post(
    "/update",
    summary="更新集数",
    description="更新指定集数的信息",
    response_model=ApiResponse[EpisodeResponse]
)
async def update_episode(
    episode_id: int = Query(..., description="集数ID"),
    update_data: EpisodeUpdate = None,
    service: EpisodeService = Depends(get_episode_service)
) -> ApiResponse[EpisodeResponse]:
    """
    更新集数信息

    - **episode_id**: 集数ID
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

    episode = await service.update(episode_id, data_dict)
    return ApiResponse.success(data=EpisodeResponse.model_validate(episode))


@router.post(
    "/delete",
    summary="删除集数",
    description="删除指定的集数",
    response_model=ApiResponse[dict[str, Any]]
)
async def delete_episode(
    episode_id: int = Query(..., description="集数ID"),
    service: EpisodeService = Depends(get_episode_service)
) -> ApiResponse[dict[str, Any]]:
    """
    删除集数

    - **episode_id**: 集数ID
    """
    await service.delete(episode_id)
    return ApiResponse.success(data={"episode_id": episode_id})


@router.post(
    "/finalize",
    summary="完成集数制作",
    description="标记集数为完成状态并触发视频合成任务",
    response_model=ApiResponse[EpisodeFinalizeResponse]
)
async def finalize_episode(
    episode_id: int = Query(..., description="集数ID"),
    request: EpisodeFinalizeRequest | None = None,
    background_tasks: BackgroundTasks = None,
    service: EpisodeService = Depends(get_episode_service),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[EpisodeFinalizeResponse]:
    """
    完成集数制作

    标记集数为完成状态并创建视频合成任务

    - **episode_id**: 集数ID
    - **request**: 可选的时间线数据，包含视频片段信息
    """
    from .tasks import process_episode_finalization

    timeline_data = request.timeline_data if request else None
    task_id = await service.finalize(episode_id, timeline_data)

    # 添加后台任务
    if background_tasks:
        background_tasks.add_task(
            process_episode_finalization,
            episode_id,
            timeline_data,
            task_id
        )

    return ApiResponse.success(data=EpisodeFinalizeResponse(
        message="集数完成制作，视频合成任务已创建",
        episode_id=episode_id,
        task_id=task_id,
        status="processing"
    ))


@router.get(
    "/download",
    summary="获取集数下载信息",
    description="获取集数视频的下载链接和元数据",
    response_model=ApiResponse[EpisodeDownloadResponse]
)
async def get_episode_download(
    episode_id: int = Query(..., description="集数ID"),
    service: EpisodeService = Depends(get_episode_service)
) -> ApiResponse[EpisodeDownloadResponse]:
    """
    获取集数下载信息

    - **episode_id**: 集数ID
    """
    download_info = await service.get_download_info(episode_id)
    return ApiResponse.success(data=EpisodeDownloadResponse(**download_info))


# ============================================================================
# 剧目关联端点
# ============================================================================

@router.get(
    "/by-drama",
    summary="获取剧目的所有集数",
    description="获取指定剧目的所有集数（不分页）",
    response_model=ApiResponse[list[EpisodeResponse]]
)
async def list_episodes_by_drama(
    drama: Drama = Depends(valid_drama_id),
    service: EpisodeService = Depends(get_episode_service)
) -> ApiResponse[list[EpisodeResponse]]:
    """
    获取指定剧目的所有集数

    - **drama_id**: 剧目ID（通过依赖注入验证）
    """
    episodes, _ = await service.get_list(drama_id=drama.id, skip=0, limit=1000)

    items = [
        EpisodeResponse.model_validate(ep) for ep in episodes
    ]

    return ApiResponse.success(data=items)
