"""
Upload 模块依赖注入
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db

from .service import UploadService


async def get_upload_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UploadService:
    """
    获取上传服务实例

    Args:
        db: 数据库会话

    Returns:
        上传服务实例
    """
    return UploadService(db)
