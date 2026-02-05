"""
AI 配置依赖项

定义 AI 配置模块的 FastAPI 依赖项。
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_config import AIServiceConfig
from src.ai_configs.exceptions import AIConfigNotFound
from src.database import get_db


async def valid_config_id(config_id: int, db: Annotated[AsyncSession, Depends(get_db)]) -> AIServiceConfig:
    """
    验证配置 ID 并返回配置对象

    Args:
        config_id: 配置 ID
        db: 数据库会话

    Returns:
        AIServiceConfig: 配置对象

    Raises:
        AIConfigNotFound: 配置不存在
    """
    result = await db.execute(select(AIServiceConfig).where(AIServiceConfig.id == config_id))
    config = result.scalar_one_or_none()

    if not config:
        raise AIConfigNotFound(config_id)

    return config
