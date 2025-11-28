"""
OpenRouter implementation of the LLMClientBackend interface.

This file handles communication with the external OpenRouter API.
"""
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from ..config import OPENROUTER_API_KEY, OPENROUTER_API_URL, API_TIMEOUT_SECONDS, LLM_MAX_OUTPUT_TOKENS
from .base import LLMClientBackend

# We only import the base timeout; the specific title timeout is handled by the caller (LLM Council)
# The client will use API_TIMEOUT_SECONDS as its default timeout.

class OpenRouterClient(LLMClientBackend):
    """
    A client that communicates with the OpenRouter API endpoint.
    """
    def __init__(self):
        # httpx client initialization
        pass # No complex setup needed for OpenRouter

    async def query_model(
        self,
        model: str,
        messages: List[Dict[str, str]],
        timeout: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """Queries a single model endpoint for chat completion."""
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": LLM_MAX_OUTPUT_TOKENS,
        }

        # Use the provided timeout, or the default from configuration
        actual_timeout = timeout if timeout is not None else API_TIMEOUT_SECONDS

        try:
            async with httpx.AsyncClient(timeout=actual_timeout) as client:
                response = await client.post(
                    OPENROUTER_API_URL,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    # Generic error handling (as seen in original openrouter.py)
                    print(f"API Error {response.status_code} querying model {model}: {response.text[:200]}")
                    return None
                
                response.raise_for_status()

                data = response.json()
                message = data['choices'][0]['message']

                return {
                    'content': message.get('content'),
                    'reasoning_details': message.get('reasoning_details')
                }

        except httpx.TimeoutException as e:
            print(f"Timeout querying model {model} after {actual_timeout}s: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP error querying model {model}: {e.response.status_code} - {e.response.text[:200]}")
            return None
        except Exception as e:
            print(f"Unexpected error querying model {model}: {type(e).__name__} - {e}")
            return None


    async def query_models_parallel(
        self,
        models: List[str],
        messages: List[Dict[str, str]]
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """Queries multiple models simultaneously for council operations."""
        
        # Create tasks for all models using the single query_model method
        tasks = [self.query_model(model, messages) for model in models]

        # Wait for all to complete
        responses = await asyncio.gather(*tasks)

        # Map models to their responses
        return {model: response for model, response in zip(models, responses)}
