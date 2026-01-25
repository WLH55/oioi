from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.drama import Storyboard, Episode
from app.schemas.drama import StoryboardUpdate
from app.models.frame_prompt import FramePrompt
from typing import List

router = APIRouter()


@router.put("/{storyboard_id}")
async def update_storyboard(
    storyboard_id: int,
    storyboard: StoryboardUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update storyboard information"""
    result = await db.execute(select(Storyboard).where(Storyboard.id == storyboard_id))
    db_storyboard = result.scalar_one_or_none()

    if not db_storyboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storyboard not found"
        )

    update_data = storyboard.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_storyboard, field, value)

    await db.commit()
    await db.refresh(db_storyboard)

    return {
        "message": "Storyboard updated successfully",
        "storyboard_id": storyboard_id,
        "storyboard": db_storyboard
    }


@router.post("/{storyboard_id}/frame-prompt")
async def generate_frame_prompt(
    storyboard_id: int,
    frame_type: str = "key",
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db)
):
    """Generate frame prompt for storyboard"""
    result = await db.execute(select(Storyboard).where(Storyboard.id == storyboard_id))
    storyboard = result.scalar_one_or_none()

    if not storyboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storyboard not found"
        )

    # In real implementation, this would use AI to generate frame prompts
    frame_prompt = FramePrompt(
        storyboard_id=storyboard_id,
        frame_type=frame_type,
        prompt=storyboard.image_prompt or "",
        description=f"Generated {frame_type} frame prompt"
    )

    db.add(frame_prompt)
    await db.commit()
    await db.refresh(frame_prompt)

    return {
        "message": "Frame prompt generated successfully",
        "storyboard_id": storyboard_id,
        "frame_prompt_id": frame_prompt.id,
        "frame_type": frame_type
    }


@router.get("/{storyboard_id}/frame-prompts")
async def get_storyboard_frame_prompts(
    storyboard_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all frame prompts for a storyboard"""
    # Verify storyboard exists
    result = await db.execute(select(Storyboard).where(Storyboard.id == storyboard_id))
    storyboard = result.scalar_one_or_none()

    if not storyboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storyboard not found"
        )

    # Get frame prompts
    result = await db.execute(
        select(FramePrompt).where(FramePrompt.storyboard_id == storyboard_id)
    )
    frame_prompts = result.scalars().all()

    return {
        "storyboard_id": storyboard_id,
        "frame_prompts": frame_prompts,
        "count": len(frame_prompts)
    }


@router.post("/episodes/{episode_id}")
async def generate_storyboard(
    episode_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Generate storyboard for episode"""
    result = await db.execute(select(Episode).where(Episode.id == episode_id))
    episode = result.scalar_one_or_none()

    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )

    # In real implementation, this would use AI to generate storyboards
    task_id = f"storyboard_gen_{episode_id}"

    return {
        "message": "Storyboard generation started",
        "episode_id": episode_id,
        "task_id": task_id,
        "status": "pending"
    }


@router.get("/episodes/{episode_id}")
async def get_episode_storyboards(
    episode_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all storyboards for an episode"""
    # Verify episode exists
    result = await db.execute(select(Episode).where(Episode.id == episode_id))
    episode = result.scalar_one_or_none()

    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )

    # Get storyboards
    result = await db.execute(
        select(Storyboard)
        .where(Storyboard.episode_id == episode_id)
        .order_by(Storyboard.storyboard_number)
    )
    storyboards = result.scalars().all()

    return {
        "episode_id": episode_id,
        "storyboards": storyboards,
        "count": len(storyboards)
    }
