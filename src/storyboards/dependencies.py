"""
Storyboards 模块依赖注入

提供 FastAPI 依赖注入函数
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.drama import Storyboard
from src.database import get_db

from .exceptions import StoryboardNotFound
from .service import StoryboardService


async def get_storyboard_service(db: AsyncSession = Depends(get_db)) -> StoryboardService:
    """
    获取 StoryboardService 实例

    Args:
        db: 数据库会话

    Returns:
        StoryboardService 实例
    """
    return StoryboardService(db)


async def valid_storyboard_id(
    storyboard_id: int,
    service: StoryboardService = Depends(get_storyboard_service)
) -> Storyboard:
    """
    验证分镜ID是否有效

    Args:
        storyboard_id: 分镜ID
        service: StoryboardService 实例

    Returns:
        Storyboard 对象

    Raises:
        StoryboardNotFound: 分镜不存在
    """
    try:
        return await service.get_by_id(storyboard_id)
    except StoryboardNotFound:
        raise


# 类型别名，方便在其他模块中使用
ServiceDep = Annotated[StoryboardService, Depends(get_storyboard_service)]
StoryboardDep = Annotated[Storyboard, Depends(valid_storyboard_id)]
