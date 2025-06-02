# HTML Chat Archive Converter

Convert your Anthropic (Claude) and OpenAI (ChatGPT) chat archives into beautiful HTML files with iOS-style chat bubbles, light/dark mode support, and excellent navigation features.

## Features

- **iOS-Style Chat Interface**: Beautiful chat bubbles with proper alignment (user messages on right, assistant on left)
- **Light/Dark Mode**: Toggle between themes with persistent preferences
- **Search & Filter**: Full-text search across all conversations with filtering by source and date
- **Responsive Design**: Works perfectly on mobile and desktop devices
- **Ready-to-Deploy**: Generates a complete zip package that can be uploaded to any web server
- **Navigation**: Chronological organization with breadcrumb navigation and previous/next links
- **Copy Functionality**: Easy copying of individual messages
- **Statistics**: Overview of total conversations, messages, and date ranges

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare Your Data**
   Place your JSON export files in the `data/raw/` directory:
   - `claude_conversations.json` (or `anthropic_conversations.json`)
   - `openai_conversations.json` (or `chatgpt_conversations.json`)

3. **Run the Converter**
   ```bash
   python scripts/convert_to_html.py
   ```

4. **View Your Archive**
   Open the generated `index.html` file in your browser or deploy the zip package to a web server.

## Output Structure

The converter creates a timestamped folder with the following structure:

```
data/html/chat_export_YYYYMMDD_HHMMSS/
├── index.html                    # Main navigation page
├── assets/
│   ├── style.css                 # iOS-style styling with themes
│   ├── script.js                 # Search, filtering, theme toggle
│   ├── favicon.svg               # Site icon
│   ├── manifest.json             # Web app manifest
│   └── robots.txt                # SEO configuration
├── anthropic/
│   ├── index.html                # Anthropic conversations index
│   └── conversations/
│       ├── conversation_1.html
│       └── ...
└── openai/
    ├── index.html                # OpenAI conversations index
    └── conversations/
        ├── conversation_1.html
        └── ...
```

## How to Get Your Chat Exports

### Anthropic (Claude)
1. Go to [Claude Settings](https://claude.ai/settings)
2. Navigate to "Data Export"
3. Request your data export
4. Download the JSON file when ready
5. Rename to `claude_conversations.json` and place in `data/raw/`

### OpenAI (ChatGPT)
1. Go to [ChatGPT Settings](https://chatgpt.com/settings)
2. Navigate to "Data Controls" → "Export Data"
3. Request your data export
4. Download and extract the ZIP file
5. Find `conversations.json` and rename to `openai_conversations.json`
6. Place in `data/raw/`

## Usage Examples

### Basic Conversion
```bash
python scripts/convert_to_html.py
```

### View Results
```bash
# Open in default browser (macOS)
open data/html/chat_export_*/index.html

# Open in default browser (Linux)
xdg-open data/html/chat_export_*/index.html

# Open in default browser (Windows)
start data/html/chat_export_*/index.html
```

### Deploy to Web Server
```bash
# Extract the generated zip file to your web server
unzip data/html/chat_export_*.zip -d /path/to/webserver/
```

## Features in Detail

### iOS-Style Chat Interface
- **User messages**: Blue bubbles aligned to the right
- **Assistant messages**: Gray bubbles aligned to the left  
- **System messages**: Centered with subtle styling
- **Timestamps**: Displayed for each message
- **Copy buttons**: Hover over messages to copy content

### Theme System
- **Light mode**: Clean white background with dark text
- **Dark mode**: Black background with light text
- **Persistent preferences**: Theme choice saved in browser
- **Smooth transitions**: Animated theme switching

### Search & Navigation
- **Real-time search**: Filter conversations as you type
- **Source filtering**: Show only OpenAI or Anthropic conversations
- **Date sorting**: Sort by newest/oldest, title, or message count
- **Breadcrumb navigation**: Easy navigation between pages
- **Statistics overview**: Total conversations, messages, and date ranges

### Mobile Support
- **Responsive design**: Optimized for all screen sizes
- **Touch-friendly**: Large tap targets and smooth scrolling
- **Mobile search**: Optimized search experience on mobile devices

## Technical Details

### Architecture
- **Modular design**: Separate parsers for each chat format
- **Template-based**: Jinja2 templates for consistent HTML generation
- **Asset management**: Automated copying and organization of CSS/JS/icons
- **Error handling**: Graceful handling of malformed data

### Browser Compatibility
- **Modern browsers**: Chrome, Firefox, Safari, Edge (latest versions)
- **JavaScript**: Vanilla JS for maximum compatibility
- **CSS**: Modern CSS with fallbacks for older browsers
- **No server required**: Pure client-side functionality

### Performance
- **Efficient parsing**: Handles thousands of conversations
- **Lazy loading**: Optimized for large conversation lists
- **Minimal dependencies**: Only requires Jinja2 for generation
- **Fast search**: Client-side search with instant results

## Troubleshooting

### Common Issues

**No input files found**
- Ensure JSON files are in `data/raw/` directory
- Check filename matches expected patterns
- Verify file is valid JSON format

**Import errors**
- Run `pip install -r requirements.txt`
- Ensure you're using Python 3.7+

**Timezone comparison errors**
- This is automatically handled in the latest version
- Timestamps are normalized to be timezone-naive

**Large file processing**
- The converter handles thousands of conversations efficiently
- For very large exports (>10k conversations), processing may take a few minutes

### Getting Help

If you encounter issues:
1. Check the console output for specific error messages
2. Verify your JSON files are valid and complete
3. Ensure all dependencies are installed correctly
4. Try with a smaller subset of data first

## Development

### Project Structure
```
scripts/
├── convert_to_html.py           # Main conversion script
├── parsers/                     # Data parsing modules
│   ├── base_parser.py          # Abstract base parser
│   ├── anthropic_parser.py     # Anthropic format parser
│   └── openai_parser.py        # OpenAI format parser
├── generators/                  # HTML generation modules
│   ├── html_generator.py       # Individual conversation pages
│   ├── index_generator.py      # Navigation index pages
│   └── asset_manager.py        # Static asset management
├── templates/                   # Jinja2 HTML templates
│   ├── conversation.html       # Individual conversation template
│   └── index.html             # Index page template
└── assets/                     # Static assets
    ├── style.css              # Main stylesheet
    └── script.js              # Main JavaScript
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with sample data
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by iOS Messages app design
- Built with modern web standards
- Designed for privacy and offline use
