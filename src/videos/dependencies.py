"""
Videos 模块依赖注入
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db

from .service import VideoGenerationService


async def get_video_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> VideoGenerationService:
    """
    获取视频生成服务实例

    Args:
        db: 数据库会话

    Returns:
        视频生成服务实例
    """
    return VideoGenerationService(db)
