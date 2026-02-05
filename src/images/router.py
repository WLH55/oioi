"""
Images 模块路由

提供图片生成相关的 API 端点
"""
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Body, Depends

from src.middlewares.rate_limit import limiter
from src.core.schemas import ApiResponse

from .dependencies import get_image_service
from .schemas import (
    BackgroundImageResponse,
    ImageGenerationCreate,
    ImageGenerationResponse,
    ImageListResponse,
)
from .service import (
    ImageGenerationService,
    process_background_extraction,
    process_batch_image_generation,
)

router = APIRouter(prefix="/images", tags=["Images"])


@router.get(
    "/list",
    summary="获取图片生成列表",
    description="分页获取图片生成记录列表，支持多种过滤条件"
)
async def list_image_generations(
    service: Annotated[ImageGenerationService, Depends(get_image_service)],
    page: int = 1,
    page_size: int = 20,
    drama_id: int | None = None,
    scene_id: int | None = None,
    storyboard_id: int | None = None,
    frame_type: str | None = None,
    status_filter: str | None = None
) -> ApiResponse[list[ImageListResponse]]:
    """
    获取图片生成列表

    支持按剧目、场景、分镜、帧类型、状态等条件过滤
    """
    result = await service.list_generations(
        page=page,
        page_size=page_size,
        drama_id=drama_id,
        scene_id=scene_id,
        storyboard_id=storyboard_id,
        frame_type=frame_type,
        status_filter=status_filter
    )
    return ApiResponse(data=result)


@router.post(
    "/create",
    summary="创建图片生成任务",
    description="创建一个新的图片生成任务"
)
@limiter.limit("20/minute")
async def create_image_generation(
    request: ImageGenerationCreate,
    background_tasks: BackgroundTasks,
    service: Annotated[ImageGenerationService, Depends(get_image_service)]
) -> ApiResponse[ImageGenerationResponse]:
    """
    创建图片生成任务

    - **prompt**: 图片生成提示词
    - **provider**: AI 提供商（如 openai, doubao）
    - **model**: 模型名称
    - **size**: 图片尺寸
    - **quality**: 图片质量
    """
    result = await service.create_generation(request)
    return ApiResponse(data=result)


@router.get(
    "/get",
    summary="获取图片生成详情",
    description="根据 ID 获取图片生成任务的详细信息"
)
async def get_image_generation(
    gen_id: int,
    service: Annotated[ImageGenerationService, Depends(get_image_service)]
) -> ApiResponse[ImageGenerationResponse]:
    """
    获取图片生成详情

    - **gen_id**: 图片生成任务 ID
    """
    result = await service.get_generation(gen_id)
    return ApiResponse(data=result)


@router.post(
    "/delete",
    summary="删除图片生成记录",
    description="删除指定的图片生成记录"
)
async def delete_image_generation(
    gen_id: int,
    service: Annotated[ImageGenerationService, Depends(get_image_service)]
) -> ApiResponse[dict]:
    """
    删除图片生成记录

    - **gen_id**: 图片生成任务 ID
    """
    await service.delete_generation(gen_id)
    return ApiResponse(data={"message": "图片生成记录已删除", "gen_id": gen_id})


@router.post(
    "/scene/generate",
    summary="为场景生成图片",
    description="为指定场景创建图片生成任务"
)
async def generate_image_for_scene(
    scene_id: int,
    background_tasks: BackgroundTasks,
    service: Annotated[ImageGenerationService, Depends(get_image_service)]
) -> ApiResponse[ImageGenerationResponse]:
    """
    为场景生成图片

    - **scene_id**: 场景 ID
    """
    result = await service.generate_for_scene(scene_id)
    return ApiResponse(data=result)


@router.get(
    "/episode/backgrounds",
    summary="获取章节场景背景图",
    description="获取指定章节的所有场景背景图片"
)
async def get_episode_backgrounds(
    episode_id: int,
    service: Annotated[ImageGenerationService, Depends(get_image_service)]
) -> ApiResponse[list[BackgroundImageResponse]]:
    """
    获取章节场景背景图

    - **episode_id**: 章节 ID
    """
    result = await service.get_backgrounds_for_episode(episode_id)
    return ApiResponse(data={"episode_id": episode_id, "backgrounds": result, "count": len(result)})


@router.post(
    "/episode/backgrounds/extract",
    summary="提取章节场景背景",
    description="为章节的所有场景创建背景提取任务"
)
async def extract_episode_backgrounds(
    episode_id: int,
    background_tasks: BackgroundTasks,
    service: Annotated[ImageGenerationService, Depends(get_image_service)],
    model: str | None = Body(None, embed=True)
) -> ApiResponse[dict]:
    """
    提取章节场景背景

    - **episode_id**: 章节 ID
    - **model**: 可选的模型名称
    """
    task_id = await service.extract_backgrounds_for_episode(episode_id, model)

    # 添加后台任务
    background_tasks.add_task(
        process_background_extraction,
        task_id,
        episode_id,
        model or ""
    )

    return ApiResponse(data={
        "message": "场景提取任务已创建，正在后台处理",
        "task_id": task_id,
        "status": "pending",
        "episode_id": episode_id
    })


@router.post(
    "/episode/batch-generate",
    summary="批量生成章节图片",
    description="为章节的所有分镜批量生成图片"
)
async def batch_generate_episode_images(
    episode_id: int,
    background_tasks: BackgroundTasks,
    service: Annotated[ImageGenerationService, Depends(get_image_service)]
) -> ApiResponse[dict]:
    """
    批量生成章节图片

    - **episode_id**: 章节 ID
    """
    task_id = await service.batch_generate_for_episode(episode_id)

    # 添加后台任务
    background_tasks.add_task(
        process_batch_image_generation,
        task_id,
        episode_id
    )

    return ApiResponse(data={
        "message": "批量图片生成任务已创建",
        "task_id": task_id,
        "status": "pending",
        "episode_id": episode_id
    })
