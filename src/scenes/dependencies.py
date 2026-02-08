"""
Scenes 模块依赖注入

提供 FastAPI 依赖注入函数
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.scenes.models import Scene
from src.database import get_db

from .exceptions import SceneNotFound
from .service import SceneService


async def get_scene_service(db: AsyncSession = Depends(get_db)) -> SceneService:
    """
    获取 SceneService 实例

    Args:
        db: 数据库会话

    Returns:
        SceneService 实例
    """
    return SceneService(db)


async def valid_scene_id(
    scene_id: int,
    service: SceneService = Depends(get_scene_service)
) -> Scene:
    """
    验证场景ID是否有效

    Args:
        scene_id: 场景ID
        service: SceneService 实例

    Returns:
        Scene 对象

    Raises:
        SceneNotFound: 场景不存在
    """
    try:
        return await service.get_by_id(scene_id)
    except SceneNotFound:
        raise


# 类型别名，方便在其他模块中使用
ServiceDep = Annotated[SceneService, Depends(get_scene_service)]
SceneDep = Annotated[Scene, Depends(valid_scene_id)]
