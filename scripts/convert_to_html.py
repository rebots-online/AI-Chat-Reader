#!/usr/bin/env python3
# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.
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
import argparse # Added for command-line arguments
from pathlib import Path # Added for Path operations, useful for filenames

# Add the scripts directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from parsers.anthropic_parser import AnthropicParser
from parsers.openai_parser import OpenAIParser
from parsers.base_parser import Conversation
from generators.html_generator import HTMLGenerator
from generators.index_generator import IndexGenerator
from generators.asset_manager import AssetManager
from generators.gif_generator import AnimatedGifGenerator # Added for GIF generation
import pdfkit # Added for PDF generation
import imgkit # Added for PNG/SVG generation


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
        print(f"[DEBUG] Absolute path for self.script_dir: {os.path.abspath(self.script_dir)}")
        print(f"[DEBUG] Calculated self.templates_dir: {self.templates_dir}")
        print(f"[DEBUG] Absolute path for self.templates_dir: {os.path.abspath(self.templates_dir)}")
        try:
            print(f"[DEBUG] Contents of self.templates_dir according to os.listdir: {os.listdir(self.templates_dir)}")
        except FileNotFoundError:
            print(f"[DEBUG] Error: self.templates_dir ({self.templates_dir}) not found by os.listdir.")
        except Exception as e_listdir:
            print(f"[DEBUG] Error listing contents of self.templates_dir ({self.templates_dir}): {e_listdir}")
        self.assets_dir = os.path.join(self.script_dir, 'assets')
        
        # Initialize components
        self.anthropic_parser = AnthropicParser()
        self.openai_parser = OpenAIParser()
        self.html_generator = HTMLGenerator(self.templates_dir, self.assets_dir)
        self.index_generator = IndexGenerator(self.templates_dir)
        self.asset_manager = AssetManager(self.assets_dir)
        self.gif_generator = AnimatedGifGenerator(assets_dir=self.assets_dir) # Initialized GIF generator
    
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
            
            
            # Generate conversation HTML files for this source
            metadata = self.html_generator.generate_conversations_batch(
                conversations=conversations,
                output_dir=output_dir,
                source_subdir=source_name,
                assets_relative_path="../assets",
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
    
    def convert(self, args) -> bool: # Added args parameter
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

            # Generate PDFs if requested
            if args.pdf:
                print("=" * 50)
                print("📄 Generating PDFs...")
                pdf_export_dir = os.path.join(output_dir, 'pdfs')
                os.makedirs(pdf_export_dir, exist_ok=True)

                for item in all_metadata:
                    try:
                        html_file_path = os.path.join(output_dir, item['filename']) # item['filename'] is relative to output_dir

                        # Determine source subdirectory for PDF from the HTML path
                        # item['filename'] is like 'openai/conversations/file.html' or 'anthropic/conversations/file.html'
                        path_parts = Path(item['filename']).parts
                        source_subdir_for_pdf = path_parts[0] # e.g., 'openai' or 'anthropic'

                        pdf_source_dir = os.path.join(pdf_export_dir, source_subdir_for_pdf)
                        os.makedirs(pdf_source_dir, exist_ok=True)

                        pdf_filename_base = Path(item['filename']).stem
                        pdf_output_path = os.path.join(pdf_source_dir, f"{pdf_filename_base}.pdf")

                        print(f"  Generating PDF for: {item['title']} ({item['source']}) -> {pdf_output_path}")
                        pdfkit.from_file(html_file_path, pdf_output_path, options={'quiet': ''})
                        print(f"    Successfully generated PDF: {pdf_output_path}")
                    except Exception as e_pdf:
                        print(f"    Error generating PDF for {item.get('title', 'Unknown Title')}: {e_pdf}")
                print("PDF generation process complete.")

            # Generate PNGs if requested
            if args.png:
                print("=" * 50)
                print("🖼️ Generating PNGs...")
                png_export_dir = os.path.join(output_dir, 'pngs')
                os.makedirs(png_export_dir, exist_ok=True)

                for item in all_metadata:
                    try:
                        html_file_path = os.path.join(output_dir, item['filename'])
                        path_parts = Path(item['filename']).parts
                        source_subdir_for_png = path_parts[0]

                        png_source_dir = os.path.join(png_export_dir, source_subdir_for_png)
                        os.makedirs(png_source_dir, exist_ok=True)

                        png_filename_base = Path(item['filename']).stem
                        png_output_path = os.path.join(png_source_dir, f"{png_filename_base}.png")

                        print(f"  Generating PNG for: {item['title']} ({item['source']}) -> {png_output_path}")
                        imgkit.from_file(html_file_path, png_output_path, options={'format': 'png', 'quiet': ''})
                        print(f"    Successfully generated PNG: {png_output_path}")
                    except Exception as e_png:
                        print(f"    Error generating PNG for {item.get('title', 'Unknown Title')}: {e_png}")
                print("PNG generation process complete.")

            # Generate SVGs if requested
            if args.svg:
                print("=" * 50)
                print("🖼️ Generating SVGs...")
                svg_export_dir = os.path.join(output_dir, 'svgs')
                os.makedirs(svg_export_dir, exist_ok=True)

                for item in all_metadata:
                    try:
                        html_file_path = os.path.join(output_dir, item['filename'])
                        path_parts = Path(item['filename']).parts
                        source_subdir_for_svg = path_parts[0]

                        svg_source_dir = os.path.join(svg_export_dir, source_subdir_for_svg)
                        os.makedirs(svg_source_dir, exist_ok=True)

                        svg_filename_base = Path(item['filename']).stem
                        svg_output_path = os.path.join(svg_source_dir, f"{svg_filename_base}.svg")

                        print(f"  Generating SVG for: {item['title']} ({item['source']}) -> {svg_output_path}")
                        # For SVG, wkhtmltoimage might produce better results if direct SVG output is supported.
                        # imgkit options for SVG might be limited or behave like raster-to-vector.
                        # Using format: 'svg' with imgkit relies on wkhtmltoimage's capabilities.
                        imgkit.from_file(html_file_path, svg_output_path, options={'format': 'svg', 'quiet': ''})
                        print(f"    Successfully generated SVG: {svg_output_path}")
                    except Exception as e_svg:
                        print(f"    Error generating SVG for {item.get('title', 'Unknown Title')}: {e_svg}")
                print("SVG generation process complete.")
            
            # Create zip package
            zip_path = self.create_zip_package(output_dir)

            # Generate GIFs if requested
            if args.gif:
                print("=" * 50)
                print("🖼️ Generating GIFs...")
                # Overall directory for all GIFs from this export run
                gif_export_run_dir = os.path.join(output_dir, 'gifs')
                os.makedirs(gif_export_run_dir, exist_ok=True)

                for source_name, conversations in conversations_by_source.items():
                    if not conversations:
                        continue

                    # Source-specific subdirectory for GIFs
                    source_gif_output_dir = os.path.join(gif_export_run_dir, source_name)
                    os.makedirs(source_gif_output_dir, exist_ok=True)

                    print(f"Generating GIFs for {len(conversations)} {source_name} conversations...")
                    for conversation in conversations:
                        # Find corresponding metadata to get the HTML filename base
                        conv_metadata = next((m for m in all_metadata if m['id'] == conversation.id and m['source'] == source_name), None)

                        if conv_metadata and 'filename' in conv_metadata:
                            gif_filename_base = Path(conv_metadata['filename']).stem
                            gif_output_path = os.path.join(source_gif_output_dir, f"{gif_filename_base}.gif")

                            print(f"  Generating GIF for: {conversation.title} -> {gif_output_path}")
                            try:
                                success_gif = self.gif_generator.generate_gif(conversation, str(gif_output_path))
                                if success_gif:
                                    print(f"    Successfully generated GIF: {gif_output_path}")
                                else:
                                    print(f"    Failed to generate GIF for: {conversation.title}")
                            except Exception as e_gif:
                                print(f"    Error generating GIF for {conversation.title}: {e_gif}")
                        else:
                            print(f"  Skipping GIF for conversation ID {conversation.id} (source: {source_name}) due to missing metadata or filename.")
                print("GIF generation process complete.")
            
            print("=" * 50)
            print("✅ Conversion completed successfully!")
            print(f"📁 HTML files: {output_dir}")
            if args.pdf:
                print(f"📄 PDFs: {pdf_export_dir}")
            if args.png:
                print(f"🖼️ PNGs: {png_export_dir}")
            if args.svg:
                print(f"🖼️ SVGs: {svg_export_dir}")
            if args.gif: # GIF dir is defined inside its own "if args.gif" block
                gif_export_run_dir = os.path.join(output_dir, 'gifs') # Re-define for printout
                print(f"🖼️ GIFs: {gif_export_run_dir}")
            print(f"📦 Zip package: {zip_path}")
            print(f"🌐 Open {os.path.join(output_dir, 'index.html')} in your browser")
            
            return True
            
        except Exception as e:
            print(f"❌ Conversion failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def print_version_banner():
    """
    Print version and copyright banner as FIRST step of initialization.

    Windsurf Rule: Copyright must be displayed on all console/terminal apps
    as a first step loading and initializing, so it displays regardless of
    successful execution and initialization or not.
    """
    import time

    # Read version from VERSION file
    version_file = Path(__file__).parent.parent / "VERSION"
    try:
        version = version_file.read_text().strip() if version_file.exists() else "unknown"
    except Exception:
        version = "unknown"

    # Generate build number: (epoch % 100) * 1000 + minutes_past_hour
    epoch = int(time.time())
    epoch_mod = epoch % 100
    minutes = (epoch // 60) % 60
    build_num = epoch_mod * 1000 + minutes

    # Print banner - this MUST be the first output
    print("=" * 70)
    print(f"AI Chat Reader v{version} Build {build_num}")
    print("Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.")
    print("=" * 70)
    print()


def main():
    """Main entry point."""
    # CRITICAL: Print version/banner FIRST before any other operations
    # This ensures copyright is always displayed, even if imports fail
    print_version_banner()

    parser = argparse.ArgumentParser(description="Convert chat archives to HTML and optionally GIFs/PDFs/PNGs/SVGs.")
    parser.add_argument('--gif', action='store_true', help='Generate animated GIF for each conversation')
    parser.add_argument('--pdf', action='store_true', help='Generate PDF for each conversation')
    parser.add_argument('--png', action='store_true', help='Generate PNG image for each conversation')
    parser.add_argument('--svg', action='store_true', help='Generate SVG image for each conversation')
    # One could add --input-dir and --output-dir arguments here if needed
    # parser.add_argument('--input-dir', default='data/raw', help='Directory containing raw chat files.')
    # parser.add_argument('--output-dir', default='data/html', help='Base directory for HTML output.')
    args = parser.parse_args()

    converter = ChatArchiveConverter() # Potentially pass input/output dirs from args if added
    success = converter.convert(args) # Pass args to convert method
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()