from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List, Dict, Any
from app.core.database import get_db
from app.core.response import APIResponse
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.drama import Episode, Drama
from app.services.ffmpeg_service import FFmpegService
from app.core.config import settings
import uuid

router = APIRouter()

# Initialize FFmpeg service
ffmpeg_service = FFmpegService(output_dir=settings.LOCAL_STORAGE_PATH)


@router.get("/{episode_id}")
async def get_episode(
    episode_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get episode by ID"""
    try:
        episode_id_int = int(episode_id)
        result = await db.execute(select(Episode).where(Episode.id == episode_id_int))
    except ValueError:
        result = await db.execute(select(Episode).where(Episode.id == episode_id))

    episode = result.scalar_one_or_none()

    if not episode:
        raise NotFoundException("章节不存在")

    return APIResponse.success({
        "id": episode.id,
        "drama_id": episode.drama_id,
        "episode_number": episode.episode_number,
        "title": episode.title,
        "description": episode.description,
        "script_content": episode.script_content,
        "duration": episode.duration,
        "status": episode.status,
        "video_url": episode.video_url,
        "created_at": episode.created_at.isoformat() if episode.created_at else None,
        "updated_at": episode.updated_at.isoformat() if episode.updated_at else None
    })


@router.put("/{episode_id}")
async def update_episode(
    episode_id: str,
    episode_data: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Update episode"""
    try:
        episode_id_int = int(episode_id)
        result = await db.execute(select(Episode).where(Episode.id == episode_id_int))
    except ValueError:
        result = await db.execute(select(Episode).where(Episode.id == episode_id))

    db_episode = result.scalar_one_or_none()

    if not db_episode:
        raise NotFoundException("章节不存在")

    # Update fields if provided
    if "title" in episode_data:
        db_episode.title = episode_data["title"]
    if "description" in episode_data:
        db_episode.description = episode_data["description"]
    if "script_content" in episode_data:
        db_episode.script_content = episode_data["script_content"]
    if "duration" in episode_data:
        db_episode.duration = episode_data["duration"]
    if "status" in episode_data:
        db_episode.status = episode_data["status"]
    if "video_url" in episode_data:
        db_episode.video_url = episode_data["video_url"]

    await db.commit()
    await db.refresh(db_episode)

    return APIResponse.success({
        "id": db_episode.id,
        "drama_id": db_episode.drama_id,
        "episode_number": db_episode.episode_number,
        "title": db_episode.title,
        "status": db_episode.status,
        "updated_at": db_episode.updated_at.isoformat() if db_episode.updated_at else None
    })


@router.delete("/{episode_id}")
async def delete_episode(
    episode_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete episode"""
    try:
        episode_id_int = int(episode_id)
        result = await db.execute(select(Episode).where(Episode.id == episode_id_int))
    except ValueError:
        result = await db.execute(select(Episode).where(Episode.id == episode_id))

    episode = result.scalar_one_or_none()

    if not episode:
        raise NotFoundException("章节不存在")

    await db.delete(episode)
    await db.commit()

    return APIResponse.success({"message": "章节已删除"})


@router.post("/{episode_id}/finalize", status_code=status.HTTP_202_ACCEPTED)
async def finalize_episode(
    episode_id: str,
    background_tasks: BackgroundTasks,
    timeline_data: Optional[Dict[str, Any]] = Body(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Finalize episode - mark as completed and prepare for export
    This corresponds to Go: FinalizeEpisode in drama.go

    This endpoint triggers video generation/merging for the episode.
    If timeline_data is provided (with clips), it will merge videos according to the timeline.
    Otherwise, it uses default scene ordering.
    """
    try:
        episode_id_int = int(episode_id)
        result = await db.execute(select(Episode).where(Episode.id == episode_id_int))
    except ValueError:
        result = await db.execute(select(Episode).where(Episode.id == episode_id))

    episode = result.scalar_one_or_none()

    if not episode:
        raise NotFoundException("章节不存在")

    # Create a task for finalization
    task_id = f"finalize_{episode_id_int}_{uuid.uuid4().hex[:8]}"

    # Update episode status to processing
    episode.status = "processing"
    await db.commit()

    # Add background task to process finalization
    background_tasks.add_task(
        process_episode_finalization,
        episode_id_int,
        timeline_data,
        task_id
    )

    return APIResponse.success({
        "message": "章节完成制作，视频合成任务已创建",
        "episode_id": episode_id_int,
        "task_id": task_id,
        "status": "processing"
    })


async def process_episode_finalization(
    episode_id: int,
    timeline_data: Optional[Dict[str, Any]],
    task_id: str
):
    """
    Background task to process episode finalization
    This handles video merging for the episode
    """
    from app.core.database import async_session_maker
    from app.models.video_generation import VideoGeneration
    from app.models.drama import Storyboard, Scene

    async with async_session_maker() as db:
        try:
            # Get episode with drama
            episode_result = await db.execute(
                select(Episode).where(Episode.id == episode_id)
            )
            episode = episode_result.scalar_one_or_none()

            if not episode:
                return

            # Get all storyboards for this episode
            storyboard_result = await db.execute(
                select(Storyboard)
                .where(Storyboard.episode_id == episode_id)
                .order_by(Storyboard.storyboard_number)
            )
            storyboards = storyboard_result.scalars().all()

            if not storyboards:
                # No storyboards, just mark as completed
                episode.status = "completed"
                await db.commit()
                return

            # Collect video clips from timeline or use default ordering
            clips = []

            if timeline_data and "clips" in timeline_data:
                # Use provided timeline data
                for clip_data in timeline_data["clips"]:
                    clips.append({
                        "scene_id": clip_data.get("scene_id"),
                        "video_url": clip_data.get("video_url"),
                        "start_time": clip_data.get("start_time", 0),
                        "end_time": clip_data.get("end_time", 5),
                        "duration": clip_data.get("duration", 5),
                        "order": clip_data.get("order", 0)
                    })
            else:
                # Use default storyboard ordering
                for idx, storyboard in enumerate(storyboards):
                    # Try to get video generation for this storyboard
                    video_gen_result = await db.execute(
                        select(VideoGeneration)
                        .where(
                            VideoGeneration.storyboard_id == storyboard.id,
                            VideoGeneration.status == "completed"
                        )
                        .order_by(VideoGeneration.created_at.desc())
                        .limit(1)
                    )
                    video_gen = video_gen_result.scalar_one_or_none()

                    if video_gen and video_gen.video_url:
                        clips.append({
                            "scene_id": storyboard.scene_id if hasattr(storyboard, 'scene_id') else storyboard.id,
                            "video_url": video_gen.video_url,
                            "start_time": 0,
                            "end_time": video_gen.duration or 5,
                            "duration": video_gen.duration or 5,
                            "order": idx
                        })

            if not clips:
                # No video clips available, just mark as completed
                episode.status = "completed"
                await db.commit()
                return

            # Merge videos using FFmpeg
            output_filename = f"episode_{episode_id}_finalized.mp4"
            output_path = f"{settings.LOCAL_STORAGE_PATH}/{output_filename}"

            merge_result = await ffmpeg_service.merge_videos(
                video_clips=clips,
                output_path=output_path
            )

            if merge_result.get("success"):
                # Generate URL for merged video
                from app.utils.file import get_file_url
                video_url = get_file_url(output_filename, settings.BASE_URL)

                # Update episode with finalized video
                episode.video_url = video_url
                episode.duration = merge_result.get("total_duration", 0)
                episode.status = "completed"
                await db.commit()
            else:
                # Mark as failed
                episode.status = "failed"
                await db.commit()

        except Exception as e:
            # Mark episode as failed
            episode_result = await db.execute(
                select(Episode).where(Episode.id == episode_id)
            )
            episode = episode_result.scalar_one_or_none()
            if episode:
                episode.status = "failed"
                await db.commit()


@router.get("/{episode_id}/download")
async def download_episode(
    episode_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get download information for episode
    Corresponds to Go: DownloadEpisodeVideo in drama.go
    """
    try:
        episode_id_int = int(episode_id)
        result = await db.execute(
            select(Episode)
            .options(select(Drama))
            .where(Episode.id == episode_id_int)
        )
    except ValueError:
        result = await db.execute(
            select(Episode)
            .options(select(Drama))
            .where(Episode.id == episode_id)
        )

    episode = result.scalar_one_or_none()

    if not episode:
        raise NotFoundException("剧集不存在")

    # Check if episode has video
    if not episode.video_url:
        raise BadRequestException("该剧集还没有生成视频")

    # Return video URL and metadata (similar to Go version)
    return APIResponse.success({
        "video_url": episode.video_url,
        "title": episode.title,
        "episode_number": episode.episode_number,
        "duration": episode.duration,
        "status": episode.status
    })
