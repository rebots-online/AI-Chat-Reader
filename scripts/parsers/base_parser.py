# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.
"""
Base parser class for chat archive conversion.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid


@dataclass
class Message:
    """Represents a single message in a conversation."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: Optional[datetime] = None
    uuid: Optional[str] = None


@dataclass
class Conversation:
    """Represents a complete conversation."""
    id: str
    title: str
    source: str  # 'openai' or 'anthropic'
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[Message] = None
    uuid: Optional[str] = None
    
    def __post_init__(self):
        if self.messages is None:
            self.messages = []
        if self.uuid is None:
            self.uuid = str(uuid.uuid4())


class BaseParser(ABC):
    """Abstract base class for chat archive parsers."""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
    
    @abstractmethod
    def parse_file(self, file_path: str) -> List[Conversation]:
        """
        Parse a JSON file and return a list of conversations.
        
        Args:
            file_path: Path to the JSON file to parse
            
        Returns:
            List of Conversation objects
        """
        pass
    
    @abstractmethod
    def _parse_conversation(self, conv_data: Dict[str, Any]) -> Conversation:
        """
        Parse a single conversation from the JSON data.
        
        Args:
            conv_data: Dictionary containing conversation data
            
        Returns:
            Conversation object
        """
        pass
    
    def _clean_content(self, content: str) -> str:
        """
        Clean and normalize message content.
        
        Args:
            content: Raw message content
            
        Returns:
            Cleaned content string
        """
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = content.strip()
        
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        return content
    
    def _parse_timestamp(self, timestamp_data: Any) -> Optional[datetime]:
        """
        Parse timestamp from various formats.
        
        Args:
            timestamp_data: Timestamp in various formats (ISO string, Unix timestamp, etc.)
            
        Returns:
            datetime object or None if parsing fails
        """
        if not timestamp_data:
            return None
        
        try:
            # Handle Unix timestamp (float/int)
            if isinstance(timestamp_data, (int, float)):
                dt = datetime.fromtimestamp(timestamp_data)
                # Make timezone-naive for consistency
                return dt.replace(tzinfo=None)
            
            # Handle ISO format string
            if isinstance(timestamp_data, str):
                # Remove 'Z' and replace with timezone info
                if timestamp_data.endswith('Z'):
                    timestamp_data = timestamp_data.replace('Z', '+00:00')
                dt = datetime.fromisoformat(timestamp_data)
                # Make timezone-naive for consistency
                return dt.replace(tzinfo=None)
                
        except (ValueError, TypeError, OSError):
            pass
        
        return None
    
    def _generate_safe_filename(self, title: str, created_at: datetime, conv_id: str) -> str:
        """
        Generate a safe filename for the conversation HTML file.
        
        Args:
            title: Conversation title
            created_at: Creation timestamp
            conv_id: Conversation ID
            
        Returns:
            Safe filename string
        """
        # Clean title for filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
        
        # Format date
        date_str = created_at.strftime('%Y%m%d_%H%M%S') if created_at else 'unknown'
        
        # Use first 8 chars of conv_id as suffix
        id_suffix = conv_id[:8] if conv_id else 'unknown'
        
        return f"{safe_title}_{date_str}_{id_suffix}.html"