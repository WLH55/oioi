from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.core.database import get_db
from app.core.response import APIResponse
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.video_merge import VideoMerge, VideoMergeStatus
from app.services.ffmpeg_service import FFmpegService
from app.core.config import settings
from pydantic import BaseModel
import uuid

router = APIRouter()

# Initialize FFmpeg service
ffmpeg_service = FFmpegService(output_dir=settings.LOCAL_STORAGE_PATH)


class SceneClip(BaseModel):
    scene_id: int
    video_url: str
    start_time: float
    end_time: float
    duration: float
    order: int
    transition: Optional[dict] = None


class VideoMergeCreate(BaseModel):
    episode_id: int
    drama_id: int
    title: str
    provider: str = "ffmpeg"
    model: Optional[str] = None
    scenes: List[SceneClip]


@router.get("")
async def list_merges(
    page: int = 1,
    page_size: int = 20,
    episode_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List video merges
    Corresponds to Go: ListMerges in video_merge.go
    """
    query = select(VideoMerge)

    if episode_id:
        query = query.where(VideoMerge.episode_id == episode_id)
    if status_filter:
        query = query.where(VideoMerge.status == status_filter)

    # Get total count
    from sqlalchemy import func
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    skip = (page - 1) * page_size
    query = query.offset(skip).limit(page_size).order_by(VideoMerge.created_at.desc())
    result = await db.execute(query)
    merges = result.scalars().all()

    merges_data = []
    for merge in merges:
        merges_data.append({
            "id": merge.id,
            "episode_id": merge.episode_id,
            "drama_id": merge.drama_id,
            "title": merge.title,
            "provider": merge.provider,
            "status": merge.status,
            "merged_url": merge.merged_url,
            "duration": merge.duration,
            "task_id": merge.task_id,
            "created_at": merge.created_at.isoformat() if merge.created_at else None,
            "completed_at": merge.completed_at.isoformat() if merge.completed_at else None
        })

    return APIResponse.success_with_pagination(
        items=merges_data,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def merge_videos(
    merge: VideoMergeCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Merge videos using FFmpeg
    Corresponds to Go: MergeVideos in video_merge.go
    """
    try:
        # Verify episode exists
        from app.models.drama import Episode
        episode_result = await db.execute(
            select(Episode).where(Episode.id == merge.episode_id)
        )
        episode = episode_result.scalar_one_or_none()

        if not episode:
            raise NotFoundException("章节不存在")

        # Generate task ID
        task_id = f"video_merge_{uuid.uuid4().hex[:8]}"

        # Generate output path
        output_filename = f"episode_{merge.episode_id}_merged.mp4"
        output_path = f"{settings.LOCAL_STORAGE_PATH}/{output_filename}"

        # Create video merge record
        db_merge = VideoMerge(
            episode_id=merge.episode_id,
            drama_id=merge.drama_id,
            title=merge.title,
            provider=merge.provider,
            model=merge.model,
            scenes=[scene.model_dump() for scene in merge.scenes],
            status=VideoMergeStatus.PROCESSING.value,
            task_id=task_id,
            output_path=output_path
        )

        db.add(db_merge)
        await db.commit()
        await db.refresh(db_merge)

        # Add background task to process video merge
        background_tasks.add_task(
            process_video_merge_task,
            db_merge.id,
            [scene.model_dump() for scene in merge.scenes],
            output_path
        )

        return APIResponse.created({
            "message": "视频合成任务已创建",
            "merge_id": db_merge.id,
            "task_id": task_id,
            "status": "processing",
            "episode_id": merge.episode_id
        })

    except NotFoundException:
        raise
    except Exception as e:
        raise BadRequestException(f"视频合成失败: {str(e)}")


async def process_video_merge_task(merge_id: int, scenes: List[dict], output_path: str):
    """
    Background task to process video merge
    """
    from app.core.database import async_session_maker
    from app.models.video_merge import VideoMerge, VideoMergeStatus

    try:
        # Merge videos using FFmpeg
        result = await ffmpeg_service.merge_videos(
            video_clips=scenes,
            output_path=output_path
        )

        # Update database with result
        async with async_session_maker() as db:
            merge_result = await db.execute(
                select(VideoMerge).where(VideoMerge.id == merge_id)
            )
            db_merge = merge_result.scalar_one_or_none()

            if db_merge:
                if result.get("success"):
                    # Generate URL for merged video
                    from app.utils.file import get_file_url
                    merged_url = get_file_url(
                        output_path.split("/")[-1],
                        settings.BASE_URL
                    )

                    db_merge.status = VideoMergeStatus.COMPLETED.value
                    db_merge.merged_url = merged_url
                    db_merge.duration = result.get("total_duration", 0)
                    db_merge.file_size = result.get("file_size", 0)
                    from sqlalchemy import func
                    db_merge.completed_at = func.now()
                else:
                    db_merge.status = VideoMergeStatus.FAILED.value
                    db_merge.error_msg = "视频合成失败"

                await db.commit()

    except Exception as e:
        # Update with error status
        async with async_session_maker() as db:
            merge_result = await db.execute(
                select(VideoMerge).where(VideoMerge.id == merge_id)
            )
            db_merge = merge_result.scalar_one_or_none()

            if db_merge:
                db_merge.status = VideoMergeStatus.FAILED.value
                db_merge.error_msg = str(e)
                await db.commit()


@router.get("/{merge_id}")
async def get_merge(
    merge_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get video merge by ID
    Corresponds to Go: GetMerge in video_merge.go
    """
    result = await db.execute(select(VideoMerge).where(VideoMerge.id == merge_id))
    merge = result.scalar_one_or_none()

    if not merge:
        raise NotFoundException("视频合成记录不存在")

    return APIResponse.success({
        "id": merge.id,
        "episode_id": merge.episode_id,
        "drama_id": merge.drama_id,
        "title": merge.title,
        "provider": merge.provider,
        "model": merge.model,
        "status": merge.status,
        "scenes": merge.scenes,
        "merged_url": merge.merged_url,
        "output_path": merge.output_path,
        "duration": merge.duration,
        "file_size": merge.file_size,
        "task_id": merge.task_id,
        "error_msg": merge.error_msg,
        "created_at": merge.created_at.isoformat() if merge.created_at else None,
        "completed_at": merge.completed_at.isoformat() if merge.completed_at else None
    })


@router.delete("/{merge_id}")
async def delete_merge(
    merge_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete video merge
    Corresponds to Go: DeleteMerge in video_merge.go
    """
    result = await db.execute(select(VideoMerge).where(VideoMerge.id == merge_id))
    merge = result.scalar_one_or_none()

    if not merge:
        raise NotFoundException("视频合成记录不存在")

    await db.delete(merge)
    await db.commit()

    return APIResponse.success({
        "message": "视频合成记录已删除",
        "merge_id": merge_id
    })
