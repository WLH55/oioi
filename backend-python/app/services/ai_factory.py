from typing import Dict, Any, Type, Optional
from app.services.ai_base import BaseAIProvider, BaseTextAIProvider
from app.services.ai_openai import OpenAIProvider
from app.services.ai_doubao import DoubaoProvider


class AIProviderFactory:
    """Factory for creating AI provider instances"""

    _providers: Dict[str, Type[BaseAIProvider]] = {
        "openai": OpenAIProvider,
        "dall-e": OpenAIProvider,  # Alias for OpenAI
        "sora": OpenAIProvider,  # Alias for OpenAI
        "doubao": DoubaoProvider,
        "volcengine": DoubaoProvider,  # Alias for Doubao
        "volces": DoubaoProvider,  # Alias for Doubao
    }

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseAIProvider]):
        """Register a new AI provider"""
        cls._providers[name.lower()] = provider_class

    @classmethod
    def create_provider(cls, provider_name: str, config: Dict[str, Any]) -> BaseAIProvider:
        """
        Create an AI provider instance

        Args:
            provider_name: Name of the provider (e.g., 'openai', 'doubao')
            config: Configuration dict containing api_key, base_url, etc.

        Returns:
            AI provider instance

        Raises:
            ValueError: If provider is not found
        """
        provider_name_lower = provider_name.lower()

        if provider_name_lower not in cls._providers:
            # Try to find partial match
            for name in cls._providers:
                if provider_name_lower in name:
                    provider_name_lower = name
                    break
            else:
                raise ValueError(
                    f"Unknown AI provider: {provider_name}. "
                    f"Available providers: {list(cls._providers.keys())}"
                )

        provider_class = cls._providers[provider_name_lower]
        return provider_class(config)

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available provider names"""
        return list(cls._providers.keys())


def get_ai_provider(provider_name: str, config: Dict[str, Any]) -> BaseAIProvider:
    """
    Convenience function to get an AI provider

    Args:
        provider_name: Name of the provider
        config: Configuration dict

    Returns:
        AI provider instance
    """
    return AIProviderFactory.create_provider(provider_name, config)
