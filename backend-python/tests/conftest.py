"""
测试配置和 fixtures

该模块提供测试所需的 fixtures 和配置。
"""
import pytest
from typing import AsyncGenerator
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.main import app
from src.config import settings
from src.database import Base


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    异步测试客户端 fixture

    使用 httpx 异步客户端测试 FastAPI 应用。

    Yields:
        AsyncClient: 配置好的异步测试客户端

    Example:
        @pytest.mark.asyncio
        async def test_health_check(client: AsyncClient):
            response = await client.get("/")
            assert response.status_code == 200
    """
    # 使用 ASGI 传输直接测试 FastAPI 应用
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def drama_data():
    """测试用剧目数据"""
    return {
        "id": 1,
        "title": "测试剧目",
        "description": "这是一个测试剧目",
    }


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    数据库会话 fixture

    为测试提供异步数据库会话。

    Yields:
        AsyncSession: 数据库会话
    """
    # 使用内存数据库进行测试
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 创建会话
    async with async_maker() as session:
        yield session

    # 清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
