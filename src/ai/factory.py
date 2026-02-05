"""
AI 提供商工厂

用于创建和管理 AI 提供商实例
"""
from typing import Any

from services.ai_doubao import DoubaoProvider

# 从 app 导入现有提供商
from services.ai_openai import OpenAIProvider

from .client import BaseAIProvider


class AIProviderFactory:
    """AI 提供商工厂类"""

    _providers: dict[str, type[BaseAIProvider]] = {
        "openai": OpenAIProvider,
        "dall-e": OpenAIProvider,  # 别名
        "sora": OpenAIProvider,  # 别名
        "doubao": DoubaoProvider,
        "volcengine": DoubaoProvider,  # 别名
        "volces": DoubaoProvider,  # 别名
    }

    @classmethod
    def register_provider(cls, name: str, provider_class: type[BaseAIProvider]):
        """
        注册新的 AI 提供商

        Args:
            name: 提供商名称
            provider_class: 提供商类
        """
        cls._providers[name.lower()] = provider_class

    @classmethod
    def create_provider(cls, provider_name: str, config: dict[str, Any]) -> BaseAIProvider:
        """
        创建 AI 提供商实例

        Args:
            provider_name: 提供商名称 (如 'openai', 'doubao')
            config: 配置字典，包含 api_key, base_url 等

        Returns:
            AI 提供商实例

        Raises:
            ValueError: 如果提供商不存在
        """
        provider_name_lower = provider_name.lower()

        if provider_name_lower not in cls._providers:
            # 尝试部分匹配
            for name in cls._providers:
                if provider_name_lower in name:
                    provider_name_lower = name
                    break
            else:
                raise ValueError(
                    f"未知的 AI 提供商: {provider_name}. "
                    f"可用的提供商: {list(cls._providers.keys())}"
                )

        provider_class = cls._providers[provider_name_lower]
        return provider_class(config)

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """获取可用的提供商名称列表"""
        return list(cls._providers.keys())


def get_ai_provider(provider_name: str, config: dict[str, Any]) -> BaseAIProvider:
    """
    获取 AI 提供商的便捷函数

    Args:
        provider_name: 提供商名称
        config: 配置字典

    Returns:
        AI 提供商实例
    """
    return AIProviderFactory.create_provider(provider_name, config)
