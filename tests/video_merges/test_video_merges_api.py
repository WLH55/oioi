"""
Video Merges 模块 API 测试
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_video_merges(async_client: AsyncClient):
    """测试获取视频合成列表"""
    response = await async_client.get("/api/video-merges/list")
    assert response.status_code == 200

    data = response.json()
    assert "code" in data
    assert "data" in data
    assert data["code"] == 200


@pytest.mark.asyncio
async def test_get_video_merge(async_client: AsyncClient):
    """测试获取视频合成详情"""
    response = await async_client.get("/api/video-merges/get?merge_id=1")
    # 可能返回 404，但应该有正确的响应格式
    assert response.status_code in [200, 404]

    data = response.json()
    assert "code" in data
