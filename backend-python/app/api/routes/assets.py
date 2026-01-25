from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.core.database import get_db
from app.models.asset import Asset, AssetType
from app.models.image_generation import ImageGeneration
from app.models.video_generation import VideoGeneration
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class AssetBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    category: Optional[str] = None
    url: str
    thumbnail_url: Optional[str] = None


class AssetCreate(AssetBase):
    drama_id: Optional[int] = None
    episode_id: Optional[int] = None
    storyboard_id: Optional[int] = None
    storyboard_num: Optional[int] = None


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_favorite: Optional[bool] = None


@router.get("", response_model=List[dict])
async def list_assets(
    skip: int = 0,
    limit: int = 100,
    drama_id: Optional[int] = None,
    episode_id: Optional[int] = None,
    type: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List assets with filters"""
    query = select(Asset)

    if drama_id:
        query = query.where(Asset.drama_id == drama_id)
    if episode_id:
        query = query.where(Asset.episode_id == episode_id)
    if type:
        query = query.where(Asset.type == type)
    if category:
        query = query.where(Asset.category == category)

    query = query.offset(skip).limit(limit).order_by(Asset.created_at.desc())
    result = await db.execute(query)
    assets = result.scalars().all()

    return [
        {
            "id": asset.id,
            "name": asset.name,
            "description": asset.description,
            "type": asset.type,
            "category": asset.category,
            "url": asset.url,
            "thumbnail_url": asset.thumbnail_url,
            "drama_id": asset.drama_id,
            "episode_id": asset.episode_id,
            "storyboard_id": asset.storyboard_id,
            "file_size": asset.file_size,
            "mime_type": asset.mime_type,
            "is_favorite": asset.is_favorite,
            "view_count": asset.view_count,
            "created_at": asset.created_at
        }
        for asset in assets
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset: AssetCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new asset"""
    db_asset = Asset(**asset.model_dump())
    db.add(db_asset)
    await db.commit()
    await db.refresh(db_asset)

    return {
        "message": "Asset created successfully",
        "asset_id": db_asset.id,
        "asset": {
            "id": db_asset.id,
            "name": db_asset.name,
            "type": db_asset.type,
            "url": db_asset.url
        }
    }


@router.get("/{asset_id}")
async def get_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get asset by ID"""
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )

    # Increment view count
    asset.view_count += 1
    await db.commit()

    return {
        "id": asset.id,
        "name": asset.name,
        "description": asset.description,
        "type": asset.type,
        "category": asset.category,
        "url": asset.url,
        "thumbnail_url": asset.thumbnail_url,
        "local_path": asset.local_path,
        "file_size": asset.file_size,
        "mime_type": asset.mime_type,
        "width": asset.width,
        "height": asset.height,
        "duration": asset.duration,
        "format": asset.format,
        "drama_id": asset.drama_id,
        "episode_id": asset.episode_id,
        "storyboard_id": asset.storyboard_id,
        "image_gen_id": asset.image_gen_id,
        "video_gen_id": asset.video_gen_id,
        "is_favorite": asset.is_favorite,
        "view_count": asset.view_count,
        "created_at": asset.created_at,
        "updated_at": asset.updated_at
    }


@router.put("/{asset_id}")
async def update_asset(
    asset_id: int,
    asset: AssetUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update asset"""
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    db_asset = result.scalar_one_or_none()

    if not db_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )

    update_data = asset.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_asset, field, value)

    await db.commit()
    await db.refresh(db_asset)

    return {
        "message": "Asset updated successfully",
        "asset_id": asset_id
    }


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete asset"""
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )

    await db.delete(asset)
    await db.commit()

    return {
        "message": "Asset deleted successfully",
        "asset_id": asset_id
    }


@router.post("/import/image/{image_gen_id}")
async def import_from_image_gen(
    image_gen_id: int,
    name: str,
    db: AsyncSession = Depends(get_db)
):
    """Import asset from image generation"""
    # Get image generation
    result = await db.execute(select(ImageGeneration).where(ImageGeneration.id == image_gen_id))
    image_gen = result.scalar_one_or_none()

    if not image_gen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image generation not found"
        )

    if not image_gen.image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image generation has no image URL"
        )

    # Create asset
    asset = Asset(
        name=name,
        type=AssetType.IMAGE.value,
        url=image_gen.image_url,
        local_path=image_gen.local_path,
        width=image_gen.width,
        height=image_gen.height,
        drama_id=image_gen.drama_id,
        image_gen_id=image_gen.id
    )

    db.add(asset)
    await db.commit()
    await db.refresh(asset)

    return {
        "message": "Asset imported successfully",
        "asset_id": asset.id,
        "image_gen_id": image_gen_id
    }


@router.post("/import/video/{video_gen_id}")
async def import_from_video_gen(
    video_gen_id: int,
    name: str,
    db: AsyncSession = Depends(get_db)
):
    """Import asset from video generation"""
    # Get video generation
    result = await db.execute(select(VideoGeneration).where(VideoGeneration.id == video_gen_id))
    video_gen = result.scalar_one_or_none()

    if not video_gen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video generation not found"
        )

    if not video_gen.video_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video generation has no video URL"
        )

    # Create asset
    asset = Asset(
        name=name,
        type=AssetType.VIDEO.value,
        url=video_gen.video_url,
        local_path=video_gen.local_path,
        width=video_gen.width,
        height=video_gen.height,
        duration=video_gen.duration,
        drama_id=video_gen.drama_id,
        video_gen_id=video_gen.id
    )

    db.add(asset)
    await db.commit()
    await db.refresh(asset)

    return {
        "message": "Asset imported successfully",
        "asset_id": asset.id,
        "video_gen_id": video_gen_id
    }
