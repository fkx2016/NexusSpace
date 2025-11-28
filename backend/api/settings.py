"""FastAPI router for handling user settings (LLM Provider, etc.)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from backend.storage.__init__ import STORAGE_MANAGER # Import the Manager

router = APIRouter()

# Pydantic models for request/response
class Setting(BaseModel):
    setting_key: str
    setting_value: str

class SettingsUpdate(BaseModel):
    settings: Dict[str, str]

# --- Database Access Helpers (Simplified) ---
# NOTE: These use raw SQL access via the Storage Manager's connection.
# The actual implementation should be in a service layer, but we place it here
# for simplicity during feature implementation.

def _get_setting_db(key: str) -> Optional[str]:
    """Retrieves a setting value from the database."""
    # Check if the storage manager supports direct connection access (DatabaseStorage)
    if not hasattr(STORAGE_MANAGER, '_get_connection'):
        # Fallback for FilesystemStorage or other backends without DB connection
        # In a real app, we might want to implement settings storage for filesystem too,
        # but for now we'll return None to trigger environment variable fallback.
        return None

    conn = STORAGE_MANAGER._get_connection() # Access connection for SQL
    cursor = conn.cursor()
    cursor.execute("SELECT setting_value FROM user_settings WHERE setting_key = ?", (key,))
    row = cursor.fetchone()
    return row[0] if row else None

def _set_setting_db(key: str, value: str) -> None:
    """Inserts or updates a setting value in the database."""
    if not hasattr(STORAGE_MANAGER, '_get_connection'):
        # Fallback/Error for non-DB backends
        print(f"WARNING: Cannot save setting {key}={value} because current storage backend does not support DB access.")
        return

    conn = STORAGE_MANAGER._get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO user_settings (setting_key, setting_value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()


# --- API Endpoints ---

@router.get("/settings", response_model=Dict[str, str])
async def get_all_settings():
    """Fetch all user-configurable settings."""
    # For simplicity, we only expose the LLM Provider setting initially
    llm_provider = _get_setting_db('llm_provider')
    if not llm_provider:
        # Fallback to the environment default if database is empty
        from backend.config import LLM_PROVIDER as ENV_LLM_PROVIDER
        llm_provider = ENV_LLM_PROVIDER

    return {"llm_provider": llm_provider}

@router.post("/settings")
async def update_settings(update: SettingsUpdate):
    """Update user-configurable settings."""
    for key, value in update.settings.items():
        if key == 'llm_provider':
            _set_setting_db(key, value)
        else:
            # Reject unsupported settings
            raise HTTPException(status_code=400, detail=f"Unsupported setting key: {key}")
    return {"message": "Settings updated successfully"}
