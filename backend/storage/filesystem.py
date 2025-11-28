"""
Filesystem implementation of the StorageBackend interface.

This implementation uses the local file system for conversation storage,
suitable for single-instance, local development environments.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..config import DATA_DIR
from .base import StorageBackend

# Ensure the data directory exists
Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

class FilesystemStorage(StorageBackend):
    """
    A storage backend that uses the local file system to store JSON conversations.
    """
    def __init__(self):
        # We explicitly ensure the DATA_DIR is ready on initialization
        self.data_path = Path(DATA_DIR)
        self.data_path.mkdir(parents=True, exist_ok=True)

    def _get_conversation_path(self, conversation_id: str) -> Path:
        """Helper to construct the full file path for a conversation ID."""
        return self.data_path / f"{conversation_id}.json"

    def create_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Initializes a new conversation record."""
        # This implementation requires the 'id' field in the initial data
        initial_data = {
            "id": conversation_id,
            "created_at": str(datetime.now()),
            "turns": [],
            "metadata": {}
        }
        self.save_conversation(initial_data)
        return initial_data

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a conversation record by ID."""
        path = self._get_conversation_path(conversation_id)
        if not path.exists():
            return None
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON for conversation ID: {conversation_id}")
            return None

    def save_conversation(self, conversation: Dict[str, Any]) -> None:
        """Persists changes made to an existing conversation record."""
        if 'id' not in conversation:
            raise ValueError("Conversation dictionary must contain an 'id' field to be saved.")

        path = self._get_conversation_path(conversation['id'])
        with open(path, 'w') as f:
            json.dump(conversation, f, indent=2)

    def get_all_conversation_ids(self) -> List[str]:
        """Retrieves a list of all existing conversation IDs."""
        ids = []
        for file in self.data_path.glob("*.json"):
            # Strip the .json extension to get the ID
            ids.append(file.stem)
        return ids
