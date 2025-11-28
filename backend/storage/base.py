"""
Abstract Base Class (ABC) for all Storage Backends.

This interface ensures that the application's core logic (e.g., loading conversations)
is decoupled from the underlying storage technology (filesystem, database, etc.).
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class StorageBackend(ABC):
    """
    Defines the contract for storing and retrieving NexusSpace conversations.
    """

    @abstractmethod
    def create_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Initializes a new conversation record.
        Must return the initial conversation dictionary.
        """
        pass

    @abstractmethod
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a conversation record by ID.
        Returns the conversation dictionary or None if not found.
        """
        pass

    @abstractmethod
    def save_conversation(self, conversation: Dict[str, Any]) -> None:
        """
        Persists changes made to an existing conversation record.
        The conversation dictionary must contain the 'id' field.
        """
        pass

    @abstractmethod
    def get_all_conversation_ids(self) -> List[str]:
        """
        Retrieves a list of all existing conversation IDs.
        Used for the dashboard/history view.
        """
        pass
