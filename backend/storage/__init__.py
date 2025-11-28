"""
Storage Manager: Selects and initializes the correct Storage Backend.

This module acts as the single point of contact for the rest of the application
to interact with storage (Factory/Dependency Injection Pattern).
"""
import sys
from typing import Optional, Dict, Any, List
from ..config import STORAGE_BACKEND
from .base import StorageBackend

# Import concrete implementations (these must exist)
from .filesystem import FilesystemStorage
from .database import DatabaseStorage

# --- Storage Factory ---
def get_storage_backend() -> StorageBackend:
    """
    Returns the initialized StorageBackend based on environment configuration.
    """
    if STORAGE_BACKEND == "filesystem":
        print("INFO: Initializing Filesystem Storage Backend...")
        return FilesystemStorage()
    
    elif STORAGE_BACKEND == "database":
        print("INFO: Initializing Database Storage Backend (for scaling)...")
        # NOTE: If we switch to PostgreSQL later, the initialization logic
        # inside DatabaseStorage will need to be updated to connect remotely.
        return DatabaseStorage()
    
    else:
        # This error should ideally be caught by config validation, but included for safety
        print(f"FATAL: Unknown STORAGE_BACKEND: {STORAGE_BACKEND}", file=sys.stderr)
        sys.exit(1)

# Initialize the global storage manager instance
# This is the single dependency injected into the rest of the application
STORAGE_MANAGER = get_storage_backend()


# --- Public API for the rest of the application ---
# The rest of the app imports these functions/methods, achieving clean abstraction.

def get_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a conversation record."""
    return STORAGE_MANAGER.get_conversation(conversation_id)

def save_conversation(conversation: Dict[str, Any]) -> None:
    """Persists changes made to an existing conversation record."""
    STORAGE_MANAGER.save_conversation(conversation)

def create_conversation(conversation_id: str) -> Dict[str, Any]:
    """Initializes a new conversation record."""
    return STORAGE_MANAGER.create_conversation(conversation_id)

def get_all_conversation_ids() -> List[str]:
    """Retrieves a list of all existing conversation IDs."""
    return STORAGE_MANAGER.get_all_conversation_ids()
