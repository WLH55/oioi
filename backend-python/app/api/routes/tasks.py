from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.core.database import get_db
from app.models.task import AsyncTask
from app.schemas.task import TaskResponse

router = APIRouter()


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get task status by ID"""
    result = await db.execute(select(AsyncTask).where(AsyncTask.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    resource_id: Optional[str] = None,
    task_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List tasks with optional filters"""
    query = select(AsyncTask)

    if resource_id:
        query = query.where(AsyncTask.resource_id == resource_id)
    if task_type:
        query = query.where(AsyncTask.type == task_type)

    query = query.offset(skip).limit(limit).order_by(AsyncTask.created_at.desc())

    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks
