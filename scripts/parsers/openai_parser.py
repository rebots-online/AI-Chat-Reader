# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.
"""
Parser for OpenAI/ChatGPT chat archive JSON files.
"""
import json
import logging
from typing import List, Dict, Any
from .base_parser import BaseParser, Conversation, Message

logger = logging.getLogger(__name__)


class OpenAIParser(BaseParser):
    """Parser for OpenAI/ChatGPT conversation exports."""
    
    def __init__(self):
        super().__init__("openai")
    
    def parse_file(self, file_path: str) -> List[Conversation]:
        """
        Parse an OpenAI JSON file and return conversations.
        
        Args:
            file_path: Path to the OpenAI JSON file
            
        Returns:
            List of Conversation objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            conversations = []
            for conv_data in data:
                try:
                    conversation = self._parse_conversation(conv_data)
                    if conversation and conversation.messages:
                        conversations.append(conversation)
                except (KeyError, ValueError, AttributeError, TypeError) as e:
                    conv_title = conv_data.get('title', 'unknown') if isinstance(conv_data, dict) else 'invalid'
                    logger.warning("Failed to parse conversation '%s': %s", conv_title, e)
                    continue

            return conversations

        except (FileNotFoundError, PermissionError) as e:
            logger.error("Cannot access OpenAI file '%s': %s", file_path, e)
            return []
        except (json.JSONDecodeError, ValueError) as e:
            logger.error("Invalid JSON in OpenAI file '%s': %s", file_path, e)
            return []
        except Exception as e:
            logger.error("Unexpected error reading OpenAI file '%s': %s", file_path, e)
            return []
    
    def _parse_conversation(self, conv_data: Dict[str, Any]) -> Conversation:
        """
        Parse a single OpenAI conversation.
        
        Args:
            conv_data: Dictionary containing conversation data
            
        Returns:
            Conversation object
        """
        # Extract basic conversation info
        title = conv_data.get('title', 'Untitled Conversation')
        
        # Parse timestamps
        created_at = self._parse_timestamp(conv_data.get('create_time'))
        updated_at = self._parse_timestamp(conv_data.get('update_time'))
        
        # Generate ID from title and timestamp
        conv_id = f"openai_{hash(title + str(created_at))}"
        
        # Create conversation object
        conversation = Conversation(
            id=conv_id,
            title=title,
            source=self.source_name,
            created_at=created_at,
            updated_at=updated_at
        )
        
        # Parse messages from mapping
        mapping = conv_data.get('mapping', {})
        messages = self._extract_messages_from_mapping(mapping)
        
        # Sort messages by creation time
        messages.sort(key=lambda m: m.timestamp or conversation.created_at or 0)
        
        conversation.messages = messages
        
        return conversation
    
    def _extract_messages_from_mapping(self, mapping: Dict[str, Any]) -> List[Message]:
        """
        Extract messages from OpenAI's mapping structure.
        
        Args:
            mapping: OpenAI mapping dictionary
            
        Returns:
            List of Message objects
        """
        messages = []
        
        for node_id, node in mapping.items():
            # Skip null nodes or nodes without messages
            if not node or node.get("message") is None:
                continue
            
            message_data = node.get("message", {})
            message = self._parse_message(message_data)
            if message:
                messages.append(message)
        
        return messages
    
    def _parse_message(self, msg_data: Dict[str, Any]) -> Message:
        """
        Parse a single message from OpenAI format.
        
        Args:
            msg_data: Dictionary containing message data
            
        Returns:
            Message object or None if parsing fails
        """
        try:
            # Skip hidden messages
            metadata = msg_data.get("metadata", {})
            if metadata.get("is_visually_hidden_from_conversation", False):
                return None
            
            # Extract author information
            author = msg_data.get("author", {}) or {}
            role = author.get("role", "unknown")
            
            # Normalize role names
            if role == "assistant":
                role = "assistant"
            elif role == "user":
                role = "user"
            elif role == "system":
                role = "system"
            elif role == "tool":
                role = "system"  # Treat tool messages as system
            else:
                role = "system"
            
            # Extract content
            content_obj = msg_data.get("content", {}) or {}
            content = self._extract_content(content_obj)
            
            if not content:
                return None
            
            # Parse timestamp
            timestamp = self._parse_timestamp(msg_data.get("create_time"))
            
            # Get message ID
            msg_id = msg_data.get("id", "")
            
            return Message(
                role=role,
                content=content,
                timestamp=timestamp,
                uuid=msg_id
            )
            
        except (KeyError, ValueError, AttributeError, TypeError) as e:
            logger.debug("Failed to parse OpenAI message: %s", e)
            return None
    
    def _extract_content(self, content_obj: Dict[str, Any]) -> str:
        """
        Extract content from OpenAI's content object.
        
        Args:
            content_obj: OpenAI content dictionary
            
        Returns:
            Cleaned content string
        """
        content_type = content_obj.get("content_type", "text")
        
        if content_type == "text":
            parts = content_obj.get("parts", []) or []
        elif content_type == "user_editable_context":
            # Handle user instructions or profile information
            user_instructions = content_obj.get("user_instructions", "")
            user_profile = content_obj.get("user_profile", "")
            parts = [f"{user_profile}\n{user_instructions}"] if user_profile or user_instructions else []
        else:
            # Handle other content types
            parts = content_obj.get("parts", []) or []
        
        # Process content parts
        processed_parts = []
        for part in parts:
            if part:  # Skip empty parts
                if isinstance(part, str):
                    processed_parts.append(part)
                elif isinstance(part, dict):
                    # Handle dictionary content types
                    if part.get('type') == 'text':
                        if 'text' in part:
                            processed_parts.append(part['text'])
                    else:
                        # For other dict types, use a reasonable representation
                        processed_parts.append(f"[Content: {str(part)}]")
                else:
                    # For any other type, convert to string
                    processed_parts.append(str(part))
        
        content = "\n".join(processed_parts).strip()
        return self._clean_content(content)