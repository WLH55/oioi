"""
Videos 模块 API 测试
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_video_generations(async_client: AsyncClient):
    """测试获取视频生成列表"""
    response = await async_client.get("/api/videos/list")
    assert response.status_code == 200

    data = response.json()
    assert "code" in data
    assert "data" in data
    assert data["code"] == 200


@pytest.mark.asyncio
async def test_get_video_generation(async_client: AsyncClient):
    """测试获取视频生成详情"""
    response = await async_client.get("/api/videos/get?gen_id=1")
    # 可能返回 404，但应该有正确的响应格式
    assert response.status_code in [200, 404]

    data = response.json()
    assert "code" in data


@pytest.mark.asyncio
async def test_generate_video_from_image(async_client: AsyncClient):
    """测试从图片生成视频"""
    response = await async_client.post("/api/videos/image/generate?image_gen_id=999")
    # 应该返回错误，因为图片生成不存在
    assert response.status_code == 200

    data = response.json()
    assert "code" in data
    # 应该返回业务错误码
    assert data["code"] != 200
