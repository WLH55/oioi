from fastapi import APIRouter, Depends, status, BackgroundTasks, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
from app.core.database import get_db
from app.core.response import APIResponse
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.video_generation import VideoGeneration
from app.models.image_generation import ImageGeneration
from app.models.drama import Episode, Storyboard
from app.schemas.video_generation import VideoGenerationCreate, VideoGenerationResponse
from app.middlewares.rate_limit import limiter

router = APIRouter()


@router.get("")
async def list_video_generations(
    page: int = 1,
    page_size: int = 20,
    drama_id: Optional[int] = None,
    storyboard_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all video generations
    Corresponds to Go: ListVideoGenerations
    """
    query = select(VideoGeneration)

    if drama_id:
        query = query.where(VideoGeneration.drama_id == drama_id)
    if storyboard_id:
        query = query.where(VideoGeneration.storyboard_id == storyboard_id)
    if status_filter:
        query = query.where(VideoGeneration.status == status_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    skip = (page - 1) * page_size
    query = query.offset(skip).limit(page_size).order_by(VideoGeneration.created_at.desc())
    result = await db.execute(query)
    generations = result.scalars().all()

    generations_data = []
    for gen in generations:
        generations_data.append({
            "id": gen.id,
            "storyboard_id": gen.storyboard_id,
            "drama_id": gen.drama_id,
            "image_gen_id": gen.image_gen_id,
            "provider": gen.provider,
            "prompt": gen.prompt,
            "model": gen.model,
            "reference_mode": gen.reference_mode,
            "image_url": gen.image_url,
            "first_frame_url": gen.first_frame_url,
            "last_frame_url": gen.last_frame_url,
            "duration": gen.duration,
            "fps": gen.fps,
            "resolution": gen.resolution,
            "aspect_ratio": gen.aspect_ratio,
            "style": gen.style,
            "video_url": gen.video_url,
            "status": gen.status,
            "error_msg": gen.error_msg,
            "created_at": gen.created_at.isoformat() if gen.created_at else None,
            "completed_at": gen.completed_at.isoformat() if gen.completed_at else None
        })

    return APIResponse.success_with_pagination(
        items=generations_data,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")  # Limit to 10 video generations per minute
async def generate_video(
    request: VideoGenerationCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate video using AI service
    Corresponds to Go: GenerateVideo
    """
    # Convert drama_id from string to int
    drama_id = int(request.drama_id)

    # Create video generation record
    db_gen = VideoGeneration(
        drama_id=drama_id,
        storyboard_id=request.storyboard_id,
        image_gen_id=request.image_gen_id,
        provider=request.provider,
        prompt=request.prompt,
        model=request.model,
        reference_mode=request.reference_mode,
        image_url=request.image_url,
        first_frame_url=request.first_frame_url,
        last_frame_url=request.last_frame_url,
        reference_image_urls=str(request.reference_image_urls) if request.reference_image_urls else None,
        duration=request.duration,
        fps=request.fps,
        aspect_ratio=request.aspect_ratio,
        style=request.style,
        motion_level=request.motion_level,
        camera_motion=request.camera_motion,
        seed=request.seed,
        status="pending"
    )

    db.add(db_gen)
    await db.commit()
    await db.refresh(db_gen)

    return APIResponse.created({
        "id": db_gen.id,
        "drama_id": db_gen.drama_id,
        "status": db_gen.status,
        "message": "视频生成任务已创建"
    })


@router.get("/{gen_id}")
async def get_video_generation(
    gen_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get video generation by ID"""
    result = await db.execute(select(VideoGeneration).where(VideoGeneration.id == gen_id))
    gen = result.scalar_one_or_none()

    if not gen:
        raise NotFoundException("视频生成记录不存在")

    return APIResponse.success({
        "id": gen.id,
        "storyboard_id": gen.storyboard_id,
        "drama_id": gen.drama_id,
        "image_gen_id": gen.image_gen_id,
        "provider": gen.provider,
        "prompt": gen.prompt,
        "model": gen.model,
        "reference_mode": gen.reference_mode,
        "image_url": gen.image_url,
        "first_frame_url": gen.first_frame_url,
        "last_frame_url": gen.last_frame_url,
        "reference_image_urls": gen.reference_image_urls,
        "duration": gen.duration,
        "fps": gen.fps,
        "resolution": gen.resolution,
        "aspect_ratio": gen.aspect_ratio,
        "style": gen.style,
        "motion_level": gen.motion_level,
        "camera_motion": gen.camera_motion,
        "seed": gen.seed,
        "video_url": gen.video_url,
        "minio_url": gen.minio_url,
        "local_path": gen.local_path,
        "status": gen.status,
        "task_id": gen.task_id,
        "error_msg": gen.error_msg,
        "completed_at": gen.completed_at.isoformat() if gen.completed_at else None,
        "created_at": gen.created_at.isoformat() if gen.created_at else None,
        "updated_at": gen.updated_at.isoformat() if gen.updated_at else None,
        "width": gen.width,
        "height": gen.height
    })


@router.delete("/{gen_id}")
async def delete_video_generation(
    gen_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete video generation"""
    result = await db.execute(select(VideoGeneration).where(VideoGeneration.id == gen_id))
    gen = result.scalar_one_or_none()

    if not gen:
        raise NotFoundException("视频生成记录不存在")

    await db.delete(gen)
    await db.commit()

    return APIResponse.success({
        "message": "视频生成记录已删除",
        "gen_id": gen_id
    })


@router.post("/image/{image_gen_id}", status_code=status.HTTP_201_CREATED)
async def generate_video_from_image(
    image_gen_id: int,
    background_tasks: BackgroundTasks,
    prompt: Optional[str] = Body(None, embed=True),
    provider: str = Body("doubao", embed=True),
    duration: float = Body(5.0, embed=True),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate video from an existing image generation
    Corresponds to Go: GenerateVideoFromImage
    """
    # Get image generation
    result = await db.execute(select(ImageGeneration).where(ImageGeneration.id == image_gen_id))
    image_gen = result.scalar_one_or_none()

    if not image_gen:
        raise NotFoundException("图片生成记录不存在")

    # Create video generation record from image
    db_gen = VideoGeneration(
        drama_id=image_gen.drama_id,
        storyboard_id=image_gen.storyboard_id,
        image_gen_id=image_gen.id,
        provider=provider,
        prompt=prompt or f"Video based on image: {image_gen.prompt}",
        model="default",
        reference_mode="image",
        image_url=image_gen.image_url,
        first_frame_url=image_gen.image_url,
        duration=int(duration),
        fps=24,
        aspect_ratio="16:9",
        status="pending"
    )

    db.add(db_gen)
    await db.commit()
    await db.refresh(db_gen)

    return APIResponse.created({
        "id": db_gen.id,
        "drama_id": db_gen.drama_id,
        "status": db_gen.status,
        "message": "视频生成任务已创建",
        "image_gen_id": image_gen_id
    })


@router.post("/episode/{episode_id}/batch")
async def batch_generate_for_episode(
    episode_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Batch generate videos for all storyboards in an episode
    Corresponds to Go: BatchGenerateForEpisode
    """
    # Get episode
    episode_result = await db.execute(select(Episode).where(Episode.id == episode_id))
    episode = episode_result.scalar_one_or_none()

    if not episode:
        raise NotFoundException("章节不存在")

    # Get all storyboards for this episode
    storyboards_result = await db.execute(
        select(Storyboard).where(Storyboard.episode_id == episode_id)
    )
    storyboards = storyboards_result.scalars().all()

    # Get image generations for these storyboards
    storyboard_ids = [s.id for s in storyboards]
    image_gens_result = await db.execute(
        select(ImageGeneration).where(
            ImageGeneration.storyboard_id.in_(storyboard_ids),
            ImageGeneration.status == "completed"
        )
    )
    image_gens = image_gens_result.scalars().all()

    # Create async task
    from app.models.task import AsyncTask
    import uuid
    task_id = str(uuid.uuid4())

    db_task = AsyncTask(
        id=task_id,
        type="batch_video_generation",
        status="pending",
        resource_id=str(episode_id),
        message=f"开始批量生成 {len(image_gens)} 个视频..."
    )
    db.add(db_task)
    await db.commit()

    # Add background task
    background_tasks.add_task(
        process_batch_video_generation,
        task_id,
        episode_id
    )

    return APIResponse.created({
        "message": f"批量视频生成任务已创建，共 {len(image_gens)} 个图片",
        "task_id": task_id,
        "status": "pending",
        "episode_id": episode_id,
        "total_storyboards": len(storyboards),
        "total_images": len(image_gens)
    })


async def process_batch_video_generation(task_id: str, episode_id: int):
    """Background task to process batch video generation"""
    from app.core.database import async_session_maker
    from app.models.task import AsyncTask

    async with async_session_maker() as db:
        try:
            # Update task status
            result = await db.execute(select(AsyncTask).where(AsyncTask.id == task_id))
            task = result.scalar_one_or_none()
            if task:
                task.status = "processing"
                task.progress = 10
                await db.commit()

            # Get episode
            episode_result = await db.execute(
                select(Episode).where(Episode.id == episode_id)
            )
            episode = episode_result.scalar_one_or_none()
            if not episode:
                raise Exception("Episode not found")

            # Get all storyboards for this episode
            storyboards_result = await db.execute(
                select(Storyboard).where(Storyboard.episode_id == episode_id)
            )
            storyboards = storyboards_result.scalars().all()

            # Get image generations for these storyboards
            storyboard_ids = [s.id for s in storyboards]
            image_gens_result = await db.execute(
                select(ImageGeneration).where(
                    ImageGeneration.storyboard_id.in_(storyboard_ids),
                    ImageGeneration.status == "completed"
                )
            )
            image_gens = image_gens_result.scalars().all()

            # Create video generation tasks
            created_count = 0
            for image_gen in image_gens:
                # Check if video generation already exists
                existing_result = await db.execute(
                    select(VideoGeneration).where(
                        VideoGeneration.image_gen_id == image_gen.id
                    )
                )
                existing = existing_result.scalar_one_or_none()

                if not existing:
                    db_gen = VideoGeneration(
                        drama_id=episode.drama_id,
                        storyboard_id=image_gen.storyboard_id,
                        image_gen_id=image_gen.id,
                        provider="doubao",
                        prompt=f"Video for storyboard {image_gen.storyboard_id}",
                        model="default",
                        reference_mode="image",
                        image_url=image_gen.image_url,
                        first_frame_url=image_gen.image_url,
                        duration=5,
                        fps=24,
                        aspect_ratio="16:9",
                        status="pending"
                    )
                    db.add(db_gen)
                    created_count += 1

            await db.commit()

            # Update task as completed
            if task:
                task.status = "completed"
                task.progress = 100
                task.message = f"成功创建 {created_count} 个视频生成任务"
                task.result = f'{{"total_storyboards": {len(storyboards)}, "total_images": {len(image_gens)}, "new_generations": {created_count}}}'
                await db.commit()

        except Exception as e:
            # Update task as failed
            result = await db.execute(select(AsyncTask).where(AsyncTask.id == task_id))
            task = result.scalar_one_or_none()
            if task:
                task.status = "failed"
                task.error = str(e)
                await db.commit()
