"""
OpenAI-Compatible LLM Provider

Supports any OpenAI-compatible API including OpenAI, Azure, Together, Groq, etc.
"""

import httpx
from typing import Dict, Any, List, Optional, AsyncIterator
from loguru import logger

from .base import LLMProvider, LLMMessage, LLMResponse, LLMProviderError


class OpenAICompatibleProvider(LLMProvider):
    """OpenAI-compatible API provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        default_model: str = "gpt-4",
        timeout: float = 60.0,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(api_key, base_url, default_model, config)
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers=self._get_headers()
        )

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def chat_completion(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        model = model or self.default_model
        messages_dict = [msg.to_dict() for msg in messages]

        payload = {
            "model": model,
            "messages": messages_dict,
            "temperature": temperature,
            **kwargs
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()

            choice = data["choices"][0]
            content = choice["message"]["content"]

            return LLMResponse(
                content=content,
                model=data.get("model", model),
                provider="openai_compatible",
                usage=data.get("usage", {}),
                finish_reason=choice.get("finish_reason"),
                raw_response=data
            )
        except httpx.HTTPStatusError as e:
            raise LLMProviderError(f"HTTP {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise LLMProviderError(f"Request failed: {str(e)}")

    async def chat_completion_stream(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        model = model or self.default_model
        messages_dict = [msg.to_dict() for msg in messages]

        payload = {
            "model": model,
            "messages": messages_dict,
            "temperature": temperature,
            "stream": True,
            **kwargs
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with self.client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        import json
                        data = json.loads(line[6:])
                        if "choices" in data:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                    except:
                        continue

    async def get_available_models(self) -> List[str]:
        try:
            response = await self.client.get("/models")
            response.raise_for_status()
            data = response.json()
            if "data" in data:
                return [model["id"] for model in data["data"]]
            return []
        except:
            return [self.default_model]

    async def close(self) -> None:
        await self.client.aclose()
