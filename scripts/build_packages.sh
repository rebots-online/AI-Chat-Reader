#!/bin/bash
set -e

# Build standalone binary with PyInstaller
pyinstaller --onefile scripts/convert_to_html.py --name chat-archive-converter

# Prepare AppDir for AppImage
APPDIR=dist/AppDir
mkdir -p "$APPDIR/usr/bin"
cp dist/chat-archive-converter "$APPDIR/usr/bin/"
mkdir -p "$APPDIR/usr/share/applications" "$APPDIR/usr/share/icons/hicolor/256x256/apps"
cat > "$APPDIR/chat-archive-converter.desktop" <<EOD
[Desktop Entry]
Type=Application
Name=Chat Archive Converter
Exec=chat-archive-converter
Icon=chat-archive-converter
Categories=Utility;
EOD
cp "$APPDIR/chat-archive-converter.desktop" "$APPDIR/usr/share/applications/"

# Placeholder icon (blank png)
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
printf '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\xda\x63\x00\x01\x00\x00\x05\x00\x01\x0d\n\x2d\xb4\x00\x00\x00\x00IEND\xaeB`\x82' > "$APPDIR/usr/share/icons/hicolor/256x256/apps/chat-archive-converter.png"

# Build AppImage
ROOT_DIR="$(dirname "$0")/.."
if [ -e /dev/fuse ]; then
  "$ROOT_DIR/appimagetool.AppImage" "$APPDIR" dist/chat-archive-converter.AppImage
else
  echo "FUSE not available; skipping AppImage build" >&2
fi

# Build DEB package
DEB_DIR=dist/deb/chat-archive-converter
mkdir -p "$DEB_DIR/DEBIAN" "$DEB_DIR/usr/bin"
cp dist/chat-archive-converter "$DEB_DIR/usr/bin/"
cat > "$DEB_DIR/DEBIAN/control" <<EOD
Package: chat-archive-converter
Version: 1.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Auto Generated <noreply@example.com>
Description: Offline chat archive converter to HTML and other formats
EOD
chmod -R 0755 "$DEB_DIR/DEBIAN"
dpkg-deb --build "$DEB_DIR" dist/chat-archive-converter.deb

echo "Packages created in dist/"
