"""
Asset manager for copying CSS, JS, and other static files.
"""
import os
import shutil
from typing import List, Dict


class AssetManager:
    """Manages copying and organizing static assets."""
    
    def __init__(self, source_assets_dir: str):
        """
        Initialize the asset manager.
        
        Args:
            source_assets_dir: Path to source assets directory
        """
        self.source_assets_dir = source_assets_dir
    
    def copy_assets(self, destination_dir: str) -> bool:
        """
        Copy all assets to the destination directory.
        
        Args:
            destination_dir: Destination directory for assets
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure destination exists
            os.makedirs(destination_dir, exist_ok=True)
            
            # Copy CSS files
            css_files = ['style.css']
            for css_file in css_files:
                src_path = os.path.join(self.source_assets_dir, css_file)
                dst_path = os.path.join(destination_dir, css_file)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dst_path)
                    print(f"Copied {css_file}")
                else:
                    print(f"Warning: {css_file} not found in source assets")
            
            # Copy JavaScript files
            js_files = ['script.js']
            for js_file in js_files:
                src_path = os.path.join(self.source_assets_dir, js_file)
                dst_path = os.path.join(destination_dir, js_file)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dst_path)
                    print(f"Copied {js_file}")
                else:
                    print(f"Warning: {js_file} not found in source assets")
            
            # Copy icons directory if it exists
            icons_src = os.path.join(self.source_assets_dir, 'icons')
            icons_dst = os.path.join(destination_dir, 'icons')
            if os.path.exists(icons_src):
                if os.path.exists(icons_dst):
                    shutil.rmtree(icons_dst)
                shutil.copytree(icons_src, icons_dst)
                print("Copied icons directory")
            
            return True
            
        except Exception as e:
            print(f"Error copying assets: {e}")
            return False
    
    def create_favicon(self, destination_dir: str) -> bool:
        """
        Create a simple favicon for the site.
        
        Args:
            destination_dir: Destination directory for favicon
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a simple SVG favicon
            favicon_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" fill="#007AFF" rx="6"/>
  <path d="M8 12h16v2H8zm0 4h16v2H8zm0 4h12v2H8z" fill="white"/>
</svg>'''
            
            favicon_path = os.path.join(destination_dir, 'favicon.svg')
            with open(favicon_path, 'w', encoding='utf-8') as f:
                f.write(favicon_svg)
            
            print("Created favicon.svg")
            return True
            
        except Exception as e:
            print(f"Error creating favicon: {e}")
            return False
    
    def create_manifest(self, destination_dir: str, site_name: str = "Chat Archive") -> bool:
        """
        Create a web app manifest for the site.
        
        Args:
            destination_dir: Destination directory for manifest
            site_name: Name of the site
            
        Returns:
            True if successful, False otherwise
        """
        try:
            manifest = {
                "name": site_name,
                "short_name": "Chat Archive",
                "description": "HTML Chat Archive Viewer",
                "start_url": "./index.html",
                "display": "standalone",
                "background_color": "#ffffff",
                "theme_color": "#007AFF",
                "icons": [
                    {
                        "src": "favicon.svg",
                        "sizes": "any",
                        "type": "image/svg+xml"
                    }
                ]
            }
            
            manifest_path = os.path.join(destination_dir, 'manifest.json')
            import json
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            print("Created manifest.json")
            return True
            
        except Exception as e:
            print(f"Error creating manifest: {e}")
            return False
    
    def create_robots_txt(self, destination_dir: str) -> bool:
        """
        Create a robots.txt file.
        
        Args:
            destination_dir: Destination directory for robots.txt
            
        Returns:
            True if successful, False otherwise
        """
        try:
            robots_content = """User-agent: *
Disallow: /assets/
Allow: /

# This is a personal chat archive
# Please respect privacy
"""
            
            robots_path = os.path.join(destination_dir, 'robots.txt')
            with open(robots_path, 'w', encoding='utf-8') as f:
                f.write(robots_content)
            
            print("Created robots.txt")
            return True
            
        except Exception as e:
            print(f"Error creating robots.txt: {e}")
            return False
    
    def setup_complete_assets(self, destination_dir: str, site_name: str = "Chat Archive") -> bool:
        """
        Set up all assets and meta files for the site.
        
        Args:
            destination_dir: Destination directory
            site_name: Name of the site
            
        Returns:
            True if all operations successful, False otherwise
        """
        success = True
        
        # Copy main assets
        if not self.copy_assets(destination_dir):
            success = False
        
        # Create favicon
        if not self.create_favicon(destination_dir):
            success = False
        
        # Create manifest
        if not self.create_manifest(destination_dir, site_name):
            success = False
        
        # Create robots.txt
        if not self.create_robots_txt(destination_dir):
            success = False
        
        return success
    
    def get_asset_list(self) -> List[str]:
        """
        Get a list of all assets that should be copied.
        
        Returns:
            List of asset filenames
        """
        assets = []
        
        if os.path.exists(self.source_assets_dir):
            for item in os.listdir(self.source_assets_dir):
                item_path = os.path.join(self.source_assets_dir, item)
                if os.path.isfile(item_path):
                    assets.append(item)
                elif os.path.isdir(item_path):
                    # Add directory contents
                    for subitem in os.listdir(item_path):
                        assets.append(f"{item}/{subitem}")
        
        return assets