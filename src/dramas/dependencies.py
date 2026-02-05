"""
剧目依赖注入

提供 FastAPI 依赖注入函数，用于验证和获取资源。
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.drama import Drama
from src.database import get_db

from .exceptions import DramaNotFound
from .service import DramaService


async def get_drama_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> DramaService:
    """
    获取剧目服务实例

    Args:
        db: 数据库会话

    Returns:
        剧目服务实例
    """
    return DramaService(db)


async def valid_drama_id(
    drama_id: int,
    service: Annotated[DramaService, Depends(get_drama_service)],
) -> Drama:
    """
    验证剧目 ID 并返回对象

    Args:
        drama_id: 剧目 ID
        service: 剧目服务

    Returns:
        剧目对象

    Raises:
        DramaNotFound: 剧目不存在
    """
    try:
        return await service.get_by_id(drama_id)
    except DramaNotFound:
        raise


# 类型别名
DramaDep = Annotated[Drama, Depends(valid_drama_id)]
ServiceDep = Annotated[DramaService, Depends(get_drama_service)]
