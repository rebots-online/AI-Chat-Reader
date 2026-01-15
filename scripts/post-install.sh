#!/bin/bash
# Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.
# Post-install script for AI Chat Reader

# Compile GSettings schemas
if [ -z "$DESTDIR" ]; then
    echo "Compiling GSettings schemas..."
    glib-compile-schemas "${MESON_INSTALL_PREFIX}/share/glib-2.0/schemas" || true
    
    echo "Updating icon cache..."
    gtk-update-icon-cache -f -t "${MESON_INSTALL_PREFIX}/share/icons/hicolor" || true
    
    echo "Updating desktop database..."
    update-desktop-database "${MESON_INSTALL_PREFIX}/share/applications" || true
fi

echo "Post-install completed."
