# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.
"""
HTML generator for individual conversation pages.
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from parsers.base_parser import Conversation, Message
import traceback
import markdown

class HTMLGenerator:
    """Generates HTML files for individual conversations."""
    
    def __init__(self, templates_dir: str, assets_dir: str):
        """
        Initialize the HTML generator.
        
        Args:
            templates_dir: Path to templates directory
            assets_dir: Path to assets directory
        """
        self.templates_dir = templates_dir
        self.assets_dir = assets_dir
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Add custom filters
        self.env.filters['nl2br'] = self._nl2br_filter
        
    def generate_conversation_html(
        self,
        conversation: Conversation,
        output_path: str,
        assets_relative_path: str = "../assets",
        index_relative_path: str = "../index.html",
        source_index_relative_path: Optional[str] = None,
        prev_conversation: Optional[Dict[str, str]] = None,
        next_conversation: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Generate HTML file for a single conversation.
        
        Args:
            conversation: Conversation object to render
            output_path: Path where HTML file should be saved
            assets_relative_path: Relative path to assets directory
            index_relative_path: Relative path to main index
            source_index_relative_path: Relative path to source-specific index
            prev_conversation: Previous conversation info (filename, title)
            next_conversation: Next conversation info (filename, title)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            template = self.env.get_template('conversation.html')
            
            # Prepare template context
            context = {
                'conversation': conversation,
                'assets_path': assets_relative_path,
                'index_path': index_relative_path,
                'source_index_path': source_index_relative_path,
                'prev_conversation': prev_conversation,
                'next_conversation': next_conversation,
                'generation_date': datetime.now()
            }
            
            # Render HTML
            html_content = template.render(**context)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
            
        except Exception as e:
            traceback.print_exc() # Added for detailed logging
            print(f"Error generating HTML for conversation {conversation.title}: {e}")
            return False
    
    def generate_conversations_batch(
        self,
        conversations: List[Conversation],
        output_dir: str,
        source_subdir: str,
        assets_relative_path: str = "../assets",
        index_relative_path: str = "../../index.html",
        source_index_relative_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate HTML files for a batch of conversations.
        
        Args:
            conversations: List of conversations to generate
            output_dir: Base output directory
            source_subdir: Subdirectory for this source (e.g., 'openai', 'anthropic')
            assets_relative_path: Relative path to assets
            index_relative_path: Relative path to main index
            source_index_relative_path: Relative path to source index
            
        Returns:
            List of conversation metadata for index generation
        """
        conversations_dir = os.path.join(output_dir, source_subdir, 'conversations')
        os.makedirs(conversations_dir, exist_ok=True)
        
        # Sort conversations by date for navigation
        sorted_conversations = sorted(
            conversations,
            key=lambda c: c.created_at or datetime.min
        )
        
        conversation_metadata = []
        
        for i, conversation in enumerate(sorted_conversations):
            # Generate safe filename
            filename = self._generate_safe_filename(conversation)
            file_path = os.path.join(conversations_dir, filename)
            
            # Determine previous and next conversations
            prev_conv = None
            next_conv = None
            
            if i > 0:
                prev_conversation = sorted_conversations[i - 1]
                prev_filename = self._generate_safe_filename(prev_conversation)
                prev_conv = {
                    'filename': prev_filename,
                    'title': prev_conversation.title
                }
            
            if i < len(sorted_conversations) - 1:
                next_conversation = sorted_conversations[i + 1]
                next_filename = self._generate_safe_filename(next_conversation)
                next_conv = {
                    'filename': next_filename,
                    'title': next_conversation.title
                }
            
            # Convert markdown content of each message to HTML
            for message in conversation.messages:
                message.content_html = markdown.markdown(message.content)
            
            # Generate HTML
            success = self.generate_conversation_html(
                conversation=conversation,
                output_path=file_path,
                assets_relative_path=assets_relative_path,
                index_relative_path=index_relative_path,
                source_index_relative_path=source_index_relative_path,
                prev_conversation=prev_conv,
                next_conversation=next_conv
            )
            
            if success:
                # Create metadata for index
                metadata = {
                    'title': conversation.title,
                    'filename': f"{source_subdir}/conversations/{filename}",
                    'source': conversation.source,
                    'id': conversation.id,
                    'created_at': conversation.created_at,
                    'updated_at': conversation.updated_at,
                    'message_count': len(conversation.messages),
                    'preview': self._generate_preview(conversation),
                    'uuid': getattr(conversation, "uuid", conversation.id)
                }
                conversation_metadata.append(metadata)
            else:
                print(f"Failed to generate HTML for conversation: {conversation.title}")
        
        return conversation_metadata
    
    def _generate_safe_filename(self, conversation: Conversation) -> str:
        """Generate a safe filename for the conversation."""
        # Clean title for filename
        safe_title = "".join(c for c in conversation.title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
        
        # Format date
        if conversation.created_at:
            date_str = conversation.created_at.strftime('%Y%m%d_%H%M%S')
        else:
            date_str = 'unknown'
        
        # Use first 8 chars of conversation ID as suffix
        id_suffix = conversation.id[:8] if conversation.id else 'unknown'
        
        return f"{safe_title}_{date_str}_{id_suffix}.html"
    
    def _generate_preview(self, conversation: Conversation, max_length: int = 150) -> str:
        """
        Generate a preview snippet from the conversation.
        
        Args:
            conversation: Conversation to generate preview for
            max_length: Maximum length of preview text
            
        Returns:
            Preview text string
        """
        import re
        raw = conversation.messages[-1].content if conversation.messages else ''
        plain = re.sub(r'[#*_>\[\]\(\)`]', '', raw)
        content = plain
        return content.strip()[:100]
    
    def _nl2br_filter(self, text: str) -> str:
        """
        Jinja2 filter to convert newlines to HTML line breaks.
        
        Args:
            text: Input text
            
        Returns:
            Text with newlines converted to <br> tags
        """
        if not text:
            return ""
        
        # Escape HTML first, then convert newlines
        from markupsafe import escape
        escaped = escape(text)
        return str(escaped).replace('\n', '<br>\n')