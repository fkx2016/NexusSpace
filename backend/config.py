"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# PRODUCTION MODELS (Commenting out for development cost savings)
# COUNCIL_MODELS = [
#     "openai/gpt-5.1",
#     "google/gemini-3-pro-preview",
#     "anthropic/claude-sonnet-4.5",
#     "x-ai/grok-4",
# ]
# CHAIRMAN_MODEL = "google/gemini-3-pro-preview"

# DEVELOPMENT MODELS (Low cost for testing)
COUNCIL_MODELS = [
    "anthropic/claude-3-haiku",
    "google/gemini-2.5-flash",
    "meta-llama/llama-3-70b-instruct",
]
CHAIRMAN_MODEL = "google/gemini-2.5-flash"

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Data directory for conversation storage
DATA_DIR = "data/conversations"

# File reader configuration
MAX_FILES_TO_READ = 500
MAX_CODEBASE_SIZE_MB = 10
SUPPORTED_EXTENSIONS = [
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.cpp', '.c', '.h', 
    '.cs', '.rb', '.php', '.swift', '.kt', '.md', '.txt', '.json', '.yaml', '.yml', 
    '.toml', '.xml', '.html', '.css', '.scss', '.sql', '.sh', '.bash', '.env.example'
]
