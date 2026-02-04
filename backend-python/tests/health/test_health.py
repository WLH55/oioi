"""Tests for health check endpoint"""
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查端点"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get("/health")

    assert response.status_code == 200

    # 验证响应格式符合 ApiResponse
    data = response.json()
    assert "code" in data
    assert "message" in data
    assert "data" in data

    # 验证成功响应
    assert data["code"] == 200
    assert data["data"]["status"] == "ok"
    assert "app" in data["data"]
    assert "version" in data["data"]
