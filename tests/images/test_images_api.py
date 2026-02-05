"""
Images 模块 API 测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_list_image_generations(async_client: AsyncClient):
    """测试获取图片生成列表"""
    response = await async_client.get("/api/images/list")
    assert response.status_code == 200

    data = response.json()
    assert "code" in data
    assert "data" in data
    assert data["code"] == 200


@pytest.mark.asyncio
async def test_get_image_generation(async_client: AsyncClient):
    """测试获取图片生成详情"""
    response = await async_client.get("/api/images/get?gen_id=1")
    # 可能返回 404，但应该有正确的响应格式
    assert response.status_code in [200, 404]

    data = response.json()
    assert "code" in data


@pytest.mark.asyncio
async def test_generate_image_for_scene(async_client: AsyncClient):
    """测试为场景生成图片"""
    # 需要先有场景数据，这里假设存在 scene_id=1
    response = await async_client.post("/api/images/scene/generate?scene_id=999")
    # 应该返回错误，因为场景不存在
    assert response.status_code == 200

    data = response.json()
    assert "code" in data
    # 应该返回业务错误码
    assert data["code"] != 200


@pytest.mark.asyncio
async def test_get_episode_backgrounds(async_client: AsyncClient):
    """测试获取章节场景背景图"""
    response = await async_client.get("/api/images/episode/backgrounds?episode_id=1")
    assert response.status_code == 200

    data = response.json()
    assert "code" in data
    assert "data" in data
