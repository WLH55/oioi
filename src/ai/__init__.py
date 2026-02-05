"""
共享 AI 服务模块

提供 AI 客户端的基础接口和工厂模式
"""
from .client import (
    BaseAIProvider,
    BaseTextAIProvider,
    ImageGenerationRequest,
    ImageGenerationResponse,
    TextGenerationRequest,
    TextGenerationResponse,
    VideoGenerationRequest,
    VideoGenerationResponse,
)
from .factory import AIProviderFactory, get_ai_provider

__all__ = [
    "BaseAIProvider",
    "BaseTextAIProvider",
    "ImageGenerationRequest",
    "ImageGenerationResponse",
    "VideoGenerationRequest",
    "VideoGenerationResponse",
    "TextGenerationRequest",
    "TextGenerationResponse",
    "AIProviderFactory",
    "get_ai_provider",
]
