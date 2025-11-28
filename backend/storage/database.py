"""
SQLite/Database implementation of the StorageBackend interface.

This implementation stores conversations in a single database table,
suitable for stateless, horizontally scalable deployments (when connected
to an external database).
"""
import json
import sqlite3
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..config import DATA_DIR # DATA_DIR is reused here for the SQLite file path
from .base import StorageBackend

# Define the path to the SQLite database file
DB_PATH = Path(DATA_DIR) / "nexusspace.db"

class DatabaseStorage(StorageBackend):
    """
    A storage backend that uses an SQL database (SQLite/PostgreSQL compatible schema).
    """
    def __init__(self):
        # Ensure the directory for the DB file exists
        Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
        self.conn = self._get_connection()
        self._initialize_db()

    def _get_connection(self):
        """Returns a database connection object."""
        # In a production setting, this would connect to a remote PostgreSQL/MySQL
        # check_same_thread=False is needed for SQLite when used with FastAPI's threadpool
        return sqlite3.connect(DB_PATH, check_same_thread=False)

    def _initialize_db(self):
        """Initializes the conversations table if it doesn't exist."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                data TEXT NOT NULL
            );
        """)
        self.conn.commit()

        # New table for storing application settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT
            );
        """)
        # Also add a default setting entry (e.g., for LLM Provider) if not already present
        cursor.execute(
            "INSERT OR IGNORE INTO user_settings (setting_key, setting_value) VALUES (?, ?)",
            ('llm_provider', 'openrouter')
        )
        self.conn.commit()

    def create_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Initializes a new conversation record."""
        initial_data = {
            "id": conversation_id,
            "created_at": str(datetime.now()),
            "turns": [],
            "metadata": {}
        }
        data_json = json.dumps(initial_data)

        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (id, created_at, data) VALUES (?, ?, ?)",
            (conversation_id, initial_data['created_at'], data_json)
        )
        self.conn.commit()
        return initial_data

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a conversation record by ID."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT data FROM conversations WHERE id = ?",
            (conversation_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return None

        # The data is stored as a JSON string in the 'data' column
        return json.loads(row[0])

    def save_conversation(self, conversation: Dict[str, Any]) -> None:
        """Persists changes made to an existing conversation record."""
        if 'id' not in conversation:
            raise ValueError("Conversation dictionary must contain an 'id' field to be saved.")

        data_json = json.dumps(conversation)

        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE conversations SET data = ? WHERE id = ?",
            (data_json, conversation['id'])
        )
        self.conn.commit()

        if cursor.rowcount == 0:
            # Handle case where record might not exist yet (though create_conversation handles initial insert)
            print(f"Warning: Attempted to update non-existent conversation ID: {conversation['id']}")


    def get_all_conversation_ids(self) -> List[str]:
        """Retrieves a list of all existing conversation IDs."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM conversations")
        # Fetch all results and flatten the list of tuples
        return [row[0] for row in cursor.fetchall()]
