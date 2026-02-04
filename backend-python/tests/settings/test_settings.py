"""Tests for settings endpoints"""
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_get_language():
    """测试获取语言设置"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/settings/language")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "language" in data["data"]


@pytest.mark.asyncio
async def test_get_all_settings():
    """测试获取所有系统设置"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/settings/all")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "app_name" in data["data"]
    assert "app_version" in data["data"]


@pytest.mark.asyncio
async def test_update_language():
    """测试更新语言设置"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.post("/api/v1/settings/update-language", json={
            "language": "en-US"
        })

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["language"] == "en-US"
