from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.models.ai_config import AIServiceConfig
from app.schemas.ai_config import (
    AIServiceConfigCreate, AIServiceConfigUpdate, AIServiceConfigResponse,
    TestConnectionRequest,
)

router = APIRouter()


@router.get("", response_model=List[AIServiceConfigResponse])
async def list_ai_configs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all AI service configurations"""
    result = await db.execute(
        select(AIServiceConfig)
        .order_by(AIServiceConfig.priority.desc())
        .offset(skip)
        .limit(limit)
    )
    configs = result.scalars().all()
    return configs


@router.post("", response_model=AIServiceConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_ai_config(
    config: AIServiceConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new AI service configuration"""
    # If this is set as default, unset other defaults for the same service type
    if config.is_default:
        await db.execute(
            select(AIServiceConfig).where(
                AIServiceConfig.service_type == config.service_type,
                AIServiceConfig.is_default == True
            )
        )
        # Update all to is_default=False (simplified - in production use proper update)

    db_config = AIServiceConfig(**config.model_dump())
    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)
    return db_config


@router.post("/test")
async def test_connection(
    request: TestConnectionRequest,
    background_tasks: BackgroundTasks
):
    """Test AI service connection"""
    # This is a placeholder - actual implementation would call the AI service
    return {
        "status": "success",
        "message": "Connection test initiated",
        "provider": request.provider
    }


@router.get("/{config_id}", response_model=AIServiceConfigResponse)
async def get_ai_config(
    config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get AI configuration by ID"""
    result = await db.execute(select(AIServiceConfig).where(AIServiceConfig.id == config_id))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI configuration not found"
        )

    return config


@router.put("/{config_id}", response_model=AIServiceConfigResponse)
async def update_ai_config(
    config_id: int,
    config: AIServiceConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update AI configuration"""
    result = await db.execute(select(AIServiceConfig).where(AIServiceConfig.id == config_id))
    db_config = result.scalar_one_or_none()

    if not db_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI configuration not found"
        )

    update_data = config.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_config, field, value)

    await db.commit()
    await db.refresh(db_config)
    return db_config


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ai_config(
    config_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete AI configuration"""
    result = await db.execute(select(AIServiceConfig).where(AIServiceConfig.id == config_id))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI configuration not found"
        )

    await db.delete(config)
    await db.commit()
    return None
