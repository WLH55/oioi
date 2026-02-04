"""
AI 配置服务层

处理 AI 配置相关的业务逻辑。
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.ai_configs.models import AIServiceConfig
from src.ai_configs.exceptions import DuplicateDefaultConfig


class AIConfigService:
    """AI 配置服务"""

    @staticmethod
    async def list_configs(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[AIServiceConfig]:
        """
        获取 AI 配置列表

        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 限制数量

        Returns:
            List[AIServiceConfig]: 配置列表
        """
        result = await db.execute(
            select(AIServiceConfig)
            .order_by(AIServiceConfig.priority.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(config_id: int, db: AsyncSession) -> AIServiceConfig:
        """
        根据 ID 获取配置

        Args:
            config_id: 配置 ID
            db: 数据库会话

        Returns:
            AIServiceConfig: 配置对象
        """
        result = await db.execute(
            select(AIServiceConfig).where(AIServiceConfig.id == config_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_config(
        config_data: dict,
        db: AsyncSession
    ) -> AIServiceConfig:
        """
        创建新配置

        Args:
            config_data: 配置数据
            db: 数据库会话

        Returns:
            AIServiceConfig: 创建的配置对象
        """
        db_config = AIServiceConfig(**config_data)
        db.add(db_config)
        await db.commit()
        await db.refresh(db_config)
        return db_config

    @staticmethod
    async def update_config(
        config: AIServiceConfig,
        update_data: dict,
        db: AsyncSession
    ) -> AIServiceConfig:
        """
        更新配置

        Args:
            config: 配置对象
            update_data: 更新数据
            db: 数据库会话

        Returns:
            AIServiceConfig: 更新后的配置对象
        """
        for field, value in update_data.items():
            setattr(config, field, value)

        await db.commit()
        await db.refresh(config)
        return config

    @staticmethod
    async def delete_config(config: AIServiceConfig, db: AsyncSession) -> None:
        """
        删除配置

        Args:
            config: 配置对象
            db: 数据库会话
        """
        await db.delete(config)
        await db.commit()
