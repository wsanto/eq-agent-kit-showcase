"""
0G Labs On-Chain Inference Provider

Integrates with 0G Labs' decentralized compute network for on-chain AI inference.
Documentation: https://docs.0g.ai/developer-hub/building-on-0g/compute-network/sdk
"""

import httpx
from typing import Dict, Any, List, Optional, AsyncIterator
from loguru import logger

from .base import LLMProvider, LLMMessage, LLMResponse, LLMProviderError


class ZeroGProvider(LLMProvider):
    """
    0G Labs on-chain inference provider.
    
    Supports decentralized AI inference through 0G's compute network.
    Models run on a distributed network of nodes with blockchain verification.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.0g.ai/v1",
        default_model: str = "0g/llama-3-8b",
        network: str = "mainnet",
        timeout: float = 120.0,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize 0G Labs provider.

        Args:
            api_key: 0G API key
            base_url: 0G API endpoint
            default_model: Default model on 0G network
            network: Network to use ("mainnet" or "testnet")
            timeout: Request timeout (on-chain is slower)
            config: Additional configuration
        """
        super().__init__(api_key, base_url, default_model, config)
        self.network = network
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers=self._get_headers()
        )
        logger.info(f"Initialized 0G Labs provider on {network}")

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
            "X-Network": self.network
        }
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
        verify_on_chain: bool = True,
        **kwargs
    ) -> LLMResponse:
        """
        Generate chat completion on 0G network.

        Args:
            messages: List of conversation messages
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream
            verify_on_chain: Whether to verify computation on-chain
            **kwargs: Additional parameters

        Returns:
            LLMResponse with on-chain verification metadata
        """
        model = model or self.default_model
        messages_dict = [msg.to_dict() for msg in messages]

        # Build payload with 0G-specific parameters
        payload = {
            "model": model,
            "messages": messages_dict,
            "temperature": temperature,
            "verify_on_chain": verify_on_chain,
            "network": self.network,
            **kwargs
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            logger.debug(f"Requesting on-chain inference from 0G: model={model}")
            response = await self.client.post("/inference/chat", json=payload)
            response.raise_for_status()
            data = response.json()

            # Extract response with on-chain metadata
            content = data.get("content") or data.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Extract on-chain verification data
            metadata = {
                "on_chain": True,
                "network": self.network,
                "tx_hash": data.get("tx_hash"),
                "block_number": data.get("block_number"),
                "compute_nodes": data.get("compute_nodes", []),
                "verification_status": data.get("verification_status"),
            }

            return LLMResponse(
                content=content,
                model=data.get("model", model),
                provider="zerog",
                usage=data.get("usage", {}),
                finish_reason=data.get("finish_reason"),
                raw_response=data,
                metadata=metadata
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"0G HTTP error: {e.response.status_code}")
            raise LLMProviderError(f"0G HTTP {e.response.status_code}: {e.response.text}")
        except Exception as e:
            logger.error(f"0G inference error: {e}")
            raise LLMProviderError(f"0G request failed: {str(e)}")

    async def chat_completion_stream(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate streaming chat completion on 0G network.

        Args:
            messages: List of conversation messages
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Yields:
            Content chunks from on-chain inference
        """
        model = model or self.default_model
        messages_dict = [msg.to_dict() for msg in messages]

        payload = {
            "model": model,
            "messages": messages_dict,
            "temperature": temperature,
            "stream": True,
            "network": self.network,
            **kwargs
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            async with self.client.stream("POST", "/inference/chat", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            import json
                            data = json.loads(line[6:])
                            if "content" in data:
                                yield data["content"]
                            elif "delta" in data:
                                yield data["delta"]
                        except:
                            continue
        except Exception as e:
            logger.error(f"0G streaming error: {e}")
            raise LLMProviderError(f"0G streaming failed: {str(e)}")

    async def get_available_models(self) -> List[str]:
        """
        Get list of available models on 0G network.

        Returns:
            List of model identifiers available on-chain
        """
        try:
            response = await self.client.get(f"/models?network={self.network}")
            response.raise_for_status()
            data = response.json()

            if "models" in data:
                return [model["id"] for model in data["models"]]
            return []

        except Exception as e:
            logger.warning(f"Failed to fetch 0G models: {e}")
            return [self.default_model]

    async def verify_computation(self, tx_hash: str) -> Dict[str, Any]:
        """
        Verify on-chain computation.

        Args:
            tx_hash: Transaction hash from inference

        Returns:
            Verification result with proof details
        """
        try:
            response = await self.client.get(f"/verify/{tx_hash}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            raise LLMProviderError(f"Could not verify computation: {str(e)}")

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
        logger.debug("Closed 0G Labs provider")
