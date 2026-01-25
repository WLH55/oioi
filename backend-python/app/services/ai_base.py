from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class ImageGenerationRequest(BaseModel):
    """Base image generation request"""
    prompt: str
    negative_prompt: Optional[str] = None
    model: str
    size: str = "1024x1024"
    quality: str = "standard"
    style: Optional[str] = None
    steps: Optional[int] = None
    cfg_scale: Optional[float] = None
    seed: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    reference_images: Optional[List[str]] = None


class ImageGenerationResponse(BaseModel):
    """Base image generation response"""
    image_url: str
    local_path: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    task_id: Optional[str] = None
    status: str = "completed"
    error: Optional[str] = None


class VideoGenerationRequest(BaseModel):
    """Base video generation request"""
    prompt: str
    model: Optional[str] = None
    image_url: Optional[str] = None
    first_frame_url: Optional[str] = None
    last_frame_url: Optional[str] = None
    reference_mode: Optional[str] = "single"
    duration: Optional[int] = 5
    fps: Optional[int] = 30
    aspect_ratio: Optional[str] = "16:9"
    style: Optional[str] = None
    motion_level: Optional[int] = None
    camera_motion: Optional[str] = None
    seed: Optional[int] = None


class VideoGenerationResponse(BaseModel):
    """Base video generation response"""
    video_url: str
    local_path: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    task_id: Optional[str] = None
    status: str = "completed"
    error: Optional[str] = None


class BaseAIProvider(ABC):
    """Base class for AI providers"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize AI provider

        Args:
            config: Provider configuration containing api_key, base_url, etc.
        """
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url")
        self.model = config.get("model", [])
        self.endpoint = config.get("endpoint", "")
        self.query_endpoint = config.get("query_endpoint", "")
        self.settings = config.get("settings", "{}")

    @abstractmethod
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """
        Generate image using AI

        Args:
            request: Image generation request

        Returns:
            ImageGenerationResponse
        """
        pass

    @abstractmethod
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResponse:
        """
        Generate video using AI

        Args:
            request: Video generation request

        Returns:
            VideoGenerationResponse
        """
        pass

    @abstractmethod
    async def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Check async task status

        Args:
            task_id: Task ID to check

        Returns:
            Task status dict with keys: status, result, error
        """
        pass

    async def test_connection(self) -> bool:
        """
        Test connection to AI service

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Default implementation - override in provider if needed
            return bool(self.api_key and self.base_url)
        except Exception:
            return False


class TextGenerationRequest(BaseModel):
    """Base text generation request"""
    prompt: str
    model: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    system_prompt: Optional[str] = None


class TextGenerationResponse(BaseModel):
    """Base text generation response"""
    text: str
    usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None


class BaseTextAIProvider(ABC):
    """Base class for text AI providers"""

    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url")
        self.model = config.get("model", [])

    @abstractmethod
    async def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        """Generate text using AI"""
        pass
