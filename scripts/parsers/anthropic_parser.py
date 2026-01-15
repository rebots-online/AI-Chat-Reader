# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.
"""
Parser for Anthropic/Claude chat archive JSON files.
"""
import json
import logging
from typing import List, Dict, Any
from .base_parser import BaseParser, Conversation, Message

logger = logging.getLogger(__name__)


class AnthropicParser(BaseParser):
    """Parser for Anthropic/Claude conversation exports."""
    
    def __init__(self):
        super().__init__("anthropic")
    
    def parse_file(self, file_path: str) -> List[Conversation]:
        """
        Parse an Anthropic JSON file and return conversations.
        
        Args:
            file_path: Path to the Anthropic JSON file
            
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
                    conv_uuid = conv_data.get('uuid', 'unknown') if isinstance(conv_data, dict) else 'invalid'
                    logger.warning("Failed to parse conversation '%s': %s", conv_uuid, e)
                    continue

            return conversations

        except (FileNotFoundError, PermissionError) as e:
            logger.error("Cannot access Anthropic file '%s': %s", file_path, e)
            return []
        except (json.JSONDecodeError, ValueError) as e:
            logger.error("Invalid JSON in Anthropic file '%s': %s", file_path, e)
            return []
        except Exception as e:
            logger.error("Unexpected error reading Anthropic file '%s': %s", file_path, e)
            return []
    
    def _parse_conversation(self, conv_data: Dict[str, Any]) -> Conversation:
        """
        Parse a single Anthropic conversation.
        
        Args:
            conv_data: Dictionary containing conversation data
            
        Returns:
            Conversation object
        """
        # Extract basic conversation info
        conv_id = conv_data.get('uuid', '')
        title = conv_data.get('name', 'Untitled Conversation')
        
        # Parse timestamps
        created_at = self._parse_timestamp(conv_data.get('created_at'))
        updated_at = self._parse_timestamp(conv_data.get('updated_at'))
        
        # Create conversation object
        conversation = Conversation(
            id=conv_id,
            title=title,
            source=self.source_name,
            created_at=created_at,
            updated_at=updated_at
        )
        
        # Parse messages
        chat_messages = conv_data.get('chat_messages', [])
        for msg_data in chat_messages:
            message = self._parse_message(msg_data)
            if message:
                conversation.messages.append(message)
        
        # Sort messages by index to ensure correct order
        conversation.messages.sort(key=lambda m: getattr(m, 'index', 0))
        
        return conversation
    
    def _parse_message(self, msg_data: Dict[str, Any]) -> Message:
        """
        Parse a single message from Anthropic format.
        
        Args:
            msg_data: Dictionary containing message data
            
        Returns:
            Message object or None if parsing fails
        """
        try:
            # Extract message content
            text = msg_data.get('text', '').strip()
            if not text:
                return None
            
            # Clean content
            content = self._clean_content(text)
            if not content:
                return None
            
            # Determine role
            sender = msg_data.get('sender', 'unknown')
            if sender == 'human':
                role = 'user'
            elif sender == 'assistant':
                role = 'assistant'
            else:
                role = 'system'
            
            # Parse timestamp
            timestamp = self._parse_timestamp(msg_data.get('created_at'))
            
            # Get message UUID
            msg_uuid = msg_data.get('uuid', '')
            
            message = Message(
                role=role,
                content=content,
                timestamp=timestamp,
                uuid=msg_uuid
            )
            
            # Store index for sorting
            message.index = msg_data.get('index', 0)
            
            return message
            
        except (KeyError, ValueError, AttributeError, TypeError) as e:
            logger.debug("Failed to parse message: %s", e)
            return None