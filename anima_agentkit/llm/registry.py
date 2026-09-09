"""
LLM Provider Registry

Manages registration and instantiation of LLM providers.
"""

from typing import Dict, Optional, Type
from loguru import logger

from .base import LLMProvider, LLMProviderError
from .openai_compatible import OpenAICompatibleProvider
from .zerog import ZeroGProvider


class LLMProviderRegistry:
    """
    Registry for LLM providers.

    Handles provider registration and instantiation.
    Users manually select their provider and model.
    """

    _providers: Dict[str, Type[LLMProvider]] = {}
    _instances: Dict[str, LLMProvider] = {}

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider]) -> None:
        """Register a provider class."""
        cls._providers[name] = provider_class
        logger.debug(f"Registered LLM provider: {name}")

    @classmethod
    def create_provider(
        cls,
        name: str,
        **kwargs
    ) -> LLMProvider:
        """Create provider instance."""
        if name not in cls._providers:
            raise LLMProviderError(f"Provider '{name}' not registered")

        provider_class = cls._providers[name]
        instance = provider_class(**kwargs)
        logger.info(f"Created LLM provider: {name}")
        return instance

    @classmethod
    def get_provider(cls, name: str) -> Optional[LLMProvider]:
        """Get cached provider instance."""
        return cls._instances.get(name)

    @classmethod
    def list_providers(cls) -> list:
        """List registered providers."""
        return list(cls._providers.keys())


# Auto-register built-in providers
LLMProviderRegistry.register_provider("openai_compatible", OpenAICompatibleProvider)
LLMProviderRegistry.register_provider("zerog", ZeroGProvider)

logger.info("LLM provider system initialized")
