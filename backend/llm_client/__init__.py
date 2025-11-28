"""
LLM Client Manager: Selects and initializes the correct LLM Client Backend.

This file acts as the single point of contact for the rest of the application
to interact with LLM services (Factory/Dependency Injection Pattern).
"""
import sys
from typing import Optional, Dict, Any, List
from ..config import LLM_PROVIDER
from .base import LLMClientBackend

# Import concrete implementations
from .openrouter import OpenRouterClient
from .ollama import OllamaClient


# --- Client Factory ---
def get_llm_client_backend() -> LLMClientBackend:
    """
    Returns the initialized LLMClientBackend based on environment configuration.
    """
    # Try to get provider from database settings first
    provider = LLM_PROVIDER # Default to env var
    try:
        # Import here to avoid circular imports at module level
        # backend.api.settings depends on backend.storage which depends on backend.config
        from ..api.settings import _get_setting_db
        db_provider = _get_setting_db("llm_provider")
        if db_provider:
            provider = db_provider
            print(f"INFO: Using LLM Provider from Database Settings: {provider}")
    except Exception as e:
        # Fallback to env var if DB access fails (e.g. during initial setup or if using filesystem storage)
        print(f"WARNING: Could not retrieve settings from DB ({e}). Using environment default.")
        pass

    if provider == "openrouter":
        print("INFO: Initializing OpenRouter Client Backend...")
        return OpenRouterClient()
    
    elif provider == "ollama":
        print("INFO: Initializing Ollama/Local AI Client Backend...")
        return OllamaClient()
    
    else:
        # Catch errors from unknown provider specified in environment
        print(f"FATAL: Unknown LLM_PROVIDER: {provider}", file=sys.stderr)
        sys.exit(1)

# Initialize the global client manager instance
LLM_CLIENT_MANAGER = get_llm_client_backend()

# --- Public API for the rest of the application ---

# Expose the methods of the selected backend for easy import by the Council.
query_model = LLM_CLIENT_MANAGER.query_model
query_models_parallel = LLM_CLIENT_MANAGER.query_models_parallel
