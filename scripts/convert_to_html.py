#!/usr/bin/env python3
"""
HTML Chat Archive Converter - Main Script

Converts Anthropic and OpenAI chat archives to HTML format with iOS-style chat bubbles,
light/dark mode support, and navigation features.
"""
import os
import sys
import zipfile
from datetime import datetime
from typing import List, Dict, Any

# Add the scripts directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from parsers.anthropic_parser import AnthropicParser
from parsers.openai_parser import OpenAIParser
from parsers.base_parser import Conversation
from generators.html_generator import HTMLGenerator
from generators.index_generator import IndexGenerator
from generators.asset_manager import AssetManager


class ChatArchiveConverter:
    """Main converter class that orchestrates the conversion process."""
    
    def __init__(self):
        """Initialize the converter with default paths."""
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.script_dir)
        
        # Input paths
        self.data_dir = os.path.join(self.project_root, 'data')
        self.raw_data_dir = os.path.join(self.data_dir, 'raw')
        
        # Output paths
        self.html_output_dir = os.path.join(self.data_dir, 'html')
        
        # Template and asset paths
        self.templates_dir = os.path.join(self.script_dir, 'templates')
        self.assets_dir = os.path.join(self.script_dir, 'assets')
        
        # Initialize components
        self.anthropic_parser = AnthropicParser()
        self.openai_parser = OpenAIParser()
        self.html_generator = HTMLGenerator(self.templates_dir, self.assets_dir)
        self.index_generator = IndexGenerator(self.templates_dir)
        self.asset_manager = AssetManager(self.assets_dir)
    
    def find_input_files(self) -> Dict[str, str]:
        """
        Find available input files in the raw data directory.
        
        Returns:
            Dictionary mapping source names to file paths
        """
        input_files = {}
        
        # Look for Anthropic files
        anthropic_patterns = [
            'claude_conversations.json',
            'anthropic_conversations.json',
            'example_claude_conversations.json'
        ]
        
        for pattern in anthropic_patterns:
            file_path = os.path.join(self.raw_data_dir, pattern)
            if os.path.exists(file_path):
                input_files['anthropic'] = file_path
                break
        
        # Look for OpenAI files
        openai_patterns = [
            'openai_conversations.json',
            'chatgpt_conversations.json',
            'example_openai_conversations.json'
        ]
        
        for pattern in openai_patterns:
            file_path = os.path.join(self.raw_data_dir, pattern)
            if os.path.exists(file_path):
                input_files['openai'] = file_path
                break
        
        return input_files
    
    def parse_conversations(self, input_files: Dict[str, str]) -> Dict[str, List[Conversation]]:
        """
        Parse conversations from input files.
        
        Args:
            input_files: Dictionary mapping source names to file paths
            
        Returns:
            Dictionary mapping source names to conversation lists
        """
        all_conversations = {}
        
        # Parse Anthropic conversations
        if 'anthropic' in input_files:
            print(f"Parsing Anthropic conversations from {input_files['anthropic']}...")
            conversations = self.anthropic_parser.parse_file(input_files['anthropic'])
            all_conversations['anthropic'] = conversations
            print(f"Found {len(conversations)} Anthropic conversations")
        
        # Parse OpenAI conversations
        if 'openai' in input_files:
            print(f"Parsing OpenAI conversations from {input_files['openai']}...")
            conversations = self.openai_parser.parse_file(input_files['openai'])
            all_conversations['openai'] = conversations
            print(f"Found {len(conversations)} OpenAI conversations")
        
        return all_conversations
    
    def create_output_directory(self) -> str:
        """
        Create timestamped output directory.
        
        Returns:
            Path to the created output directory
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join(self.html_output_dir, f'chat_export_{timestamp}')
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def generate_html_files(
        self,
        conversations_by_source: Dict[str, List[Conversation]],
        output_dir: str
    ) -> List[Dict[str, Any]]:
        """
        Generate HTML files for all conversations.
        
        Args:
            conversations_by_source: Dictionary mapping source names to conversation lists
            output_dir: Output directory path
            
        Returns:
            List of all conversation metadata
        """
        all_conversation_metadata = []
        
        # Generate HTML for each source
        for source_name, conversations in conversations_by_source.items():
            if not conversations:
                continue
            
            print(f"Generating HTML files for {len(conversations)} {source_name} conversations...")
            
            # Generate conversation HTML files
            metadata = self.html_generator.generate_conversations_batch(
                conversations=conversations,
                output_dir=output_dir,
                source_subdir=source_name,
                assets_relative_path="../../assets",
                index_relative_path="../../index.html",
                source_index_relative_path="../index.html"
            )
            
            all_conversation_metadata.extend(metadata)
            
            # Generate source-specific index
            source_index_path = os.path.join(output_dir, source_name, 'index.html')
            self.index_generator.generate_source_index(
                conversations=metadata,
                source_name=source_name,
                output_path=source_index_path,
                assets_relative_path="../assets",
                main_index_path="../index.html"
            )
            
            print(f"Generated {len(metadata)} HTML files for {source_name}")
        
        return all_conversation_metadata
    
    def generate_main_index(self, all_metadata: List[Dict[str, Any]], output_dir: str) -> bool:
        """
        Generate the main index page.
        
        Args:
            all_metadata: List of all conversation metadata
            output_dir: Output directory path
            
        Returns:
            True if successful, False otherwise
        """
        print("Generating main index page...")
        
        main_index_path = os.path.join(output_dir, 'index.html')
        success = self.index_generator.generate_main_index(
            all_conversations=all_metadata,
            output_path=main_index_path,
            assets_relative_path="assets"
        )
        
        if success:
            print("Generated main index page")
        else:
            print("Failed to generate main index page")
        
        return success
    
    def setup_assets(self, output_dir: str) -> bool:
        """
        Copy assets and create additional files.
        
        Args:
            output_dir: Output directory path
            
        Returns:
            True if successful, False otherwise
        """
        print("Setting up assets...")
        
        assets_dir = os.path.join(output_dir, 'assets')
        success = self.asset_manager.setup_complete_assets(
            destination_dir=assets_dir,
            site_name="Chat Archive"
        )
        
        if success:
            print("Assets setup complete")
        else:
            print("Failed to setup assets")
        
        return success
    
    def create_zip_package(self, output_dir: str) -> str:
        """
        Create a zip package of the generated HTML files.
        
        Args:
            output_dir: Output directory path
            
        Returns:
            Path to the created zip file
        """
        print("Creating zip package...")
        
        zip_path = f"{output_dir}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, output_dir)
                    zipf.write(file_path, arc_path)
        
        print(f"Created zip package: {zip_path}")
        return zip_path
    
    def convert(self) -> bool:
        """
        Run the complete conversion process.
        
        Returns:
            True if successful, False otherwise
        """
        print("🚀 Starting HTML Chat Archive Converter...")
        print("=" * 50)
        
        try:
            # Find input files
            input_files = self.find_input_files()
            if not input_files:
                print("❌ No input files found!")
                print(f"Please place your JSON files in: {self.raw_data_dir}")
                print("Expected filenames:")
                print("  - claude_conversations.json (or anthropic_conversations.json)")
                print("  - openai_conversations.json (or chatgpt_conversations.json)")
                return False
            
            print(f"📁 Found input files: {list(input_files.keys())}")
            
            # Parse conversations
            conversations_by_source = self.parse_conversations(input_files)
            if not conversations_by_source:
                print("❌ No conversations found in input files!")
                return False
            
            total_conversations = sum(len(convs) for convs in conversations_by_source.values())
            print(f"📊 Total conversations to convert: {total_conversations}")
            
            # Create output directory
            output_dir = self.create_output_directory()
            print(f"📂 Output directory: {output_dir}")
            
            # Generate HTML files
            all_metadata = self.generate_html_files(conversations_by_source, output_dir)
            if not all_metadata:
                print("❌ Failed to generate HTML files!")
                return False
            
            # Generate main index
            if not self.generate_main_index(all_metadata, output_dir):
                print("❌ Failed to generate main index!")
                return False
            
            # Setup assets
            if not self.setup_assets(output_dir):
                print("❌ Failed to setup assets!")
                return False
            
            # Create zip package
            zip_path = self.create_zip_package(output_dir)
            
            print("=" * 50)
            print("✅ Conversion completed successfully!")
            print(f"📁 HTML files: {output_dir}")
            print(f"📦 Zip package: {zip_path}")
            print(f"🌐 Open {os.path.join(output_dir, 'index.html')} in your browser")
            
            return True
            
        except Exception as e:
            print(f"❌ Conversion failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point."""
    converter = ChatArchiveConverter()
    success = converter.convert()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()