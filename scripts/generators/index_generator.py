# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.
"""
Index page generator for chat archive navigation.
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
import traceback


class IndexGenerator:
    """Generates index pages for navigation."""
    
    def __init__(self, templates_dir: str):
        """
        Initialize the index generator.
        
        Args:
            templates_dir: Path to templates directory
        """
        self.templates_dir = templates_dir
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def generate_main_index(
        self,
        all_conversations: List[Dict[str, Any]],
        output_path: str,
        assets_relative_path: str = "assets"
    ) -> bool:
        """
        Generate the main index page with all conversations.
        
        Args:
            all_conversations: List of all conversation metadata
            output_path: Path where index.html should be saved
            assets_relative_path: Relative path to assets directory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            template = self.env.get_template('index.html')
            
            # Sort conversations by date (newest first)
            sorted_conversations = sorted(
                all_conversations,
                key=lambda c: c.get('created_at') or datetime.min,
                reverse=True
            )
            
            # Calculate statistics
            total_messages = sum(c.get('message_count', 0) for c in all_conversations)
            
            # Get date range
            date_range = self._calculate_date_range(all_conversations)
            
            # Group conversations by source for navigation
            source_links = self._generate_source_links(all_conversations)
            
            # Prepare conversations data for JavaScript
            conversations_json = json.dumps([
                {
                    'title': c['title'],
                    'source': c['source'],
                    'created_at': c['created_at'].isoformat() if c.get('created_at') else None,
                    'message_count': c.get('message_count', 0),
                    'preview': c.get('preview', ''),
                    'filename': c['filename'],
                    'uuid': c.get('uuid', ''),
                }
                for c in sorted_conversations
            ])
            
            # Prepare template context
            context = {
                'page_title': 'Chat Archive',
                'conversations': sorted_conversations,
                'conversations_json': conversations_json,
                'total_messages': total_messages,
                'date_range': date_range,
                'source_links': source_links,
                'show_source_filter': len(source_links) > 1,
                'assets_path': assets_relative_path,
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
            print(f"Error generating main index: {e}")
            return False
    
    def generate_source_index(
        self,
        conversations: List[Dict[str, Any]],
        source_name: str,
        output_path: str,
        assets_relative_path: str = "../assets",
        main_index_path: str = "../index.html"
    ) -> bool:
        """
        Generate a source-specific index page.
        
        Args:
            conversations: List of conversations for this source
            source_name: Name of the source (e.g., 'openai', 'anthropic')
            output_path: Path where index.html should be saved
            assets_relative_path: Relative path to assets directory
            main_index_path: Relative path to main index
            
        Returns:
            True if successful, False otherwise
        """
        try:
            template = self.env.get_template('index.html')
            
            # Filter conversations for this source
            source_conversations = [
                c for c in conversations if c.get('source') == source_name
            ]
            
            # Sort conversations by date (newest first)
            sorted_conversations = sorted(
                source_conversations,
                key=lambda c: c.get('created_at') or datetime.min,
                reverse=True
            )
            
            # Calculate statistics
            total_messages = sum(c.get('message_count', 0) for c in source_conversations)
            
            # Get date range
            date_range = self._calculate_date_range(source_conversations)
            
            # Prepare conversations data for JavaScript
            conversations_json = json.dumps([
                {
                    'title': c['title'],
                    'source': c['source'],
                    'created_at': c['created_at'].isoformat() if c.get('created_at') else None,
                    'message_count': c.get('message_count', 0),
                    'preview': c.get('preview', ''),
                    'filename': f"conversations/{os.path.basename(c['filename'])}",
                    'uuid': c.get('uuid', ''),
                }
                for c in sorted_conversations
            ])
            
            # Prepare template context
            context = {
                'page_title': f'{source_name.title()} Conversations',
                'conversations': sorted_conversations,
                'conversations_json': conversations_json,
                'total_messages': total_messages,
                'date_range': date_range,
                'source_links': None,  # Don't show source links on source-specific pages
                'show_source_filter': False,
                'breadcrumb': {
                    'url': main_index_path,
                    'text': 'All Conversations'
                },
                'assets_path': assets_relative_path,
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
            print(f"Error generating {source_name} index: {e}")
            return False
    
    def _calculate_date_range(self, conversations: List[Dict[str, Any]]) -> Optional[Dict[str, datetime]]:
        """
        Calculate the date range for a list of conversations.
        
        Args:
            conversations: List of conversation metadata
            
        Returns:
            Dictionary with 'start' and 'end' datetime objects, or None
        """
        dates = [
            c.get('created_at') for c in conversations 
            if c.get('created_at') is not None
        ]
        
        if not dates:
            return None
        
        return {
            'start': min(dates),
            'end': max(dates)
        }
    
    def _generate_source_links(self, conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate source navigation links.
        
        Args:
            conversations: List of all conversation metadata
            
        Returns:
            List of source link dictionaries
        """
        # Count conversations by source
        source_counts = {}
        for conv in conversations:
            source = conv.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        # Generate links
        source_links = []
        for source, count in source_counts.items():
            if source != 'unknown':
                source_links.append({
                    'name': source,
                    'display_name': source.title(),
                    'url': f"{source}/index.html",
                    'count': count
                })
        
        # Sort by name
        source_links.sort(key=lambda x: x['name'])
        
        return source_links