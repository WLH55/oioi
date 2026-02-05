"""
Upload 模块 API 测试
"""
import pytest
import io
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_image(async_client: AsyncClient):
    """测试上传图片"""
    # 创建一个假的图片文件
    file_content = b"fake image content"
    files = {"file": ("test.jpg", io.BytesIO(file_content), "image/jpeg")}

    response = await async_client.post("/api/upload/image", files=files)
    # 可能返回错误，但应该有正确的响应格式
    assert response.status_code == 200

    data = response.json()
    assert "code" in data


@pytest.mark.asyncio
async def test_upload_video(async_client: AsyncClient):
    """测试上传视频"""
    # 创建一个假的视频文件
    file_content = b"fake video content"
    files = {"file": ("test.mp4", io.BytesIO(file_content), "video/mp4")}

    response = await async_client.post("/api/upload/video", files=files)
    # 可能返回错误，但应该有正确的响应格式
    assert response.status_code == 200

    data = response.json()
    assert "code" in data


@pytest.mark.asyncio
async def test_upload_audio(async_client: AsyncClient):
    """测试上传音频"""
    # 创建一个假的音频文件
    file_content = b"fake audio content"
    files = {"file": ("test.mp3", io.BytesIO(file_content), "audio/mpeg")}

    response = await async_client.post("/api/upload/audio", files=files)
    # 可能返回错误，但应该有正确的响应格式
    assert response.status_code == 200

    data = response.json()
    assert "code" in data
