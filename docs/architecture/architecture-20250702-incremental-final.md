# Architecture Snapshot - 2025-07-02 (After Incremental Script)

```mermaid
graph TD
    A[scripts/convert_to_html.py] --> B{Generators}
    B --> C[html_generator.py]
    B --> D[index_generator.py]
    B --> E[asset_manager.py]
    B --> F[gif_generator.py]
    A --> G{Parsers}
    G --> H[openai_parser.py]
    G --> I[anthropic_parser.py]
    A --> J[data/raw]
    C --> K[data/html]
    A --> L[build_packages.sh]
    L --> M[PyInstaller]
    L --> N[DEB/AppImage]
    O[scripts/process_openai_delta.py] --> H
    O --> C
    O --> D
    O --> E
```
