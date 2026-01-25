from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings
import json

router = APIRouter()


class LanguageUpdate(BaseModel):
    language: str


@router.get("/language")
async def get_language():
    """Get system language setting"""
    return {
        "language": settings.LANGUAGE
    }


@router.put("/language")
async def update_language(request: LanguageUpdate):
    """Update system language setting"""
    # In real implementation, this would update a persistent settings store
    return {
        "message": "Language updated successfully",
        "language": request.language
    }


@router.get("/all")
async def get_all_settings():
    """Get all system settings (excluding sensitive data)"""
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "language": settings.LANGUAGE,
        "storage_type": settings.STORAGE_TYPE,
        "default_ai_provider": settings.DEFAULT_AI_PROVIDER,
        "cors_origins": settings.CORS_ORIGINS
    }
