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


def build_gnome_app_deb():
    """Build GNOME app as .deb package."""
    print("\n=== Building GNOME App .deb Package ===")

    version_str, build_num = get_full_version()
    version = get_version()
    project_root = Path(__file__).parent.parent

    # Create DEB directory structure
    deb_dir = Path("dist/deb/ai-chat-reader-gnome")
    deb_dir.mkdir(parents=True, exist_ok=True)

    # Create directory structure
    (deb_dir / "DEBIAN").mkdir(exist_ok=True)
    (deb_dir / "usr/bin").mkdir(parents=True, exist_ok=True)
    (deb_dir / "usr/share/ai-chat-reader/src/widgets").mkdir(parents=True, exist_ok=True)
    (deb_dir / "usr/share/ai-chat-reader/src/models").mkdir(parents=True, exist_ok=True)
    (deb_dir / "usr/share/ai-chat-reader/src/utils").mkdir(parents=True, exist_ok=True)
    (deb_dir / "usr/share/ai-chat-reader/scripts").mkdir(parents=True, exist_ok=True)
    (deb_dir / "usr/share/applications").mkdir(parents=True, exist_ok=True)
    (deb_dir / "usr/share/icons/hicolor/scalable/apps").mkdir(parents=True, exist_ok=True)
    (deb_dir / "usr/share/glib-2.0/schemas").mkdir(parents=True, exist_ok=True)

    # Copy source files
    import shutil

    # Copy main.js
    shutil.copy(project_root / "src/main.js", deb_dir / "usr/share/ai-chat-reader/src/")

    # Copy widgets
    for widget_file in (project_root / "src/widgets").glob("*.js"):
        shutil.copy(widget_file, deb_dir / "usr/share/ai-chat-reader/src/widgets/")

    # Copy models
    for model_file in (project_root / "src/models").glob("*.js"):
        shutil.copy(model_file, deb_dir / "usr/share/ai-chat-reader/src/models/")

    # Copy utils
    for util_file in (project_root / "src/utils").glob("*.js"):
        shutil.copy(util_file, deb_dir / "usr/share/ai-chat-reader/src/utils/")

    # Copy Python scripts
    shutil.copytree(project_root / "scripts", deb_dir / "usr/share/ai-chat-reader/scripts",
                    dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'build.py'))

    # Copy desktop file and icon
    shutil.copy(project_root / "data/org.gnome.AI-Chat-Reader.desktop",
                deb_dir / "usr/share/applications/")
    shutil.copy(project_root / "data/org.gnome.AI-Chat-Reader.svg",
                deb_dir / "usr/share/icons/hicolor/scalable/apps/")
    shutil.copy(project_root / "data/org.gnome.AI-Chat-Reader.gschema.xml",
                deb_dir / "usr/share/glib-2.0/schemas/")

    # Create launcher script
    launcher_content = f"""#!/bin/bash
# AI Chat Reader v{version} Build {build_num}
# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.

export PKGDATADIR="/usr/share/ai-chat-reader"
export GSETTINGS_SCHEMA_DIR="/usr/share/glib-2.0/schemas:$GSETTINGS_SCHEMA_DIR"

cd /usr/share/ai-chat-reader
exec gjs -m /usr/share/ai-chat-reader/src/main.js "$@"
"""
    launcher_path = deb_dir / "usr/bin/ai-chat-reader"
    launcher_path.write_text(launcher_content)
    subprocess.run(["chmod", "+x", str(launcher_path)], check=True)

    # Create control file
    control_content = f"""Package: ai-chat-reader-gnome
Version: {version}-{build_num}
Section: utils
Priority: optional
Architecture: all
Depends: gjs (>= 1.72.0), libgtk-4-1 (>= 4.6.0), libadwaita-1-0 (>= 1.2.0), python3, python3-jinja2, python3-pil
Maintainer: Robin L. M. Cheung, MBA <noreply@example.com>
Description: AI Chat Reader - GNOME GUI Application
 Convert OpenAI and Anthropic chat exports to HTML format
 with iOS-style chat bubbles, light/dark mode support,
 and navigation features. This is the GNOME desktop application.
"""
    (deb_dir / "DEBIAN" / "control").write_text(control_content)

    # Create postinst script
    postinst_content = """#!/bin/bash
set -e
glib-compile-schemas /usr/share/glib-2.0/schemas || true
gtk-update-icon-cache -f -t /usr/share/icons/hicolor || true
update-desktop-database /usr/share/applications || true
"""
    postinst_path = deb_dir / "DEBIAN" / "postinst"
    postinst_path.write_text(postinst_content)
    subprocess.run(["chmod", "0755", str(postinst_path)], check=True)

    # Set permissions
    subprocess.run(["chmod", "-R", "0755", str(deb_dir / "DEBIAN")], check=True)

    # Build deb package
    deb_output = Path("dist") / f"ai-chat-reader-gnome-{version}-{build_num}-all.deb"
    subprocess.run(["dpkg-deb", "--build", str(deb_dir), str(deb_output)], check=True)

    print(f"✅ GNOME .deb package built: {deb_output}")
    return deb_output


def build_appimage():
    """Build AppImage package for GNOME app."""
    print("\n=== Building AppImage ===")

    version_str, build_num = get_full_version()
    version = get_version()
    project_root = Path(__file__).parent.parent

    # Check if appimagetool exists
    appimagetool_path = None
    try:
        result = subprocess.run(["which", "appimagetool"], check=True, capture_output=True, text=True)
        appimagetool_path = result.stdout.strip()
    except subprocess.CalledProcessError:
        # Try to download appimagetool
        print("⚠️  appimagetool not found, attempting to download...")
        try:
            appimagetool_path = Path("dist/appimagetool-x86_64.AppImage")
            if not appimagetool_path.exists():
                subprocess.run([
                    "wget", "-q", "-O", str(appimagetool_path),
                    "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
                ], check=True)
                subprocess.run(["chmod", "+x", str(appimagetool_path)], check=True)
            appimagetool_path = str(appimagetool_path)
        except Exception as e:
            print(f"⚠️  Could not download appimagetool: {e}")
            print("⚠️  Skipping AppImage build")
            return None

    import shutil

    # Create AppDir structure
    appdir = Path("dist/AI-Chat-Reader.AppDir")
    if appdir.exists():
        shutil.rmtree(appdir)
    appdir.mkdir(parents=True)

    # Create directory structure
    (appdir / "usr/bin").mkdir(parents=True)
    (appdir / "usr/share/ai-chat-reader/src/widgets").mkdir(parents=True)
    (appdir / "usr/share/ai-chat-reader/src/models").mkdir(parents=True)
    (appdir / "usr/share/ai-chat-reader/src/utils").mkdir(parents=True)
    (appdir / "usr/share/ai-chat-reader/scripts").mkdir(parents=True)
    (appdir / "usr/share/applications").mkdir(parents=True)
    (appdir / "usr/share/icons/hicolor/scalable/apps").mkdir(parents=True)
    (appdir / "usr/share/glib-2.0/schemas").mkdir(parents=True)

    # Copy source files
    shutil.copy(project_root / "src/main.js", appdir / "usr/share/ai-chat-reader/src/")

    for widget_file in (project_root / "src/widgets").glob("*.js"):
        shutil.copy(widget_file, appdir / "usr/share/ai-chat-reader/src/widgets/")

    for model_file in (project_root / "src/models").glob("*.js"):
        shutil.copy(model_file, appdir / "usr/share/ai-chat-reader/src/models/")

    for util_file in (project_root / "src/utils").glob("*.js"):
        shutil.copy(util_file, appdir / "usr/share/ai-chat-reader/src/utils/")

    shutil.copytree(project_root / "scripts", appdir / "usr/share/ai-chat-reader/scripts",
                    dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'build.py'))

    # Copy desktop file and icon
    shutil.copy(project_root / "data/org.gnome.AI-Chat-Reader.desktop",
                appdir / "usr/share/applications/")
    shutil.copy(project_root / "data/org.gnome.AI-Chat-Reader.svg",
                appdir / "usr/share/icons/hicolor/scalable/apps/")
    shutil.copy(project_root / "data/org.gnome.AI-Chat-Reader.gschema.xml",
                appdir / "usr/share/glib-2.0/schemas/")

    # Copy to AppDir root for AppImage (must match Icon= in desktop file)
    shutil.copy(project_root / "data/org.gnome.AI-Chat-Reader.desktop", appdir / "org.gnome.AI-Chat-Reader.desktop")
    shutil.copy(project_root / "data/org.gnome.AI-Chat-Reader.svg", appdir / "org.gnome.AI-Chat-Reader.svg")

    # Create AppRun script
    apprun_content = f"""#!/bin/bash
# AI Chat Reader v{version} Build {build_num}
# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.

HERE="$(dirname "$(readlink -f "${{0}}")")"

export PATH="$HERE/usr/bin:$PATH"
export PKGDATADIR="$HERE/usr/share/ai-chat-reader"
export GSETTINGS_SCHEMA_DIR="$HERE/usr/share/glib-2.0/schemas:$GSETTINGS_SCHEMA_DIR"
export XDG_DATA_DIRS="$HERE/usr/share:$XDG_DATA_DIRS"
export GI_TYPELIB_PATH="$HERE/usr/lib/girepository-1.0:$GI_TYPELIB_PATH"

# Compile schemas if needed
if [ ! -f "$HERE/usr/share/glib-2.0/schemas/gschemas.compiled" ]; then
    glib-compile-schemas "$HERE/usr/share/glib-2.0/schemas" 2>/dev/null || true
fi

cd "$HERE/usr/share/ai-chat-reader"
exec gjs -m "$HERE/usr/share/ai-chat-reader/src/main.js" "$@"
"""
    apprun_path = appdir / "AppRun"
    apprun_path.write_text(apprun_content)
    subprocess.run(["chmod", "+x", str(apprun_path)], check=True)

    # Compile schemas
    try:
        subprocess.run([
            "glib-compile-schemas",
            str(appdir / "usr/share/glib-2.0/schemas")
        ], check=True, capture_output=True)
    except Exception as e:
        print(f"⚠️  Could not compile schemas: {e}")

    # Build AppImage
    appimage_output = Path("dist") / f"AI-Chat-Reader-{version}-{build_num}-x86_64.AppImage"
    try:
        env = os.environ.copy()
        env["ARCH"] = "x86_64"
        subprocess.run([
            appimagetool_path,
            str(appdir),
            str(appimage_output)
        ], check=True, env=env)
        print(f"✅ AppImage built: {appimage_output}")
        return appimage_output
    except Exception as e:
        print(f"⚠️  AppImage build failed: {e}")
        return None


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

        # Step 3: Build CLI .deb package
        try:
            build_deb_package()
        except Exception as e:
            print(f"⚠️  CLI .deb build failed: {e}")

        # Step 4: Build GNOME App .deb package
        try:
            build_gnome_app_deb()
        except Exception as e:
            print(f"⚠️  GNOME .deb build failed: {e}")
            import traceback
            traceback.print_exc()

        # Step 5: Build AppImage
        try:
            build_appimage()
        except Exception as e:
            print(f"⚠️  AppImage build failed: {e}")
            import traceback
            traceback.print_exc()

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
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
