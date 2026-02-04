"""
数据库连接和会话管理

该模块提供数据库连接、会话管理和初始化功能。
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

from src.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base 类用于模型声明
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话

    这是一个依赖注入函数，用于在路由中获取数据库会话。
    自动处理事务提交和回滚。

    Yields:
        AsyncSession: 数据库会话

    Example:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    初始化数据库表

    创建所有定义的数据库表。
    注意：此函数会在应用启动时调用。
    """
    async with engine.begin() as conn:
        # 导入所有模型以确保它们被注册
        # 注意：这些导入路径暂时使用 app，后续会迁移到 src
        from app.models import drama, asset, character_library, ai_config, task
        from app.models import image_generation, video_generation, video_merge
        from app.models import frame_prompt, timeline

        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
