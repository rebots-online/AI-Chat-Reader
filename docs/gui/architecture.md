# AI Chat Reader - GNOME GUI Architecture (Revised)

## Overview
This document outlines the revised architecture for the GNOME GUI front-end of the AI Chat Reader application, designed to run on Ubuntu. The primary purpose of this GUI is to provide a user-friendly interface for configuring and executing scripts that convert OpenAI and Anthropic chat exports. It is *not* an interactive chat application.

The front-end is built using GTK4 and libadwaita, following GNOME Human Interface Guidelines (HIG) for a native GNOME experience.

## Architecture Components

### 1. Core Components

#### 1.1 Application Window (`MainWindow`)
- Main application window following GNOME HIG.
- `HeaderBar` with application title and global actions (e.g., settings).
- Main content area for configuration and execution controls.

#### 1.2 Configuration Interface (`ConfigView`)
- Provides UI elements for setting conversion parameters.
- **Input File Selection**: Button/entry for selecting the source chat export file (OpenAI JSON, Anthropic JSON).
- **Output Directory Selection**: Button/entry for selecting the destination directory for converted files.
- **Conversion Options**: Checkboxes/radio buttons for specific conversion parameters (e.g., format, filtering).
- **Script Execution Button**: Triggers the conversion process.

#### 1.3 Output/Log Display (`LogView`)
- Displays real-time output and logs from the executed conversion scripts.
- Read-only text area for displaying success/failure messages, errors, and progress.

### 2. Data Management

#### 2.1 Settings Model (`SettingsModel`)
- Manages application preferences and last-used paths.
- Persists configuration settings (e.g., default input/output directories, last-used conversion options).

#### 2.2 Script Integration
- Handles communication with the external conversion scripts.
- Passes configuration parameters to the scripts.
- Captures and streams script output to the `LogView`.

### 3. Integration Layer

#### 3.1 System Integration
- `FileManager`: Handles file dialogs for input file and output directory selection.
- `ProcessManager`: Manages the execution of external conversion scripts and captures their stdout/stderr.
- `NotificationManager`: Handles desktop notifications for conversion completion/errors.

## Technical Stack

### Frontend
- **GTK4**: Primary UI toolkit.
- **libadwaita**: For modern GNOME UI components.
- **GJS**: JavaScript bindings for GTK.

### Data Management
- **Gio.Settings**: For application settings persistence.
- **JSON-GLib**: For configuration and data serialization (if needed for complex settings).

### Development Tools
- **Meson**: Build system.
- **Flatpak**: For packaging and distribution.
- **GJS Console**: For debugging.

## Data Flow (Revised)

1. User opens `MainWindow`.
2. `ConfigView` loads saved settings via `SettingsModel`.
3. User selects input file, output directory, and sets conversion options.
4. User clicks 'Execute' button.
5. `ProcessManager` is invoked, launching the conversion script with provided parameters.
6. `ProcessManager` captures script output and streams it to `LogView`.
7. Upon script completion, `NotificationManager` provides feedback.
8. `SettingsModel` saves updated preferences.

## Security Considerations

- Ensure proper sandboxing for script execution (e.g., Flatpak).
- Validate user inputs to prevent command injection.
- Handle sensitive data (if any) securely.

## Performance Considerations

- Asynchronous script execution to keep UI responsive.
- Efficient streaming of logs to prevent UI freezes.

## Future Extensions

- Batch conversion capabilities.
- Support for additional chat export formats.
- User-defined custom conversion scripts.
