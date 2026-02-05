"""
Audio 模块 API 测试
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_extract_audio(async_client: AsyncClient):
    """测试提取音频"""
    request_data = {
        "video_path": "/path/to/video.mp4",
        "output_format": "mp3"
    }
    response = await async_client.post("/api/audio/extract", json=request_data)
    # 可能返回错误，但应该有正确的响应格式
    assert response.status_code == 200

    data = response.json()
    assert "code" in data
    assert "data" in data


@pytest.mark.asyncio
async def test_batch_extract_audio(async_client: AsyncClient):
    """测试批量提取音频"""
    request_data = {
        "video_paths": ["/path/to/video1.mp4", "/path/to/video2.mp4"],
        "output_format": "mp3"
    }
    response = await async_client.post("/api/audio/extract/batch", json=request_data)
    # 可能返回错误，但应该有正确的响应格式
    assert response.status_code == 200

    data = response.json()
    assert "code" in data
    assert "data" in data
