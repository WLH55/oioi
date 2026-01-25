from fastapi import APIRouter, Depends, status, BackgroundTasks, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
from app.core.database import get_db
from app.core.response import APIResponse
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.image_generation import ImageGeneration
from app.models.drama import Scene, Episode, Storyboard
from app.services.image_service import ImageGenerationService
from app.schemas.image_generation import ImageGenerationCreate, ImageGenerationResponse
from app.middlewares.rate_limit import limiter

router = APIRouter()


@router.get("")
async def list_image_generations(
    page: int = 1,
    page_size: int = 20,
    drama_id: Optional[int] = None,
    scene_id: Optional[int] = None,
    storyboard_id: Optional[int] = None,
    frame_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all image generations
    Corresponds to Go: ListImageGenerations
    """
    query = select(ImageGeneration)

    if drama_id:
        query = query.where(ImageGeneration.drama_id == drama_id)
    if scene_id:
        query = query.where(ImageGeneration.scene_id == scene_id)
    if storyboard_id:
        query = query.where(ImageGeneration.storyboard_id == storyboard_id)
    if frame_type:
        query = query.where(ImageGeneration.frame_type == frame_type)
    if status_filter:
        query = query.where(ImageGeneration.status == status_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    skip = (page - 1) * page_size
    query = query.offset(skip).limit(page_size).order_by(ImageGeneration.created_at.desc())
    result = await db.execute(query)
    generations = result.scalars().all()

    generations_data = []
    for gen in generations:
        generations_data.append({
            "id": gen.id,
            "storyboard_id": gen.storyboard_id,
            "drama_id": gen.drama_id,
            "scene_id": gen.scene_id,
            "character_id": gen.character_id,
            "image_type": gen.image_type,
            "frame_type": gen.frame_type,
            "provider": gen.provider,
            "prompt": gen.prompt,
            "negative_prompt": gen.negative_prompt,
            "model": gen.model,
            "size": gen.size,
            "quality": gen.quality,
            "style": gen.style,
            "steps": gen.steps,
            "cfg_scale": gen.cfg_scale,
            "seed": gen.seed,
            "image_url": gen.image_url,
            "local_path": gen.local_path,
            "status": gen.status,
            "error_msg": gen.error_msg,
            "width": gen.width,
            "height": gen.height,
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
@limiter.limit("20/minute")  # Limit to 20 image generations per minute
async def generate_image(
    request: ImageGenerationCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate image using AI service
    Corresponds to Go: GenerateImage
    """
    # Convert drama_id from string to int
    drama_id = int(request.drama_id)

    # Create image generation record
    db_gen = ImageGeneration(
        drama_id=drama_id,
        storyboard_id=request.storyboard_id,
        scene_id=request.scene_id,
        character_id=request.character_id,
        image_type=request.image_type or "storyboard",
        frame_type=request.frame_type,
        provider=request.provider,
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        model=request.model,
        size=request.size,
        quality=request.quality,
        style=request.style,
        steps=request.steps,
        cfg_scale=request.cfg_scale,
        seed=request.seed,
        width=request.width,
        height=request.height,
        reference_images=request.reference_images,
        status="pending"
    )

    db.add(db_gen)
    await db.commit()
    await db.refresh(db_gen)

    return APIResponse.created({
        "id": db_gen.id,
        "drama_id": db_gen.drama_id,
        "status": db_gen.status,
        "message": "图片生成任务已创建"
    })


@router.get("/{gen_id}")
async def get_image_generation(
    gen_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get image generation by ID"""
    result = await db.execute(select(ImageGeneration).where(ImageGeneration.id == gen_id))
    gen = result.scalar_one_or_none()

    if not gen:
        raise NotFoundException("图片生成记录不存在")

    return APIResponse.success({
        "id": gen.id,
        "storyboard_id": gen.storyboard_id,
        "drama_id": gen.drama_id,
        "scene_id": gen.scene_id,
        "character_id": gen.character_id,
        "image_type": gen.image_type,
        "frame_type": gen.frame_type,
        "provider": gen.provider,
        "prompt": gen.prompt,
        "negative_prompt": gen.negative_prompt,
        "model": gen.model,
        "size": gen.size,
        "quality": gen.quality,
        "style": gen.style,
        "steps": gen.steps,
        "cfg_scale": gen.cfg_scale,
        "seed": gen.seed,
        "image_url": gen.image_url,
        "local_path": gen.local_path,
        "status": gen.status,
        "error_msg": gen.error_msg,
        "width": gen.width,
        "height": gen.height,
        "created_at": gen.created_at.isoformat() if gen.created_at else None,
        "updated_at": gen.updated_at.isoformat() if gen.updated_at else None,
        "completed_at": gen.completed_at.isoformat() if gen.completed_at else None
    })


@router.delete("/{gen_id}")
async def delete_image_generation(
    gen_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete image generation"""
    result = await db.execute(select(ImageGeneration).where(ImageGeneration.id == gen_id))
    gen = result.scalar_one_or_none()

    if not gen:
        raise NotFoundException("图片生成记录不存在")

    await db.delete(gen)
    await db.commit()

    return APIResponse.success({
        "message": "图片生成记录已删除",
        "gen_id": gen_id
    })


@router.post("/scene/{scene_id}")
async def generate_images_for_scene(
    scene_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate image for a specific scene
    Corresponds to Go: GenerateImagesForScene
    """
    # Get scene
    result = await db.execute(select(Scene).where(Scene.id == scene_id))
    scene = result.scalar_one_or_none()

    if not scene:
        raise NotFoundException("场景不存在")

    # Create image generation record
    db_gen = ImageGeneration(
        drama_id=scene.drama_id,
        scene_id=scene.id,
        image_type="scene",
        provider="openai",  # Default provider
        prompt=scene.prompt,
        model="dall-e-3",
        size="1024x1024",
        quality="standard",
        status="pending"
    )

    db.add(db_gen)
    await db.commit()
    await db.refresh(db_gen)

    # Update scene status
    scene.status = "pending"
    await db.commit()

    return APIResponse.created({
        "message": "场景图片生成任务已创建",
        "scene_id": scene_id,
        "image_gen_id": db_gen.id,
        "status": "pending"
    })


@router.get("/episode/{episode_id}/backgrounds")
async def get_backgrounds_for_episode(
    episode_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get background images for an episode
    Corresponds to Go: GetBackgroundsForEpisode
    """
    # Get episode
    episode_result = await db.execute(select(Episode).where(Episode.id == episode_id))
    episode = episode_result.scalar_one_or_none()

    if not episode:
        raise NotFoundException("章节不存在")

    # Get scenes for episode with generated images
    result = await db.execute(
        select(ImageGeneration)
        .where(
            ImageGeneration.drama_id == episode.drama_id,
            ImageGeneration.image_type == "scene",
            ImageGeneration.status == "completed"
        )
        .order_by(ImageGeneration.created_at.desc())
    )

    image_gens = result.scalars().all()

    backgrounds = []
    for gen in image_gens:
        if gen.scene_id:
            scene_result = await db.execute(select(Scene).where(Scene.id == gen.scene_id))
            scene = scene_result.scalar_one_or_none()
            if scene and scene.episode_id == episode_id:
                backgrounds.append({
                    "scene_id": scene.id,
                    "location": scene.location,
                    "time": scene.time,
                    "image_url": gen.image_url,
                    "local_path": gen.local_path,
                    "image_gen_id": gen.id
                })

    return APIResponse.success({
        "episode_id": episode_id,
        "backgrounds": backgrounds,
        "count": len(backgrounds)
    })


@router.post("/episode/{episode_id}/backgrounds/extract")
async def extract_backgrounds_for_episode(
    episode_id: int,
    background_tasks: BackgroundTasks,
    model: Optional[str] = Body(None, embed=True),
    db: AsyncSession = Depends(get_db)
):
    """
    Extract background images from storyboards for an episode
    Corresponds to Go: ExtractBackgroundsForEpisode
    """
    # Get episode
    episode_result = await db.execute(select(Episode).where(Episode.id == episode_id))
    episode = episode_result.scalar_one_or_none()

    if not episode:
        raise NotFoundException("章节不存在")

    # Get all scenes for this episode
    scenes_result = await db.execute(
        select(Scene).where(Scene.episode_id == episode_id)
    )
    scenes = scenes_result.scalars().all()

    # Create async task
    from app.models.task import AsyncTask
    import uuid
    task_id = str(uuid.uuid4())

    db_task = AsyncTask(
        id=task_id,
        type="background_extraction",
        status="pending",
        resource_id=str(episode_id),
        message="开始提取场景..."
    )
    db.add(db_task)
    await db.commit()

    # Add background task to process extraction
    background_tasks.add_task(
        process_background_extraction,
        task_id,
        episode_id,
        model or ""
    )

    return APIResponse.created({
        "message": "场景提取任务已创建，正在后台处理",
        "task_id": task_id,
        "status": "pending",
        "episode_id": episode_id
    })


async def process_background_extraction(task_id: str, episode_id: int, model: str):
    """Background task to process background extraction"""
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

            # Get all scenes for episode
            scenes_result = await db.execute(
                select(Scene).where(Scene.episode_id == episode_id)
            )
            scenes = scenes_result.scalars().all()

            # Create image generation tasks for each scene
            created_count = 0
            for scene in scenes:
                # Check if image generation already exists
                existing_result = await db.execute(
                    select(ImageGeneration).where(
                        ImageGeneration.scene_id == scene.id,
                        ImageGeneration.image_type == "scene"
                    )
                )
                existing = existing_result.scalar_one_or_none()

                if not existing:
                    db_gen = ImageGeneration(
                        drama_id=scene.drama_id,
                        scene_id=scene.id,
                        image_type="scene",
                        provider="openai",
                        prompt=scene.prompt,
                        model=model or "dall-e-3",
                        size="1024x1024",
                        quality="standard",
                        status="pending"
                    )
                    db.add(db_gen)
                    created_count += 1

            await db.commit()

            # Update task as completed
            if task:
                task.status = "completed"
                task.progress = 100
                task.message = f"成功提取 {created_count} 个场景"
                task.result = f'{{"total_scenes": {len(scenes)}, "new_generations": {created_count}}}'
                await db.commit()

        except Exception as e:
            # Update task as failed
            result = await db.execute(select(AsyncTask).where(AsyncTask.id == task_id))
            task = result.scalar_one_or_none()
            if task:
                task.status = "failed"
                task.error = str(e)
                await db.commit()


@router.post("/episode/{episode_id}/batch")
async def batch_generate_for_episode(
    episode_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Batch generate images for an episode (all scenes and storyboards)
    Corresponds to Go: BatchGenerateForEpisode
    """
    # Get episode
    episode_result = await db.execute(select(Episode).where(Episode.id == episode_id))
    episode = episode_result.scalar_one_or_none()

    if not episode:
        raise NotFoundException("章节不存在")

    # Get all storyboards for episode
    storyboards_result = await db.execute(
        select(Storyboard).where(Storyboard.episode_id == episode_id)
    )
    storyboards = storyboards_result.scalars().all()

    # Create async task
    from app.models.task import AsyncTask
    import uuid
    task_id = str(uuid.uuid4())

    db_task = AsyncTask(
        id=task_id,
        type="batch_image_generation",
        status="pending",
        resource_id=str(episode_id),
        message=f"开始批量生成 {len(storyboards)} 个分镜图片..."
    )
    db.add(db_task)
    await db.commit()

    # Add background task
    background_tasks.add_task(
        process_batch_image_generation,
        task_id,
        episode_id
    )

    return APIResponse.created({
        "message": f"批量图片生成任务已创建，共 {len(storyboards)} 个分镜",
        "task_id": task_id,
        "status": "pending",
        "episode_id": episode_id
    })


async def process_batch_image_generation(task_id: str, episode_id: int):
    """Background task to process batch image generation"""
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

            # Get all storyboards for episode
            storyboards_result = await db.execute(
                select(Storyboard).where(Storyboard.episode_id == episode_id)
            )
            storyboards = storyboards_result.scalars().all()

            # Create image generation tasks for each storyboard
            created_count = 0
            for storyboard in storyboards:
                existing_result = await db.execute(
                    select(ImageGeneration).where(
                        ImageGeneration.storyboard_id == storyboard.id,
                        ImageGeneration.image_type == "storyboard"
                    )
                )
                existing = existing_result.scalar_one_or_none()

                if not existing and storyboard.image_prompt:
                    db_gen = ImageGeneration(
                        drama_id=storyboard.drama_id,
                        storyboard_id=storyboard.id,
                        image_type="storyboard",
                        provider="openai",
                        prompt=storyboard.image_prompt,
                        model="dall-e-3",
                        size="1024x1792",  # 16:9 aspect ratio
                        quality="standard",
                        status="pending"
                    )
                    db.add(db_gen)
                    created_count += 1

            await db.commit()

            # Update task as completed
            if task:
                task.status = "completed"
                task.progress = 100
                task.message = f"成功创建 {created_count} 个图片生成任务"
                task.result = f'{{"total_storyboards": {len(storyboards)}, "new_generations": {created_count}}}'
                await db.commit()

        except Exception as e:
            # Update task as failed
            result = await db.execute(select(AsyncTask).where(AsyncTask.id == task_id))
            task = result.scalar_one_or_none()
            if task:
                task.status = "failed"
                task.error = str(e)
                await db.commit()
