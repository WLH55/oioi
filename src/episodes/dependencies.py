"""
Episodes 模块依赖注入

提供 FastAPI 依赖注入函数
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.episodes.models import Episode
from src.database import get_db

from .exceptions import EpisodeNotFound
from .service import EpisodeService


async def get_episode_service(db: AsyncSession = Depends(get_db)) -> EpisodeService:
    """
    获取 EpisodeService 实例

    Args:
        db: 数据库会话

    Returns:
        EpisodeService 实例
    """
    return EpisodeService(db)


async def valid_episode_id(
    episode_id: int,
    service: EpisodeService = Depends(get_episode_service)
) -> Episode:
    """
    验证集数ID是否有效

    Args:
        episode_id: 集数ID
        service: EpisodeService 实例

    Returns:
        Episode 对象

    Raises:
        EpisodeNotFound: 集数不存在
    """
    try:
        return await service.get_by_id(episode_id)
    except EpisodeNotFound:
        raise


# 类型别名，方便在其他模块中使用
ServiceDep = Annotated[EpisodeService, Depends(get_episode_service)]
EpisodeDep = Annotated[Episode, Depends(valid_episode_id)]
