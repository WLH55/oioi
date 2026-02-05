"""
Video Merges 模块路由

提供视频合成相关的 API 端点
"""
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends

from src.core.schemas import ApiResponse

from .dependencies import get_video_merge_service
from .schemas import VideoMergeCreate, VideoMergeResponse
from .service import VideoMergeService, process_video_merge_task

router = APIRouter(prefix="/video-merges", tags=["Video Merges"])


@router.get(
    "/list",
    summary="获取视频合成列表",
    description="分页获取视频合成记录列表，支持多种过滤条件"
)
async def list_video_merges(
    service: Annotated[VideoMergeService, Depends(get_video_merge_service)],
    page: int = 1,
    page_size: int = 20,
    episode_id: int = None,
    status_filter: str = None
) -> ApiResponse:
    """
    获取视频合成列表

    支持按章节、状态等条件过滤
    """
    result = await service.list_merges(
        page=page,
        page_size=page_size,
        episode_id=episode_id,
        status_filter=status_filter
    )
    return ApiResponse(data=result)


@router.post(
    "/create",
    summary="创建视频合成任务",
    description="创建一个新的视频合成任务"
)
async def create_video_merge(
    merge: VideoMergeCreate,
    background_tasks: BackgroundTasks,
    service: Annotated[VideoMergeService, Depends(get_video_merge_service)]
) -> ApiResponse[VideoMergeResponse]:
    """
    创建视频合成任务

    - **episode_id**: 章节 ID
    - **drama_id**: 剧目 ID
    - **title**: 标题
    - **scenes**: 场景片段列表
    """
    result = await service.create_merge(merge)

    # 添加后台任务处理视频合成
    background_tasks.add_task(
        process_video_merge_task,
        result.id,
        [scene.model_dump() for scene in merge.scenes],
        f"{result.output_path}" if hasattr(result, 'output_path') else ""
    )

    return ApiResponse(data={
        "message": "视频合成任务已创建",
        "merge_id": result.id,
        "task_id": result.task_id,
        "status": result.status,
        "episode_id": merge.episode_id
    })


@router.get(
    "/get",
    summary="获取视频合成详情",
    description="根据 ID 获取视频合成任务的详细信息"
)
async def get_video_merge(
    merge_id: int,
    service: Annotated[VideoMergeService, Depends(get_video_merge_service)]
) -> ApiResponse[VideoMergeResponse]:
    """
    获取视频合成详情

    - **merge_id**: 视频合成任务 ID
    """
    result = await service.get_merge(merge_id)
    return ApiResponse(data=result)


@router.post(
    "/delete",
    summary="删除视频合成记录",
    description="删除指定的视频合成记录"
)
async def delete_video_merge(
    merge_id: int,
    service: Annotated[VideoMergeService, Depends(get_video_merge_service)]
) -> ApiResponse[dict]:
    """
    删除视频合成记录

    - **merge_id**: 视频合成任务 ID
    """
    await service.delete_merge(merge_id)
    return ApiResponse(data={"message": "视频合成记录已删除", "merge_id": merge_id})
