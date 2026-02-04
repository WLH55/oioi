"""Tests for AI configs endpoints"""
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_list_ai_configs():
    """测试获取 AI 配置列表"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/ai-configs/list")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "list" in data["data"]


@pytest.mark.asyncio
async def test_test_connection():
    """测试连接接口"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.post("/api/v1/ai-configs/test-connection", json={
            "base_url": "https://api.openai.com/v1",
            "api_key": "test-key",
            "model": ["gpt-4"],
            "provider": "openai"
        })

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "status" in data["data"]
