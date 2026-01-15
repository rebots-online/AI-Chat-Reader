# AI Chat Reader - Theme System Architecture

**Version:** 1.0.0
**Copyright:** Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.

---

## Overview

This document defines the architecture for implementing the 9 Windsurf UI themes in AI Chat Reader, as specified in Windsurf-global-rules.md.

### Theme Specifications

| Theme | Description | Primary Colors | Key Design Elements |
|-------|-------------|----------------|---------------------|
| **Kinetic** | Colorful, dynamic, Gumroad-inspired | Pink (#FF6B9D), Purple, Yellow | Smooth animations, playful UI |
| **Brutalist** | Raw, honest, monospace aesthetic | Black (#000), White (#FFF) | System fonts, stark contrast |
| **Retro** | CRT terminal vibes with scanlines | Green (#33FF00) on Black | Scanlines, phosphor glow |
| **Neumorphism** | Soft shadows, extruded surfaces | Off-white (#F0F0F0), Soft gray | Subtle depth, light/dark modes |
| **Glassmorphism** | Frosted glass with depth | Blur effects, semi-transparent | Layered glass planes, blur |
| **Y2K** | Early 2000s web maximalism | Bright gradients, metallic | Bevels, animated GIFs, marquees |
| **Cyberpunk** | Neon-soaked dystopian future | Pink (#FF00FF), Cyan (#00FFFF) | Glitch effects, scanlines |
| **Minimal** | Clean Swiss design | Monochrome + accent color | Whitespace, grid layout |
| **System-Auto** | Follows OS theme preference | OS-dependent | `prefers-color-scheme` |

---

## Architecture

### Directory Structure

```
scripts/
├── assets/
│   ├── themes/
│   │   ├── kinetic/
│   │   │   ├── theme.css
│   │   │   ├── assets/
│   │   │   │   ├── background.svg
│   │   │   │   └── patterns.svg
│   │   │   └── config.json
│   │   ├── brutalist/
│   │   ├── retro/
│   │   ├── neumorphism/
│   │   ├── glassmorphism/
│   │   ├── y2k/
│   │   ├── cyberpunk/
│   │   ├── minimal/
│   │   └── system-auto/
│   │       ├── light.css
│   │       └── dark.css
│   ├── theme-manager.js      # Theme switching logic
│   └── base-styles.css        # Common styles
└── config.py                  # Theme config support

templates/
├── base.html                  # Base template with theme support
├── conversation.html
└── index.html
```

---

## Implementation Plan

### Phase 1: Theme Infrastructure

#### 1.1 Theme Configuration System

**File**: `scripts/assets/themes/theme-config.json`

```json
{
  "default_theme": "kinetic",
  "available_themes": [
    "kinetic",
    "brutalist",
    "retro",
    "neumorphism",
    "glassmorphism",
    "y2k",
    "cyberpunk",
    "minimal",
    "system-auto"
  ],
  "theme_metadata": {
    "kinetic": {
      "name": "Kinetic",
      "description": "Colorful, dynamic design",
      "preview_color": "#FF6B9D"
    },
    "brutalist": {
      "name": "Brutalist",
      "description": "Raw, honest aesthetic",
      "preview_color": "#000000"
    }
  }
}
```

#### 1.2 Theme Selector Component

**File**: `scripts/assets/theme-selector.html`

```html
<div class="theme-selector">
  <label for="theme-select">Theme:</label>
  <select id="theme-select" onchange="switchTheme(this.value)">
    <option value="kinetic">Kinetic</option>
    <option value="brutalist">Brutalist</option>
    <option value="retro">Retro</option>
    <option value="neumorphism">Neumorphism</option>
    <option value="glassmorphism">Glassmorphism</option>
    <option value="y2k">Y2K</option>
    <option value="cyberpunk">Cyberpunk</option>
    <option value="minimal">Minimal</option>
    <option value="system-auto">System Auto</option>
  </select>
</div>
```

#### 1.3 Theme Manager JavaScript

**File**: `scripts/assets/theme-manager.js`

```javascript
class ThemeManager {
  constructor() {
    this.currentTheme = this.getSavedTheme() || 'kinetic';
    this.applyTheme(this.currentTheme);
  }

  getSavedTheme() {
    return localStorage.getItem('chat-archive-theme');
  }

  saveTheme(theme) {
    localStorage.setItem('chat-archive-theme', theme);
  }

  applyTheme(theme) {
    // Remove existing theme CSS
    document.querySelectorAll('link[rel="stylesheet"][data-theme]')
      .forEach(el => el.remove());

    // Add new theme CSS
    if (theme === 'system-auto') {
      this.applySystemTheme();
    } else {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = `assets/themes/${theme}/theme.css`;
      link.dataset.theme = theme;
      document.head.appendChild(link);
    }

    this.currentTheme = theme;
    this.saveTheme(theme);
  }

  applySystemTheme() {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = `assets/themes/system-auto/${prefersDark ? 'dark' : 'light'}.css`;
    link.dataset.theme = 'system-auto';
    document.head.appendChild(link);
  }

  switchTheme(theme) {
    this.applyTheme(theme);
  }
}

// Initialize theme manager
const themeManager = new ThemeManager();

// Global function for theme selector
function switchTheme(theme) {
  themeManager.switchTheme(theme);
}
```

### Phase 2: Theme CSS Implementations

#### 2.1 Base Theme Structure

Each theme CSS file follows this structure:

```css
/**
 * Theme: Kinetic
 * Description: Colorful, dynamic, Gumroad-inspired design
 */

/* CSS Custom Properties */
:root {
  /* Colors */
  --theme-primary: #FF6B9D;
  --theme-secondary: #9B6BFF;
  --theme-accent: #FFD93D;
  --theme-background: #FFFFFF;
  --theme-text: #1A1A2E;
  --theme-text-secondary: #6B7280;

  /* Chat Bubbles */
  --bubble-user-bg: var(--theme-primary);
  --bubble-user-text: #FFFFFF;
  --bubble-assistant-bg: var(--theme-secondary);
  --bubble-assistant-text: #FFFFFF;

  /* UI Elements */
  --border-radius: 12px;
  --shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  /* Typography */
  --font-family: 'Inter', -apple-system, sans-serif;
  --font-size-base: 16px;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  :root {
    --theme-background: #1A1A2E;
    --theme-text: #F9FAFB;
    --theme-text-secondary: #9CA3AF;
  }
}

/* Component styles */
.chat-bubble {
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  transition: var(--transition);
}

.chat-bubble:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

/* Theme-specific animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-message {
  animation: fadeIn 0.3s ease-out;
}
```

#### 2.2 Theme-Specific Implementations

**Kinetic Theme** (`kinetic/theme.css`):
```css
:root {
  --theme-primary: #FF6B9D;
  --theme-secondary: #9B6BFF;
  --theme-accent: #FFD93D;
  --gradient: linear-gradient(135deg, #FF6B9D 0%, #9B6BFF 100%);
  --bubble-shape: 20px;
  --animation-duration: 0.3s;
}
```

**Brutalist Theme** (`brutalist/theme.css`):
```css
:root {
  --theme-primary: #000000;
  --theme-secondary: #FFFFFF;
  --theme-accent: #FF0000;
  --font-family: 'Courier New', monospace;
  --border-radius: 0;
  --border: 2px solid #000;
  --shadow: none;
}
```

**Retro Theme** (`retro/theme.css`):
```css
:root {
  --theme-primary: #33FF00;
  --theme-background: #000000;
  --theme-text: #33FF00;
  --font-family: 'VT323', monospace;
  --scanline-color: rgba(0, 255, 0, 0.1);
}

/* Scanline effect */
.chat-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    var(--scanline-color) 2px,
    var(--scanline-color) 4px
  );
  pointer-events: none;
}

/* Phosphor glow */
.chat-bubble {
  text-shadow: 0 0 5px var(--theme-primary);
  box-shadow: 0 0 10px var(--theme-primary);
}
```

**Neumorphism Theme** (`neumorphism/theme.css`):
```css
:root {
  --theme-background: #E8EBF0;
  --theme-text: #2D3748;
  --light-source: 135deg;
  --shadow-light: #FFFFFF;
  --shadow-dark: #B8BCC8;
}

.chat-bubble {
  background: var(--theme-background);
  box-shadow:
    8px 8px 16px var(--shadow-dark),
    -8px -8px 16px var(--shadow-light);
  border-radius: 20px;
  border: none;
}
```

**Glassmorphism Theme** (`glassmorphism/theme.css`):
```css
:root {
  --blur-amount: 20px;
  --glass-bg: rgba(255, 255, 255, 0.2);
  --glass-border: rgba(255, 255, 255, 0.3);
}

.chat-bubble {
  background: var(--glass-bg);
  backdrop-filter: blur(var(--blur-amount));
  -webkit-backdrop-filter: blur(var(--blur-amount));
  border: 1px solid var(--glass-border);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}
```

**Y2K Theme** (`y2k/theme.css`):
```css
:root {
  --theme-primary: #0099FF;
  --theme-secondary: #FF00CC;
  --gradient: linear-gradient(180deg, #0099FF 0%, #FF00CC 100%);
  --bevel-light: #FFFFFF;
  --bevel-dark: #000000;
}

.chat-bubble {
  background: var(--gradient);
  border: 3px outset #CCCCCC;
  box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.5);
}

@keyframes rainbow {
  0% { filter: hue-rotate(0deg); }
  100% { filter: hue-rotate(360deg); }
}

.header {
  animation: rainbow 10s linear infinite;
}
```

**Cyberpunk Theme** (`cyberpunk/theme.css`):
```css
:root {
  --theme-primary: #FF00FF;
  --theme-secondary: #00FFFF;
  --theme-background: #0A0A0A;
  --theme-text: #00FF00;
  --glitch-color: #FF0000;
}

@keyframes glitch {
  0%, 100% { transform: translate(0); }
  20% { transform: translate(-2px, 2px); }
  40% { transform: translate(-2px, -2px); }
  60% { transform: translate(2px, 2px); }
  80% { transform: translate(2px, -2px); }
}

.chat-bubble:hover {
  animation: glitch 0.3s ease-in-out;
}

/* Neon glow */
.chat-bubble.user {
  box-shadow: 0 0 10px var(--theme-primary),
              0 0 20px var(--theme-primary);
  text-shadow: 0 0 5px var(--theme-primary);
}
```

**Minimal Theme** (`minimal/theme.css`):
```css
:root {
  --theme-primary: #000000;
  --theme-background: #FFFFFF;
  --theme-text: #1A1A1A;
  --border-color: #E5E5E5;
  --font-family: 'Helvetica Neue', Arial, sans-serif;
  --whitespace: 2rem;
}

.chat-container {
  max-width: 680px;
  margin: 0 auto;
  padding: var(--whitespace);
}

.chat-bubble {
  border: 1px solid var(--border-color);
  box-shadow: none;
  border-radius: 4px;
}
```

**System-Auto Theme** (`system-auto/light.css`, `system-auto/dark.css`):
```css
/* light.css */
:root {
  --theme-background: #FFFFFF;
  --theme-text: #1A1A1A;
  --theme-border: #E5E5E5;
}

/* dark.css */
:root {
  --theme-background: #1A1A1A;
  --theme-text: #F9FAFB;
  --theme-border: #374151;
}
```

---

## Integration Steps

### Step 1: Update HTML Generator

Modify `scripts/generators/html_generator.py`:

```python
class HTMLGenerator:
    def __init__(self, templates_dir, assets_dir, theme='kinetic'):
        self.theme = theme
        # ... existing code

    def generate_conversation_html(self, conversation, output_path, theme=None):
        """Generate HTML with theme support."""
        theme = theme or self.theme

        context = {
            'conversation': conversation,
            'theme': theme,
            'theme_selector': self._generate_theme_selector(theme),
        }

        template = self.env.get_template('conversation.html')
        html = template.render(**context)

        Path(output_path).write_text(html, encoding='utf-8')
```

### Step 2: Update Templates

Modify `scripts/templates/base.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Chat Archive{% endblock %}</title>

    <!-- Base Styles -->
    <link rel="stylesheet" href="assets/base-styles.css">

    <!-- Theme CSS -->
    <link rel="stylesheet" href="assets/themes/{{ theme }}/theme.css" data-theme="{{ theme }}">
</head>
<body class="theme-{{ theme }}">
    {% block content %}{% endblock %}

    <!-- Theme Manager -->
    <script src="assets/theme-manager.js"></script>
</body>
</html>
```

### Step 3: Add CLI Support

Modify `scripts/convert_to_html.py`:

```python
def main():
    """Main entry point."""
    print_version_banner()

    parser = argparse.ArgumentParser(
        description="Convert chat archives to HTML and optionally GIFs/PDFs/PNGs/SVGs."
    )
    parser.add_argument('--gif', action='store_true', help='Generate animated GIF')
    parser.add_argument('--pdf', action='store_true', help='Generate PDF')
    parser.add_argument('--png', action='store_true', help='Generate PNG')
    parser.add_argument('--svg', action='store_true', help='Generate SVG')
    parser.add_argument(
        '--theme',
        choices=['kinetic', 'brutalist', 'retro', 'neumorphism', 'glassmorphism',
                 'y2k', 'cyberpunk', 'minimal', 'system-auto'],
        default=os.environ.get('CHAT_THEME', 'kinetic'),
        help='Theme for generated HTML (default: kinetic, env: CHAT_THEME)'
    )
    args = parser.parse_args()

    converter = ChatArchiveConverter(theme=args.theme)
    success = converter.convert(args)
    sys.exit(0 if success else 1)
```

### Step 4: Update Config

Modify `scripts/config.py`:

```python
@dataclass
class Config:
    # ... existing fields ...

    # Theme configuration
    default_theme: str = "kinetic"
    enable_theme_selector: bool = True

    @classmethod
    def from_env(cls, project_root: Optional[Path] = None) -> "Config":
        # ... existing code ...

        return cls(
            # ... existing fields ...
            default_theme=os.environ.get("CHAT_THEME", "kinetic"),
            enable_theme_selector=os.environ.get("CHAT_THEME_SELECTOR", "true").lower() == "true",
        )
```

---

## Testing Plan

### Theme Testing Checklist

For each theme, verify:
- [ ] Color scheme is visually correct
- [ ] Typography is readable
- [ ] Chat bubbles are properly styled
- [ ] Hover effects work as expected
- [ ] Dark mode (if supported) functions
- [ ] Animations are smooth
- [ ] No layout breakage
- [ ] Mobile responsive
- [ ] Accessibility (contrast, focus indicators)

### Cross-Browser Testing

Test in:
- Chrome/Edge (Chromium)
- Firefox
- Safari (if available)
- Mobile browsers (responsive design)

---

## Performance Considerations

1. **CSS File Size**: Each theme CSS should be <50KB
2. **Animation Performance**: Use `transform` and `opacity` for smooth animations
3. **Asset Loading**: Lazy-load theme assets if large
4. **Caching**: Cache selected theme in localStorage

---

## Future Enhancements

1. **Custom Themes**: Allow users to define custom themes
2. **Theme Editor**: Visual theme builder
3. **Theme Marketplace**: Shareable theme files
4. **Dynamic Theme Switching**: Live preview without reload
5. **Accessibility-First Themes**: High contrast, reduced motion variants

---

**Document Version:** 1.0.0
**Last Updated:** 2025-01-14
**Maintained By:** Robin L. M. Cheung, MBA
