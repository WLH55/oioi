"""
角色库依赖注入

提供 FastAPI 依赖注入函数，用于验证和获取资源。
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.character_library import CharacterLibrary
from app.models.drama import Character
from src.database import get_db

from .exceptions import CharacterLibraryNotFound
from .service import CharacterLibraryService


async def get_character_library_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> CharacterLibraryService:
    """
    获取角色库服务实例

    Args:
        db: 数据库会话

    Returns:
        角色库服务实例
    """
    return CharacterLibraryService(db)


async def valid_library_item_id(
    item_id: int,
    service: Annotated[CharacterLibraryService, Depends(get_character_library_service)],
) -> CharacterLibrary:
    """
    验证角色库项 ID 并返回对象

    Args:
        item_id: 角色 ID
        service: 角色库服务

    Returns:
        角色库对象

    Raises:
        CharacterLibraryNotFound: 角色库项不存在
    """
    try:
        return await service.get_by_id(item_id)
    except CharacterLibraryNotFound:
        raise


async def valid_character_id(
    character_id: int,
    service: Annotated[CharacterLibraryService, Depends(get_character_library_service)],
) -> Character:
    """
    验证角色 ID 并返回对象

    Args:
        character_id: 角色 ID
        service: 角色库服务

    Returns:
        角色对象

    Raises:
        CharacterNotFound: 角色不存在
    """
    from .exceptions import CharacterNotFound

    try:
        return await service.get_character_by_id(character_id)
    except CharacterNotFound:
        raise


# 类型别名
LibraryItemDep = Annotated[CharacterLibrary, Depends(valid_library_item_id)]
CharacterDep = Annotated[Character, Depends(valid_character_id)]
ServiceDep = Annotated[CharacterLibraryService, Depends(get_character_library_service)]
