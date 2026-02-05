"""
Video Merges 模块依赖注入
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db

from .service import VideoMergeService


async def get_video_merge_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> VideoMergeService:
    """
    获取视频合成服务实例

    Args:
        db: 数据库会话

    Returns:
        视频合成服务实例
    """
    return VideoMergeService(db)
