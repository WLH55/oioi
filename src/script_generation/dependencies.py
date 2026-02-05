"""
Script Generation 模块依赖注入

提供 FastAPI 依赖注入函数
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db

from .service import ScriptGenerationService


async def get_script_generation_service(db: AsyncSession = Depends(get_db)) -> ScriptGenerationService:
    """
    获取 ScriptGenerationService 实例

    Args:
        db: 数据库会话

    Returns:
        ScriptGenerationService 实例
    """
    return ScriptGenerationService(db)


# 类型别名，方便在其他模块中使用
ServiceDep = Annotated[ScriptGenerationService, Depends(get_script_generation_service)]
