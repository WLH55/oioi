"""
Videos 模块路由

提供视频生成相关的 API 端点
"""
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Body, Depends

from src.middlewares.rate_limit import limiter
from src.core.schemas import ApiResponse

from .dependencies import get_video_service
from .schemas import VideoGenerationCreate, VideoGenerationResponse
from .service import VideoGenerationService, process_batch_video_generation

router = APIRouter(prefix="/videos", tags=["Videos"])


@router.get(
    "/list",
    summary="获取视频生成列表",
    description="分页获取视频生成记录列表，支持多种过滤条件"
)
async def list_video_generations(
    service: Annotated[VideoGenerationService, Depends(get_video_service)],
    page: int = 1,
    page_size: int = 20,
    drama_id: int | None = None,
    storyboard_id: int | None = None,
    status_filter: str | None = None
) -> ApiResponse:
    """
    获取视频生成列表

    支持按剧目、分镜、状态等条件过滤
    """
    result = await service.list_generations(
        page=page,
        page_size=page_size,
        drama_id=drama_id,
        storyboard_id=storyboard_id,
        status_filter=status_filter
    )
    return ApiResponse(data=result)


@router.post(
    "/create",
    summary="创建视频生成任务",
    description="创建一个新的视频生成任务"
)
@limiter.limit("10/minute")
async def create_video_generation(
    request: VideoGenerationCreate,
    background_tasks: BackgroundTasks,
    service: Annotated[VideoGenerationService, Depends(get_video_service)]
) -> ApiResponse[VideoGenerationResponse]:
    """
    创建视频生成任务

    - **prompt**: 视频生成提示词
    - **provider**: AI 提供商（如 openai, doubao）
    - **model**: 模型名称
    - **duration**: 视频时长（秒）
    - **image_url**: 可选的参考图片 URL
    """
    result = await service.create_generation(request)
    return ApiResponse(data=result)


@router.get(
    "/get",
    summary="获取视频生成详情",
    description="根据 ID 获取视频生成任务的详细信息"
)
async def get_video_generation(
    gen_id: int,
    service: Annotated[VideoGenerationService, Depends(get_video_service)]
) -> ApiResponse[VideoGenerationResponse]:
    """
    获取视频生成详情

    - **gen_id**: 视频生成任务 ID
    """
    result = await service.get_generation(gen_id)
    return ApiResponse(data=result)


@router.post(
    "/delete",
    summary="删除视频生成记录",
    description="删除指定的视频生成记录"
)
async def delete_video_generation(
    gen_id: int,
    service: Annotated[VideoGenerationService, Depends(get_video_service)]
) -> ApiResponse[dict]:
    """
    删除视频生成记录

    - **gen_id**: 视频生成任务 ID
    """
    await service.delete_generation(gen_id)
    return ApiResponse(data={"message": "视频生成记录已删除", "gen_id": gen_id})


@router.post(
    "/image/generate",
    summary="从图片生成视频",
    description="基于现有图片生成视频"
)
async def generate_video_from_image(
    image_gen_id: int,
    background_tasks: BackgroundTasks,
    service: Annotated[VideoGenerationService, Depends(get_video_service)],
    prompt: str | None = Body(None, embed=True),
    provider: str = Body("doubao", embed=True),
    duration: int = Body(5, embed=True)
) -> ApiResponse[VideoGenerationResponse]:
    """
    从图片生成视频

    - **image_gen_id**: 图片生成任务 ID
    - **prompt**: 可选的自定义提示词
    - **provider**: AI 提供商
    - **duration**: 视频时长（秒）
    """
    result = await service.create_from_image(image_gen_id, prompt, provider, duration)
    return ApiResponse(data=result)


@router.post(
    "/episode/batch-generate",
    summary="批量生成章节视频",
    description="为章节的所有分镜批量生成视频"
)
async def batch_generate_episode_videos(
    episode_id: int,
    background_tasks: BackgroundTasks,
    service: Annotated[VideoGenerationService, Depends(get_video_service)]
) -> ApiResponse[dict]:
    """
    批量生成章节视频

    - **episode_id**: 章节 ID
    """
    task_id = await service.batch_generate_for_episode(episode_id)

    # 添加后台任务
    background_tasks.add_task(
        process_batch_video_generation,
        task_id,
        episode_id
    )

    return ApiResponse(data={
        "message": "批量视频生成任务已创建",
        "task_id": task_id,
        "status": "pending",
        "episode_id": episode_id
    })
