from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.models.drama import Scene
from app.schemas.drama import SceneUpdate

router = APIRouter()


@router.put("/{scene_id}")
async def update_scene(
    scene_id: int,
    scene: SceneUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update scene information"""
    result = await db.execute(select(Scene).where(Scene.id == scene_id))
    db_scene = result.scalar_one_or_none()

    if not db_scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )

    update_data = scene.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_scene, field, value)

    await db.commit()
    await db.refresh(db_scene)

    return {
        "message": "Scene updated successfully",
        "scene_id": scene_id,
        "scene": db_scene
    }


@router.put("/{scene_id}/prompt")
async def update_scene_prompt(
    scene_id: int,
    prompt: str,
    db: AsyncSession = Depends(get_db)
):
    """Update scene prompt"""
    result = await db.execute(select(Scene).where(Scene.id == scene_id))
    db_scene = result.scalar_one_or_none()

    if not db_scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )

    db_scene.prompt = prompt
    await db.commit()
    await db.refresh(db_scene)

    return {
        "message": "Scene prompt updated successfully",
        "scene_id": scene_id,
        "prompt": prompt
    }


@router.delete("/{scene_id}")
async def delete_scene(
    scene_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete scene"""
    result = await db.execute(select(Scene).where(Scene.id == scene_id))
    scene = result.scalar_one_or_none()

    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )

    await db.delete(scene)
    await db.commit()

    return {
        "message": "Scene deleted successfully",
        "scene_id": scene_id
    }


@router.post("/generate-image")
async def generate_scene_image(
    scene_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Generate image for scene"""
    result = await db.execute(select(Scene).where(Scene.id == scene_id))
    scene = result.scalar_one_or_none()

    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )

    # Update status to pending
    scene.status = "pending"
    await db.commit()

    # In real implementation, this would trigger AI image generation
    task_id = f"scene_img_gen_{scene_id}"

    return {
        "message": "Scene image generation started",
        "scene_id": scene_id,
        "task_id": task_id,
        "status": "pending"
    }
