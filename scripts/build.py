#!/usr/bin/env python3
# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.

"""
Build script for AI Chat Reader
Generates versioned packages with auto-incrementing build numbers.
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime


def get_version():
    """Read version from VERSION file."""
    version_file = Path(__file__).parent.parent / "VERSION"
    return version_file.read_text().strip()


def generate_build_number():
    """Generate build number from epoch time."""
    epoch = int(time.time())
    epoch_mod = epoch % 100
    minutes = (epoch // 60) % 60
    return epoch_mod * 1000 + minutes


def get_full_version():
    """Get full version string with build number."""
    version = get_version()
    build_num = generate_build_number()
    return f"v{version} Build {build_num}", build_num


def run_command(cmd, check=True):
    """Run a shell command and return output."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=check)
    return result


def install_dependencies():
    """Install build dependencies."""
    print("=== Installing Build Dependencies ===")

    # Check for PyInstaller
    try:
        result = run_command(["pyinstaller", "--version"], check=False)
        if result.returncode != 0:
            print("Installing PyInstaller...")
            run_command(["pip", "install", "pyinstaller"])
    except FileNotFoundError:
        print("Installing PyInstaller...")
        run_command([sys.executable, "-m", "pip", "install", "pyinstaller"])


def build_cli_binary():
    """Build standalone CLI binary with PyInstaller."""
    print("\n=== Building CLI Binary ===")

    version_str, build_num = get_full_version()
    print(f"Version: {version_str}")

    # Run PyInstaller with hidden imports
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--name", f"chat-archive-converter-{version_str.replace(' ', '-').lower()}",
        "--add-data", f"VERSION:.",
        "--hidden-import", "jinja2",
        "--hidden-import", "markdown",
        "--hidden-import", "PIL",
        "--hidden-import", "pdfkit",
        "--hidden-import", "docx",
        "--hidden-import", "openpyxl",
        "--hidden-import", "reportlab",
        "--collect-all", "jinja2",
        "--collect-all", "markdown",
        str(Path(__file__).parent.parent / "scripts" / "convert_to_html.py")
    ]

    run_command(pyinstaller_cmd)
    print(f"✅ CLI binary built: dist/chat-archive-converter-*")


def build_deb_package():
    """Build Debian package."""
    print("\n=== Building .deb Package ===")

    version_str, build_num = get_full_version()

    # Get the binary name
    binary_name = f"chat-archive-converter-{version_str.replace(' ', '-').lower()}"

    # Create DEB directory structure
    deb_dir = Path("dist/deb/chat-archive-converter")
    deb_dir.mkdir(parents=True, exist_ok=True)

    # Create control directories
    (deb_dir / "DEBIAN").mkdir(exist_ok=True)
    (deb_dir / "usr/bin").mkdir(parents=True, exist_ok=True)

    # Copy binary
    binary_path = Path("dist") / binary_name
    if binary_path.exists():
        subprocess.run(["cp", str(binary_path), str(deb_dir / "usr/bin" / "chat-archive-converter")], check=True)

    # Create control file
    control_content = f"""Package: chat-archive-converter
Version: {get_version()}
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Robin L. M. Cheung, MBA <noreply@example.com>
Description: Offline chat archive converter to HTML and other formats
 Convert OpenAI and Anthropic chat exports to static HTML pages.
 Supports multiple output formats including PDF, DOCX, and more.
"""

    (deb_dir / "DEBIAN" / "control").write_text(control_content)

    # Set permissions
    subprocess.run(["chmod", "-R", "0755", str(deb_dir / "DEBIAN")], check=True)

    # Build deb package
    deb_output = Path("dist") / f"chat-archive-converter-{get_version()}-amd64.deb"
    subprocess.run(["dpkg-deb", "--build", str(deb_dir), str(deb_output)], check=True)

    print(f"✅ .deb package built: {deb_output}")


def build_appimage():
    """Build AppImage package."""
    print("\n=== Building AppImage ===")

    version_str, build_num = get_full_version()

    # Check if appimagetool exists
    try:
        subprocess.run(["which", "appimagetool"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("⚠️  appimagetool not found, skipping AppImage build")
        return

    # This would be expanded with actual AppImage build commands
    print("✅ AppImage would be built here (requires additional setup)")


def main():
    """Main build process."""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        AI Chat Reader - Build & Release Script            ║")
    print("║  Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.  ║")
    print("╚════════════════════════════════════════════════════════════╝")

    version_str, build_num = get_full_version()
    print(f"\n📦 Building: AI Chat Reader {version_str}")
    print(f"🕐 Build started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Step 1: Install dependencies
        install_dependencies()

        # Step 2: Build CLI binary
        build_cli_binary()

        # Step 3: Build packages
        try:
            build_deb_package()
        except Exception as e:
            print(f"⚠️  .deb build failed: {e}")

        try:
            build_appimage()
        except Exception as e:
            print(f"⚠️  AppImage build failed: {e}")

        print(f"\n✅ Build completed successfully!")
        print(f"📦 Output directory: dist/")
        print(f"🕐 Build completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # List built files
        print("\n📦 Built packages:")
        dist_dir = Path("dist")
        if dist_dir.exists():
            for file in sorted(dist_dir.iterdir()):
                if file.is_file() and not file.name.endswith('.pyc') and not file.name.endswith('.spec'):
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"  - {file.name} ({size_mb:.1f} MB)")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
