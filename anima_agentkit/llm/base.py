"""
Base LLM Provider Interface for ANIMA AgentKit

Provides abstract base class for LLM providers with support for:
- OpenAI-compatible APIs
- On-chain inference (0G Labs)
- Model selection and routing
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum


class ProviderType(Enum):
    """Types of LLM providers."""
    OPENAI_COMPATIBLE = "openai_compatible"  # Any OpenAI-compatible API
    ZEROG = "zerog"  # 0G Labs on-chain inference
    ANTHROPIC = "anthropic"  # Anthropic Claude
    CUSTOM = "custom"  # Custom provider implementation


@dataclass
class LLMMessage:
    """Message format for LLM conversations."""
    role: str  # "system", "user", "assistant"
    content: str
    name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        msg = {"role": self.role, "content": self.content}
        if self.name:
            msg["name"] = self.name
        return msg


@dataclass
class LLMResponse:
    """Response from LLM provider."""
    content: str
    model: str
    provider: str
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "usage": self.usage,
            "finish_reason": self.finish_reason,
            "metadata": self.metadata
        }


class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    pass


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All providers must implement this interface to work with ANIMA AgentKit.
    Supports both off-chain (traditional APIs) and on-chain (0G Labs) inference.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: str = "gpt-4",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize LLM provider.

        Args:
            api_key: API key for authentication
            base_url: Base URL for API endpoint
            default_model: Default model to use
            config: Additional configuration
        """
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = default_model
        self.config = config or {}

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """
        Generate chat completion.

        Args:
            messages: List of conversation messages
            model: Model to use (defaults to default_model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse with generated content

        Raises:
            LLMProviderError: If request fails
        """
        pass

    @abstractmethod
    async def chat_completion_stream(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate streaming chat completion.

        Args:
            messages: List of conversation messages
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Yields:
            Content chunks as they're generated

        Raises:
            LLMProviderError: If request fails
        """
        pass

    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """
        Get list of available models.

        Returns:
            List of model identifiers
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close any open connections."""
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.default_model}>"


