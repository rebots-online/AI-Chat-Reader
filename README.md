# Chat HTML Generator

Transform your OpenAI or Anthropic chat exports into static, navigable HTML pages with ease.

---

## 🚀 Overview

This repository provides a single‑script solution to:

1. **Scan** a folder of JSON chat exports (OpenAI or Anthropic).
2. **Parse** each conversation into timestamped messages.
3. **Render** one standalone HTML file per conversation, styled as chat bubbles.
4. **Generate** a top‑level `index.html` that lists all conversations chronologically.

Whether you want to archive your AI interactions, share them on a static site, or simply browse them offline, this tool makes it quick and customizable.

---

## 🔧 Features

* **Universal Compatibility**: Works with OpenAI JSON exports (v1 mapping format) and can be extended to Anthropic exports by adjusting a single parser function.
* **Automatic Timestamps**: Each message displays its creation date/time, and the filename itself is prefixed by the conversation’s creation timestamp.
* **Chat‑Bubble Styling**: User and assistant messages are visually distinct. Easy-to‑customize CSS variables let you swap colors, fonts, and bubble shapes.
* **Chronological Index**: An `index.html` is generated that links to each conversation file, sorted by date.
* **Minimal Dependencies**: Pure Python (≥3.7) with only the standard library—no external packages required.

---

## 📥 Installation

1. **Clone this repo**:

   ```bash
   git clone https://github.com/yourusername/chat-html-generator.git
   cd chat-html-generator
   ```

2. **Ensure Python 3.7+ is installed**. Check with:

   ```bash
   python3 --version
   ```

3. (Optional) Create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Make the script executable** (optional):

   ```bash
   chmod +x generate_chat_html.py
   ```

That’s it—no other dependencies needed.

---

## 🏃 Usage

Run the script, pointing to your folder of JSON exports and an output folder where HTML will be written:

```bash
python3 generate_chat_html.py \
  --input-folder /path/to/json_exports \
  --output-folder /path/to/html_output
```

* `--input-folder`: Directory containing one or more `.json` files (either OpenAI exports, a list of exports, or custom Anthropic exports).
* `--output-folder`: Directory where the generated `.html` files (and `index.html`) will be placed. Will be created if it doesn’t exist.

Example:

```bash
python3 generate_chat_html.py \
  --input-folder ~/Downloads/openai_chats \
  --output-folder ~/site/conversations
```

Once it finishes, open `~/site/conversations/index.html` in your browser to see your sorted archive.

### 🔍 Customizing the Appearance

By default, the script inlines CSS variables at the top of each HTML. To tweak:

1. **Open** `generate_chat_html.py` in your favorite editor.
2. Look for the `USER_BACKGROUND`, `ASSISTANT_BACKGROUND`, and other style constants at the top:

   ```python
   USER_BG       = "#daf1da"     # user chat bubble background color
   ASSISTANT_BG  = "#f1f1f1"     # assistant bubble background color
   USER_COLOR    = "#000000"     # user text color
   ASSIST_COLOR  = "#000000"     # assistant text color
   FONT_FAMILY   = "Arial, sans-serif"
   BODY_BG       = "#ffffff"
   BORDER_RADIUS = "12px"
   ```
3. **Modify** any hex code, font, or radius value to match your brand or personal taste.
4. (Advanced) Extract the entire `<style>…</style>` block into a separate `theme.css` file, then replace the inline CSS with a `<link rel="stylesheet" href="theme.css">` in the template.

---

## 🛠️ Extending for Anthropic or Other Formats

If you have a different JSON structure (e.g., from Anthropic), update the `parse_anthropic_conv()` function:

```python

def parse_anthropic_conv(conv: dict) -> dict:
    # Example: conv might be a list of messages:
    #    [ { "sender": "human", "timestamp": …, "text": … }, … ]
    if isinstance(conv, list):
        messages = []
        for m in conv:
            role = "user" if m.get("sender") == "human" else "assistant"
            ts = m.get("timestamp", 0)
            content = m.get("text", "").strip()
            if content:
                messages.append({"role": role, "ts": ts, "content": content})
        messages.sort(key=lambda msg: msg["ts"])
        return {
            "title": "Anthropic Conversation",
            "create_ts": messages[0]["ts"] if messages else 0,
            "messages": messages
        }
    # … add other parsing rules as needed …
    return {"title": "(unparsed)", "create_ts": 0, "messages": []}
```

With that function producing the same shape as the OpenAI parser, the rendering logic remains identical.

---

## 📤 Exporting Conversations

Use `scripts/export_conversations.py` to convert selected chats to PDF, DOCX, Excel, CSV, Markdown or plain text.

```bash
python scripts/export_conversations.py --match "search text" --formats pdf,docx,md --output exports
```


## 📂 Repository Structure

```
chat-html-generator/
├── generate_chat_html.py    # Core script that generates HTML
├── example_openai_conversations.json  # Sample export for testing
└── README.md                # <-- You’re here!
```

* **`generate_chat_html.py`**: Walks input folder, parses each JSON, renders HTML.
* **`example_openai_conversations.json`**: A small sample export for smoke-testing.

---

## 🤝 Contributing

1. **Fork** this repo and create a descriptive branch (e.g. `feature/anthropic-support`).
2. **Commit** changes with clear messages.
3. **Submit a Pull Request** against `main`. We’ll review and merge!
4. Feel free to open issues if you:

   * Discover a bug.
   * Need help with a custom use case.
   * Have a styling or usability suggestion.

---

## 💳 Licensing via RevenueCat

The optional module `scripts/revenuecat_client.py` provides a lightweight wrapper around the RevenueCat REST API for verifying lifetime and subscription purchases. Set `REVENUECAT_API_KEY` and call its methods within your automation.

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

* Inspired by [convert\_openai\_chats.py](#) and community feedback.
* Built with ❤️ and pure Python.

---

*Happy archiving!* 🎉
