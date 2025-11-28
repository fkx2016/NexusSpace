"""
Ollama/Local AI implementation of the LLMClientBackend interface.

This file handles communication with a local or self-hosted LLM endpoint
(like Ollama, or a custom VLLM/TGI server) that supports the OpenAI API spec.
"""
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from ..config import OLLAMA_API_URL, API_TIMEOUT_SECONDS
from .base import LLMClientBackend

class OllamaClient(LLMClientBackend):
    """
    A client that communicates with a local/internal Ollama or VLLM endpoint.
    """
    def __init__(self):
        # We assume the local API does not require an API key
        # httpx client initialization
        pass 

    async def query_model(
        self,
        model: str,
        messages: List[Dict[str, str]],
        timeout: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """Queries a single model endpoint for chat completion."""
        
        headers = {
            "Content-Type": "application/json",
        }

        # Ollama/VLLM uses the same payload structure as OpenAI/OpenRouter
        payload = {
            "model": model,
            "messages": messages,
        }

        actual_timeout = timeout if timeout is not None else API_TIMEOUT_SECONDS

        try:
            # Note: OLLAMA_API_URL is the full endpoint (e.g., http://localhost:11434/v1/chat/completions)
            async with httpx.AsyncClient(timeout=actual_timeout) as client:
                response = await client.post(
                    OLLAMA_API_URL, 
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    print(f"Local API Error {response.status_code} querying model {model}: {response.text[:200]}")
                    return None
                
                response.raise_for_status()

                data = response.json()
                message = data['choices'][0]['message']

                return {
                    'content': message.get('content'),
                    # Ollama/VLLM may not return 'reasoning_details', so we stick to the required content
                }

        except httpx.TimeoutException as e:
            print(f"Local Timeout querying model {model} after {actual_timeout}s: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"Local HTTP error querying model {model}: {e.response.status_code} - {e.response.text[:200]}")
            return None
        except Exception as e:
            print(f"Unexpected error querying local model {model}: {type(e).__name__} - {e}")
            return None


    async def query_models_parallel(
        self,
        models: List[str],
        messages: List[Dict[str, str]]
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Queries multiple models simultaneously for council operations.
        Note: While Ollama is usually single-instance, we maintain this parallel
        structure for consistency and future-proofing against multi-model Ollama servers.
        """
        
        tasks = [self.query_model(model, messages) for model in models]
        responses = await asyncio.gather(*tasks)

        return {model: response for model, response in zip(models, responses)}
