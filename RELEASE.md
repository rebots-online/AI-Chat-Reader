# AI Chat Reader - Release Documentation

**Version:** 1.0.0
**Build:** Auto-generated from epoch time
**Copyright:** Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.

---

## Quick Start

### CLI Binary (Linux)

```bash
# Download the binary
wget https://github.com/rebots-online/AI-Chat-Reader/releases/download/v1.0.0/chat-archive-converter-v1.0.0-build-XXXXX

# Make executable
chmod +x chat-archive-converter-v1.0.0-build-XXXXX

# Prepare your data
mkdir -p ~/chat-archive/data/raw
cp ~/Downloads/openai_conversations.json ~/chat-archive/data/raw/

# Run the converter
cd ~/chat-archive
./chat-archive-converter-v1.0.0-build-XXXXX
```

### .deb Package (Debian/Ubuntu)

```bash
# Download and install
wget https://github.com/rebots-online/AI-Chat-Reader/releases/download/v1.0.0/chat-archive-converter-1.0.0-amd64.deb
sudo dpkg -i chat-archive-converter-1.0.0-amd64.deb
sudo apt-get install -f  # Fix any missing dependencies

# Run from anywhere
chat-archive-converter
```

---

## Build Process

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AI-Chat-Reader Build Pipeline                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │ Python Src   │───→│ PyInstaller  │───→│ CLI Binary   │          │
│  │ scripts/     │    │ Spec File    │    │ 52MB ELF    │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │ CLI Binary   │───→│ dpkg-deb     │───→│ .deb Package │          │
│  │ + Templates  │    │ Control File │    │ Ready to install│     │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Build Commands

```bash
# 1. Install build dependencies
pip install pyinstaller
pip install -r requirements.txt

# 2. Build CLI binary
pyinstaller scripts/cli.spec

# 3. Build .deb package
python scripts/build.py
```

---

## Packages Generated

| Package | Platform | Size | Status |
|---------|----------|------|--------|
| `chat-archive-converter-v1.0.0-build-XXXXX` | Linux CLI | ~52MB | ✅ Working |
| `chat-archive-converter-1.0.0-amd64.deb` | Debian/Ubuntu | ~52MB | ✅ Working |
| `*.AppImage` | Linux Portable | TBD | ⚠️ Requires appimagetool |

---

## Usage Instructions

### CLI Binary Usage

The CLI binary uses the following directory structure by default:

```
chat-archive/
├── data/
│   ├── raw/           # ← Place your JSON files here
│   │   ├── openai_conversations.json
│   │   └── claude_conversations.json
│   └── html/          # ← Output HTML appears here
└── chat-archive-converter  # Binary
```

**Supported file names:**
- OpenAI: `openai_conversations.json`, `chatgpt_conversations.json`
- Anthropic: `claude_conversations.json`, `anthropic_conversations.json`

**Environment Variables:**

```bash
# Override default data directory
export CHAT_DATA_DIR=/path/to/data
export CHAT_RAW_DIR=/path/to/raw
export CHAT_OUTPUT_DIR=/path/to/output

# Run with custom paths
chat-archive-converter
```

### Output Files

After running, you'll find:
- `index.html` - Main index page with all conversations
- `conversation-*.html` - Individual conversation pages
- `assets/` - CSS, JavaScript, and icons

---

## Installation Methods

### Method 1: Standalone Binary (No Installation)

```bash
# Download
wget https://github.com/rebots-online/AI-Chat-Reader/releases/download/v1.0.0/chat-archive-converter-v1.0.0-build-XXXXX

# Run
chmod +x chat-archive-converter-v1.0.0-build-XXXXX
./chat-archive-converter-v1.0.0-build-XXXXX
```

### Method 2: Debian Package (System-wide)

```bash
# Download and install
wget https://github.com/rebots-online/AI-Chat-Reader/releases/download/v1.0.0/chat-archive-converter-1.0.0-amd64.deb
sudo dpkg -i chat-archive-converter-1.0.0-amd64.deb
sudo apt-get install -f

# Run
chat-archive-converter
```

### Method 3: Source (Development)

```bash
# Clone repository
git clone https://github.com/rebots-online/AI-Chat-Reader.git
cd AI-Chat-Reader

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python scripts/convert_to_html.py
```

---

## Build System

### Version Number Format

```
v<major>.<minor>[.<patch>][-<prerelease>] Build <epoch%100, 5-digit>

Example: v1.0.0 Build 43052
         │   │    │     │       └─ Minutes (0-59)
         │   │    │     └─ Day counter (0-99)
         │   │    └─ Patch version
         │   └─ Minor version
         └─ Major version
```

### Build Script

```bash
# Full build (CLI + .deb)
python scripts/build.py

# Spec file build (CLI only)
pyinstaller scripts/cli.spec
```

---

## Troubleshooting

### Binary fails with "No module named 'jinja2'"

**Cause:** Dependencies not packaged correctly
**Solution:** Use the .deb package or rebuild with all dependencies installed

### "No input files found!" error

**Cause:** No JSON files in the expected location
**Solution:** Place your `openai_conversations.json` or `claude_conversations.json` in `data/raw/` directory

### Build fails with "appimagetool not found"

**Cause:** AppImage requires additional setup
**Solution:** Skip AppImage build and use CLI binary or .deb package

---

## Development

### Project Structure

```
AI-Chat-Reader/
├── VERSION                 # Version number
├── scripts/
│   ├── build.py          # Main build script
│   ├── cli.spec          # PyInstaller spec file
│   ├── config.py         # Centralized configuration
│   ├── convert_to_html.py # Main CLI entry point
│   ├── parsers/          # OpenAI/Anthropic parsers
│   ├── generators/       # HTML/GIF generators
│   └── templates/        # Jinja2 templates
├── src/                  # GNOME GUI (GJS)
│   ├── main.js
│   ├── widgets/
│   └── models/
└── requirements.txt      # Python dependencies
```

### Adding New Features

1. **Parser changes:** Edit `scripts/parsers/*.py`
2. **Template changes:** Edit `scripts/templates/*.html`
3. **Configuration:** Edit `scripts/config.py`
4. **Build changes:** Edit `scripts/build.py` or `scripts/cli.spec`

---

## Release Checklist

- [x] VERSION file created
- [x] Copyright notices added to all Python files
- [x] Duplicate handleSearch() function removed
- [x] Specific exception handling added to parsers
- [x] Centralized configuration system created
- [x] PyInstaller build script with spec file
- [x] CLI binary built and tested
- [x] .deb package built and tested
- [x] Release documentation created

---

## Next Steps

1. **Create GitHub Release** with tagged version
2. **Upload packages** to GitHub Releases
3. **Update README.md** with release links
4. **Create AppImage** for portable Linux distribution
5. **Consider Tauri 2** for cross-platform desktop app

---

## Support

For issues, questions, or contributions:
- GitHub: https://github.com/rebots-online/AI-Chat-Reader
- License: All Rights Reserved

---

**Built with ❤️ and PyInstaller**
