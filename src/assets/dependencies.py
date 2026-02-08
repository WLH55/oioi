"""
资源依赖注入

提供 FastAPI 依赖注入函数，用于验证和获取资源。
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.assets.models import Asset
from src.database import get_db

from .exceptions import AssetNotFound
from .service import AssetService


async def get_asset_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> AssetService:
    """
    获取资源服务实例

    Args:
        db: 数据库会话

    Returns:
        资源服务实例
    """
    return AssetService(db)


async def valid_asset_id(
    asset_id: int,
    service: Annotated[AssetService, Depends(get_asset_service)],
) -> Asset:
    """
    验证资源 ID 并返回对象

    Args:
        asset_id: 资源 ID
        service: 资源服务

    Returns:
        资源对象

    Raises:
        AssetNotFound: 资源不存在
    """
    try:
        return await service.get_by_id(asset_id)
    except AssetNotFound:
        raise


# 类型别名
AssetDep = Annotated[Asset, Depends(valid_asset_id)]
ServiceDep = Annotated[AssetService, Depends(get_asset_service)]
