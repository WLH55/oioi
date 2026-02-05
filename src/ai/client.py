"""
AI 客户端基础接口

定义 AI 服务的抽象基类和请求/响应模型
"""
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ImageGenerationRequest(BaseModel):
    """图片生成请求模型"""
    prompt: str
    negative_prompt: str | None = None
    model: str
    size: str = "1024x1024"
    quality: str = "standard"
    style: str | None = None
    steps: int | None = None
    cfg_scale: float | None = None
    seed: int | None = None
    width: int | None = None
    height: int | None = None
    reference_images: list[str] | None = None


class ImageGenerationResponse(BaseModel):
    """图片生成响应模型"""
    image_url: str
    local_path: str | None = None
    width: int | None = None
    height: int | None = None
    task_id: str | None = None
    status: str = "completed"
    error: str | None = None


class VideoGenerationRequest(BaseModel):
    """视频生成请求模型"""
    prompt: str
    model: str | None = None
    image_url: str | None = None
    first_frame_url: str | None = None
    last_frame_url: str | None = None
    reference_mode: str | None = "single"
    duration: int | None = 5
    fps: int | None = 30
    aspect_ratio: str | None = "16:9"
    style: str | None = None
    motion_level: int | None = None
    camera_motion: str | None = None
    seed: int | None = None


class VideoGenerationResponse(BaseModel):
    """视频生成响应模型"""
    video_url: str
    local_path: str | None = None
    width: int | None = None
    height: int | None = None
    duration: int | None = None
    task_id: str | None = None
    status: str = "completed"
    error: str | None = None


class BaseAIProvider(ABC):
    """AI 提供商基类"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化 AI 提供商

        Args:
            config: 提供商配置，包含 api_key, base_url 等
        """
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url")
        self.model = config.get("model", "")
        self.endpoint = config.get("endpoint", "")
        self.query_endpoint = config.get("query_endpoint", "")
        self.settings = config.get("settings", {})

    @abstractmethod
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """
        生成图片

        Args:
            request: 图片生成请求

        Returns:
            ImageGenerationResponse
        """
        pass

    @abstractmethod
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResponse:
        """
        生成视频

        Args:
            request: 视频生成请求

        Returns:
            VideoGenerationResponse
        """
        pass

    @abstractmethod
    async def check_task_status(self, task_id: str) -> dict[str, Any]:
        """
        检查异步任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态字典，包含: status, result, error
        """
        pass

    async def test_connection(self) -> bool:
        """
        测试与 AI 服务的连接

        Returns:
            连接成功返回 True，否则返回 False
        """
        try:
            return bool(self.api_key and self.base_url)
        except Exception:
            return False


class TextGenerationRequest(BaseModel):
    """文本生成请求模型"""
    prompt: str
    model: str
    max_tokens: int | None = 1000
    temperature: float | None = 0.7
    system_prompt: str | None = None


class TextGenerationResponse(BaseModel):
    """文本生成响应模型"""
    text: str
    usage: dict[str, int] | None = None
    error: str | None = None


class BaseTextAIProvider(ABC):
    """文本 AI 提供商基类"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化文本 AI 提供商

        Args:
            config: 提供商配置
        """
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url")
        self.model = config.get("model", "")
        self.endpoint = config.get("endpoint", "")
        self.settings = config.get("settings", {})

    @abstractmethod
    async def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        """
        生成文本

        Args:
            request: 文本生成请求

        Returns:
            TextGenerationResponse
        """
        pass

    async def test_connection(self) -> bool:
        """
        测试与 AI 服务的连接

        Returns:
            连接成功返回 True，否则返回 False
        """
        try:
            return bool(self.api_key and self.base_url)
        except Exception:
            return False
