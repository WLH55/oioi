"""
Storyboards 模块路由

提供分镜管理相关的 API 端点
"""

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.episodes.dependencies import valid_episode_id
from src.core.schemas import ApiResponse, ListResponse

from src.episodes.models import Episode

from .dependencies import get_storyboard_service
from .schemas import (
    FramePromptListResponse,
    FramePromptResponse,
    StoryboardGenerationRequest,
    StoryboardGenerationResponse,
    StoryboardResponse,
    StoryboardUpdate,
)
from .service import StoryboardService

router = APIRouter()


# ============================================================================
# 分镜管理端点
# ============================================================================

@router.get(
    "/list",
    summary="获取分镜列表",
    description="获取分镜列表，支持按集数筛选，支持分页",
    response_model=ApiResponse[ListResponse[StoryboardResponse]]
)
async def list_storyboards(
    episode_id: int | None = Query(None, description="集数ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: StoryboardService = Depends(get_storyboard_service)
) -> ApiResponse[ListResponse[StoryboardResponse]]:
    """
    获取分镜列表

    - **episode_id**: 可选，筛选指定集数的分镜
    - **page**: 页码，从1开始
    - **page_size**: 每页数量，最大100
    """
    skip = (page - 1) * page_size
    storyboards, total = await service.get_list(
        episode_id=episode_id,
        skip=skip,
        limit=page_size
    )

    items = [
        StoryboardResponse.model_validate(sb) for sb in storyboards
    ]

    return ApiResponse.success(data=ListResponse(total=total, items=items))


@router.get(
    "/info",
    summary="获取分镜详情",
    description="根据ID获取分镜的详细信息",
    response_model=ApiResponse[StoryboardResponse]
)
async def get_storyboard_info(
    storyboard_id: int = Query(..., description="分镜ID"),
    service: StoryboardService = Depends(get_storyboard_service)
) -> ApiResponse[StoryboardResponse]:
    """
    获取分镜详情

    - **storyboard_id**: 分镜ID
    """
    storyboard = await service.get_by_id(storyboard_id)
    return ApiResponse.success(data=StoryboardResponse.model_validate(storyboard))


@router.post(
    "/update",
    summary="更新分镜",
    description="更新指定分镜的信息",
    response_model=ApiResponse[StoryboardResponse]
)
async def update_storyboard(
    storyboard_id: int = Query(..., description="分镜ID"),
    update_data: StoryboardUpdate = None,
    service: StoryboardService = Depends(get_storyboard_service)
) -> ApiResponse[StoryboardResponse]:
    """
    更新分镜信息

    - **storyboard_id**: 分镜ID
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

    storyboard = await service.update(storyboard_id, data_dict)
    return ApiResponse.success(data=StoryboardResponse.model_validate(storyboard))


@router.post(
    "/delete",
    summary="删除分镜",
    description="删除指定的分镜",
    response_model=ApiResponse[dict]
)
async def delete_storyboard(
    storyboard_id: int = Query(..., description="分镜ID"),
    service: StoryboardService = Depends(get_storyboard_service)
) -> ApiResponse[dict]:
    """
    删除分镜

    - **storyboard_id**: 分镜ID
    """
    await service.delete(storyboard_id)
    return ApiResponse.success(data={"storyboard_id": storyboard_id})


# ============================================================================
# 集数关联端点
# ============================================================================

@router.get(
    "/by-episode",
    summary="获取集数的所有分镜",
    description="获取指定集数的所有分镜（不分页）",
    response_model=ApiResponse[list[StoryboardResponse]]
)
async def list_storyboards_by_episode(
    episode: Episode = Depends(valid_episode_id),
    service: StoryboardService = Depends(get_storyboard_service)
) -> ApiResponse[list[StoryboardResponse]]:
    """
    获取指定集数的所有分镜

    - **episode_id**: 集数ID（通过依赖注入验证）
    """
    storyboards = await service.get_by_episode(episode.id)

    items = [
        StoryboardResponse.model_validate(sb) for sb in storyboards
    ]

    return ApiResponse.success(data=items)


@router.post(
    "/generate",
    summary="为集数生成分镜",
    description="使用 AI 为指定集数生成分镜",
    response_model=ApiResponse[StoryboardGenerationResponse]
)
async def generate_storyboards(
    episode_id: int = Query(..., description="集数ID"),
    request: StoryboardGenerationRequest | None = None,
    background_tasks: BackgroundTasks = None,
    service: StoryboardService = Depends(get_storyboard_service),
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[StoryboardGenerationResponse]:
    """
    为集数生成分镜

    创建后台任务来使用 AI 生成分镜

    - **episode_id**: 集数ID
    - **request**: 可选的生成参数
    """
    from .tasks import process_storyboard_generation

    task_id = await service.generate_for_episode(episode_id)

    # 添加后台任务
    if background_tasks and request:
        background_tasks.add_task(
            process_storyboard_generation,
            episode_id,
            request.model_dump() if request else {},
            task_id
        )

    return ApiResponse.success(data=StoryboardGenerationResponse(
        message="分镜生成已开始",
        episode_id=episode_id,
        task_id=task_id,
        status="pending"
    ))


# ============================================================================
# 帧提示词端点
# ============================================================================

@router.post(
    "/frame-prompt",
    summary="生成帧提示词",
    description="为分镜生成 AI 帧提示词",
    response_model=ApiResponse[FramePromptResponse]
)
async def generate_frame_prompt(
    storyboard_id: int = Query(..., description="分镜ID"),
    frame_type: str = Query("key", description="帧类型"),
    service: StoryboardService = Depends(get_storyboard_service)
) -> ApiResponse[FramePromptResponse]:
    """
    生成帧提示词

    - **storyboard_id**: 分镜ID
    - **frame_type**: 帧类型 (first, key, last, panel, action)
    """
    # 获取分镜以获取提示词
    storyboard = await service.get_by_id(storyboard_id)
    prompt = storyboard.image_prompt or ""

    frame_prompt = await service.create_frame_prompt(
        storyboard_id=storyboard_id,
        frame_type=frame_type,
        prompt=prompt
    )

    return ApiResponse.success(data=FramePromptResponse.model_validate(frame_prompt))


@router.get(
    "/frame-prompts",
    summary="获取分镜的帧提示词",
    description="获取指定分镜的所有帧提示词",
    response_model=ApiResponse[FramePromptListResponse]
)
async def get_storyboard_frame_prompts(
    storyboard_id: int = Query(..., description="分镜ID"),
    service: StoryboardService = Depends(get_storyboard_service)
) -> ApiResponse[FramePromptListResponse]:
    """
    获取分镜的所有帧提示词

    - **storyboard_id**: 分镜ID
    """
    # 验证分镜存在
    await service.get_by_id(storyboard_id)

    frame_prompts = await service.get_frame_prompts(storyboard_id)

    return ApiResponse.success(data=FramePromptListResponse(
        storyboard_id=storyboard_id,
        frame_prompts=[FramePromptResponse.model_validate(fp) for fp in frame_prompts],
        count=len(frame_prompts)
    ))
