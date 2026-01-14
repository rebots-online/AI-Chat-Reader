# Architecture Plan - 2025-09-26 (GNOME Launcher Regression) - Final

**Project UUIDv8:** 8f0f72f4-7b61-8e4d-bcb3-8f7a821dc9e5

## Updated Flow Summary
- `scripts/build_packages.sh` now writes the GNOME wrapper to execute `gjs "$DIR/src/main.js"`, matching the packaged directory structure where `main.js` lives under `src/`.
- AppDir and DEB layouts continue to stage GUI assets under `/usr/share/chat-archive-converter/src`, while the CLI binary remains at `/usr/bin/chat-archive-converter-cli`.
- GNOME desktop entry still launches the wrapper (`Exec=chat-archive-converter`), which `cd`s into `/usr/share/chat-archive-converter/` ensuring `imports.searchPath` resolves bundled widgets/utilities.

## Adjusted AST Highlights
```text
scripts/build_packages.sh
  ├─ Wrapper script cat <<'EOF'
  │    #!/bin/bash
  │    DIR="/usr/share/chat-archive-converter"
  │    cd "$DIR"
  │    exec gjs "$DIR/src/main.js" "$@"
  ├─ Desktop entry unchanged (Exec=chat-archive-converter)
  └─ DEB/AppImage stages rely on same wrapper script asset
```

## Mermaid Flow
```mermaid
flowchart TD
    A[scripts/build_packages.sh] --> B[/usr/bin/chat-archive-converter]
    B -->|cd| C[/usr/share/chat-archive-converter]
    B -->|gjs| D[src/main.js]
    D --> E[MainWindow]
```

## Knowledge Graph Sync
- Final topology with corrected wrapper path logged for UUIDv8 `8f0f72f4-7b61-8e4d-bcb3-8f7a821dc9e5`.
