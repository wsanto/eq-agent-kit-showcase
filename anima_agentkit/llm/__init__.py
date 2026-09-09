"""
LLM Provider System for ANIMA AgentKit

Supports multiple LLM providers including:
- OpenAI-compatible APIs (OpenAI, Together, Groq, Fireworks, etc.)
- 0G Labs on-chain inference
- Custom providers

Features:
- Simple provider wrappers
- Manual model selection
- Streaming support
- On-chain verification (0G Labs)
"""

from .base import (
    LLMProvider,
    LLMMessage,
    LLMResponse,
    LLMProviderError,
    ProviderType
)
from .openai_compatible import OpenAICompatibleProvider
from .zerog import ZeroGProvider
from .registry import LLMProviderRegistry

__all__ = [
    # Base classes
    "LLMProvider",
    "LLMMessage",
    "LLMResponse",
    "LLMProviderError",
    "ProviderType",
    # Providers
    "OpenAICompatibleProvider",
    "ZeroGProvider",
    # Registry
    "LLMProviderRegistry",
]
