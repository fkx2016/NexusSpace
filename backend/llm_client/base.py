"""
Abstract Base Class (ABC) for all LLM Client Backends.

This interface ensures that the application's core logic (the LLM Council)
is decoupled from the underlying LLM provider (OpenRouter, local Ollama, etc.).
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LLMClientBackend(ABC):
    """
    Defines the contract for querying an LLM provider endpoint.
    All concrete implementations (OpenRouter, Ollama, etc.) must adhere to this.
    """

    @abstractmethod
    async def query_model(
        self,
        model: str,
        messages: List[Dict[str, str]],
        timeout: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Queries a single model endpoint for chat completion.

        Returns:
            A dictionary containing the response content and details, or None on failure.
        """
        pass

    @abstractmethod
    async def query_models_parallel(
        self,
        models: List[str],
        messages: List[Dict[str, str]]
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Queries multiple models simultaneously for council operations.
        """
        pass
