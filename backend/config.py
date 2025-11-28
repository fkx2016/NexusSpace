"""Configuration for the LLM Council.

This module loads all configuration from environment variables following
12-Factor App principles. All required variables are validated at startup.
"""

import os
import sys
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file (development only)
load_dotenv()


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""
    pass


def get_required_env(key: str) -> str:
    """Get a required environment variable or raise ConfigurationError."""
    value = os.getenv(key)
    if value is None or value.strip() == "":
        raise ConfigurationError(
            f"Missing required environment variable: {key}\n"
            f"Please set {key} in your .env file or environment."
        )
    return value.strip()


def get_optional_env(key: str, default: str) -> str:
    """Get an optional environment variable with a default value."""
    value = os.getenv(key)
    return value.strip() if value else default


def get_env_list(key: str, default: List[str]) -> List[str]:
    """Get a comma-separated list from environment variable."""
    value = os.getenv(key)
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def get_env_int(key: str, default: int) -> int:
    """Get an integer environment variable with a default value."""
    value = os.getenv(key)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        raise ConfigurationError(
            f"Invalid integer value for {key}: {value}"
        )


def get_env_float(key: str, default: float) -> float:
    """Get a float environment variable with a default value."""
    value = os.getenv(key)
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        raise ConfigurationError(
            f"Invalid float value for {key}: {value}"
        )


# ============================================================================
# REQUIRED CONFIGURATION
# ============================================================================

try:
    # OpenRouter API Configuration
    OPENROUTER_API_KEY = get_required_env("OPENROUTER_API_KEY")
    OPENROUTER_API_URL = get_optional_env(
        "OPENROUTER_API_URL",
        "https://openrouter.ai/api/v1/chat/completions"
    )
    OLLAMA_API_URL = get_optional_env(
        "OLLAMA_API_URL",
        "http://localhost:11434/v1/chat/completions"
    )

    LLM_PROVIDER = get_optional_env("LLM_PROVIDER", "openrouter")

    # LLM Model Configuration
    COUNCIL_MODELS = get_env_list(
        "COUNCIL_MODELS",
        [
            "anthropic/claude-3-haiku",
            "google/gemini-2.5-flash",
            "meta-llama/llama-3-70b-instruct",
        ]
    )
    CHAIRMAN_MODEL = get_optional_env(
        "CHAIRMAN_MODEL",
        "google/gemini-2.5-flash"
    )

    # Feature Flags
    RUN_STAGE_2 = os.getenv("RUN_STAGE_2", "true").lower() == "true"

    # Storage Configuration
    STORAGE_BACKEND = get_optional_env("STORAGE_BACKEND", "filesystem")
    DATA_DIR = get_optional_env("DATA_DIR", "data/conversations")
    
    # Temporary Storage Configuration (for cloning remote repos)
    TEMP_CLONE_DIR = get_optional_env("TEMP_CLONE_DIR", "temp_clones")

    # Server Configuration
    SERVER_HOST = get_optional_env("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = get_env_int("SERVER_PORT", 8001)

    # CORS Configuration
    CORS_ORIGINS = get_env_list(
        "CORS_ORIGINS",
        ["http://localhost:5173", "http://localhost:3000"]
    )

    # File Reader Configuration
    MAX_FILES_TO_READ = get_env_int("MAX_FILES_TO_READ", 500)
    MAX_CODEBASE_SIZE_MB = get_env_int("MAX_CODEBASE_SIZE_MB", 10)

    SUPPORTED_EXTENSIONS = get_env_list(
        "SUPPORTED_EXTENSIONS",
        [
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs',
            '.cpp', '.c', '.h', '.cs', '.rb', '.php', '.swift', '.kt',
            '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.xml',
            '.html', '.css', '.scss', '.sql', '.sh', '.bash', '.env.example'
        ]
    )

    # API Timeout Configuration
    API_TIMEOUT_SECONDS = get_env_float("API_TIMEOUT_SECONDS", 120.0)
    TITLE_GENERATION_TIMEOUT = get_env_float("TITLE_GENERATION_TIMEOUT", 30.0)

except ConfigurationError as e:
    print(f"\n❌ CONFIGURATION ERROR:\n{e}\n", file=sys.stderr)
    print("Please check your .env file or environment variables.\n", file=sys.stderr)
    sys.exit(1)


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_config():
    """Validate configuration values at startup."""
    errors = []

    # Validate STORAGE_BACKEND
    if STORAGE_BACKEND not in ["filesystem", "database"]:
        errors.append(
            f"Invalid STORAGE_BACKEND: {STORAGE_BACKEND}. "
            f"Must be 'filesystem' or 'database'."
        )

    # Validate LLM_PROVIDER
    if LLM_PROVIDER not in ["openrouter", "ollama"]:
        errors.append(
            f"Invalid LLM_PROVIDER: {LLM_PROVIDER}. "
            f"Must be 'openrouter' or 'ollama'."
        )

    # Validate model lists
    if not COUNCIL_MODELS:
        errors.append("COUNCIL_MODELS cannot be empty.")

    if not CHAIRMAN_MODEL:
        errors.append("CHAIRMAN_MODEL cannot be empty.")

    # Validate numeric ranges
    if MAX_FILES_TO_READ <= 0:
        errors.append(f"MAX_FILES_TO_READ must be positive, got {MAX_FILES_TO_READ}")

    if MAX_CODEBASE_SIZE_MB <= 0:
        errors.append(f"MAX_CODEBASE_SIZE_MB must be positive, got {MAX_CODEBASE_SIZE_MB}")

    if API_TIMEOUT_SECONDS <= 0:
        errors.append(f"API_TIMEOUT_SECONDS must be positive, got {API_TIMEOUT_SECONDS}")

    if errors:
        print("\n❌ CONFIGURATION VALIDATION ERRORS:\n", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print("", file=sys.stderr)
        sys.exit(1)


# Run validation on import
validate_config()


# ============================================================================
# CONFIGURATION SUMMARY (for debugging)
# ============================================================================

def print_config_summary():
    """Print configuration summary (for debugging/startup logs)."""
    print("\n" + "="*60)
    print("NexusSpace Configuration Summary")
    print("="*60)
    print(f"OpenRouter API URL: {OPENROUTER_API_URL}")
    print(f"Ollama API URL: {OLLAMA_API_URL}")
    print(f"OpenRouter API Key: {'*' * 20} (hidden)")
    print(f"LLM Provider: {LLM_PROVIDER}")
    print(f"Council Models: {', '.join(COUNCIL_MODELS)}")
    print(f"Chairman Model: {CHAIRMAN_MODEL}")
    print(f"Storage Backend: {STORAGE_BACKEND}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Server: {SERVER_HOST}:{SERVER_PORT}")
    print(f"CORS Origins: {', '.join(CORS_ORIGINS)}")
    print(f"Max Files to Read: {MAX_FILES_TO_READ}")
    print(f"Max Codebase Size: {MAX_CODEBASE_SIZE_MB} MB")
    print(f"API Timeout: {API_TIMEOUT_SECONDS}s")
    print("="*60 + "\n")


# Optionally print config on startup (set DEBUG_CONFIG=1 to enable)
if os.getenv("DEBUG_CONFIG") == "1":
    print_config_summary()
