import time
import uuid
import json
from utils.logger import setup_logger

class MemoryStore:
    """
    Shared memory store for maintaining context across agents.
    """
    
    def __init__(self, storage_type="in_memory"):
        """
        Initialize the memory store.
        
        Args:
            storage_type (str): The type of storage to use (in_memory, sqlite, redis)
        """
        self.storage_type = storage_type
        self.logger = setup_logger(name="memory_store")
        
        # In-memory storage
        self.memory = {}
        self.conversations = {}
        
        # Initialize storage
        if storage_type == "in_memory":
            # Already initialized with self.memory
            pass
        elif storage_type == "sqlite":
            # In a real implementation, we would initialize SQLite here
            self.logger.warning("SQLite storage not implemented, falling back to in-memory")
        elif storage_type == "redis":
            # In a real implementation, we would initialize Redis here
            self.logger.warning("Redis storage not implemented, falling back to in-memory")
        else:
            self.logger.warning(f"Unknown storage type: {storage_type}, falling back to in-memory")
    
    def create_conversation(self):
        """
        Create a new conversation and return its ID.
        
        Returns:
            str: The conversation ID
        """
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = []
        self.logger.info(f"Created new conversation with ID: {conversation_id}")
        return conversation_id
    
    def add_entry(self, entry):
        """
        Add an entry to memory.
        
        Args:
            entry (dict): The entry to add
        """
        # Add timestamp if not present
        if "timestamp" not in entry:
            entry["timestamp"] = time.time()
        
        # Get conversation ID
        conversation_id = entry.get("conversation_id")
        if not conversation_id:
            self.logger.warning("No conversation ID provided, entry will not be stored")
            return
        
        # Create conversation if it doesn't exist
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        # Add entry to conversation
        self.conversations[conversation_id].append(entry)
        self.logger.info(f"Added entry to conversation {conversation_id}")
    
    def get_conversation(self, conversation_id):
        """
        Get all entries for a conversation.
        
        Args:
            conversation_id (str): The conversation ID
            
        Returns:
            list: The conversation entries
        """
        if conversation_id not in self.conversations:
            self.logger.warning(f"Conversation {conversation_id} not found")
            return []
        
        return self.conversations[conversation_id]
    
    def load_conversation(self, conversation_id):
        """
        Load a conversation from storage.
        
        Args:
            conversation_id (str): The conversation ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.storage_type == "in_memory":
            # For in-memory storage, the conversation is already loaded
            return conversation_id in self.conversations
        
        # In a real implementation, we would load from SQLite or Redis here
        self.logger.warning(f"Loading from {self.storage_type} not implemented")
        return False
    
    def save_conversation(self, conversation_id):
        """
        Save a conversation to persistent storage.
        
        Args:
            conversation_id (str): The conversation ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if conversation_id not in self.conversations:
            self.logger.warning(f"Conversation {conversation_id} not found")
            return False
        
        if self.storage_type == "in_memory":
            # For in-memory storage, we can export to JSON
            try:
                filename = f"conversation_{conversation_id}.json"
                with open(filename, "w") as f:
                    json.dump(self.conversations[conversation_id], f, indent=2)
                self.logger.info(f"Saved conversation {conversation_id} to {filename}")
                return True
            except Exception as e:
                self.logger.error(f"Error saving conversation: {str(e)}")
                return False
        
        # In a real implementation, we would save to SQLite or Redis here
        self.logger.warning(f"Saving to {self.storage_type} not implemented")
        return False
    
    def get_last_entry(self, conversation_id):
        """
        Get the last entry for a conversation.
        
        Args:
            conversation_id (str): The conversation ID
            
        Returns:
            dict: The last entry, or None if not found
        """
        if conversation_id not in self.conversations or not self.conversations[conversation_id]:
            return None
        
        return self.conversations[conversation_id][-1]
    
    def search_entries(self, conversation_id, query):
        """
        Search for entries in a conversation.
        
        Args:
            conversation_id (str): The conversation ID
            query (dict): The search query
            
        Returns:
            list: Matching entries
        """
        if conversation_id not in self.conversations:
            return []
        
        # Simple search implementation
        results = []
        for entry in self.conversations[conversation_id]:
            match = True
            for key, value in query.items():
                if key not in entry or entry[key] != value:
                    match = False
                    break
            if match:
                results.append(entry)
        
        return results
    
    def clear_conversation(self, conversation_id):
        """
        Clear a conversation from memory.
        
        Args:
            conversation_id (str): The conversation ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            self.logger.info(f"Cleared conversation {conversation_id}")
            return True
        
        self.logger.warning(f"Conversation {conversation_id} not found")
        return False