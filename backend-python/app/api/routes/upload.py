from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.core.database import get_db
from app.core.config import settings
from app.utils.file import save_upload_file, get_file_url
from app.models.drama import Character
import os
import uuid

router = APIRouter()


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    character_id: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload image file"""
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )

    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"

    # Save file
    try:
        file_path = await save_upload_file(
            file,
            settings.LOCAL_STORAGE_PATH,
            filename
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Get file URL
    file_url = get_file_url(filename, settings.BASE_URL)

    # If character_id provided, update character image
    if character_id:
        result = await db.execute(select(Character).where(Character.id == character_id))
        character = result.scalar_one_or_none()

        if character:
            character.image_url = file_url
            await db.commit()

    return {
        "message": "Image uploaded successfully",
        "filename": filename,
        "url": file_url,
        "path": file_path,
        "character_id": character_id
    }


@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload video file"""
    # Validate file type
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a video"
        )

    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"

    # Save file
    try:
        file_path = await save_upload_file(
            file,
            settings.LOCAL_STORAGE_PATH,
            filename
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Get file URL
    file_url = get_file_url(filename, settings.BASE_URL)

    return {
        "message": "Video uploaded successfully",
        "filename": filename,
        "url": file_url,
        "path": file_path
    }


@router.post("/audio")
async def upload_audio(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload audio file"""
    # Validate file type
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an audio file"
        )

    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"

    # Save file
    try:
        file_path = await save_upload_file(
            file,
            settings.LOCAL_STORAGE_PATH,
            filename
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Get file URL
    file_url = get_file_url(filename, settings.BASE_URL)

    return {
        "message": "Audio uploaded successfully",
        "filename": filename,
        "url": file_url,
        "path": file_path
    }
