"""
Images 模块依赖注入
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db

from .service import ImageGenerationService


async def get_image_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ImageGenerationService:
    """
    获取图片生成服务实例

    Args:
        db: 数据库会话

    Returns:
        图片生成服务实例
    """
    return ImageGenerationService(db)
