# AI Chat Reader - GNOME GUI Implementation Checklist (Revised)

This checklist details the implementation steps for the GNOME GUI front-end, which serves as a configuration and execution launcher for OpenAI and Anthropic chat export conversion scripts. This GUI is *not* an interactive chat application.

Each item specifies required components, filenames, dependencies, and intended outcomes to facilitate precise, 'filling-in-the-blanks' coding.

## 1. Application Core

### 1.1 Application Entry Point
- [x] Update `src/main.js` to properly initialize the `Adw.Application` and `MainWindow`.
  - Defines `AI_Chat_Reader_App` class extending `Adw.Application`.
  - Implements `vfunc_startup()` to set up application actions and `vfunc_activate()` to create and show the main window.
  - Handles application lifecycle (startup, activation, shutdown).

### 1.2 Main Application Window
- [x] Create `src/widgets/MainWindow.js` for the main application window.
  - Extends `Adw.ApplicationWindow`.
  - Contains a `Gtk.Box` (vertical orientation) as the main container.
  - Appends `HeaderBar` to the top.
  - Appends `ConfigView` (main content area) below the `HeaderBar`.
  - Appends `LogView` (for output display) below `ConfigView`.
  - Sets up window title and default size.

### 1.3 Application Header Bar
- [x] Create `src/widgets/HeaderBar.js` for the application's header bar.
  - Extends `Gtk.HeaderBar`.
  - Sets application title (e.g., "AI Chat Reader Converter").
  - Includes a `Gtk.MenuButton` for application-wide settings (e.g., "About", "Preferences").

## 2. Configuration Interface

### 2.1 Configuration View
- [/] Create `src/widgets/ConfigView.js` to manage conversion settings.
  - Extends `Gtk.Box` (vertical orientation).
  - Contains sections for input file, output directory, and conversion options.
  - Uses `Gtk.Grid` or `Gtk.Box` for layout of controls.
  - Emits signals when conversion parameters change or 'Execute' button is clicked.

### 2.2 Input File Selector
- [x] Implement input file selection within `ConfigView`.
  - Required elements: `Gtk.Entry` for displaying path, `Gtk.Button` to open file chooser.
  - Uses `Gtk.FileChooserNative` for file selection.
  - Filters for `.json` files (OpenAI, Anthropic exports).
  - Stores selected file path in `SettingsModel`.

### 2.3 Output Directory Selector
- [x] Implement output directory selection within `ConfigView`.
  - Required elements: `Gtk.Entry` for displaying path, `Gtk.Button` to open folder chooser.
  - Uses `Gtk.FileChooserNative` for folder selection.
  - Stores selected directory path in `SettingsModel`.

### 2.4 Conversion Options
- [x] Implement conversion options within `ConfigView`.
  - Example elements: `Gtk.CheckButton` for specific formats (e.g., "Markdown Output"), `Gtk.ComboBoxText` for other options.
  - Stores selected options in `SettingsModel`.

### 2.5 Execute Button
- [x] Implement an "Execute Conversion" button within `ConfigView`.
  - Required element: `Gtk.Button`.
  - Connects to a method that gathers all current configuration from `ConfigView`.
  - Emits a signal (e.g., `execute-conversion`) with the collected parameters.

## 3. Output and Logging

### 3.1 Log View
- [x] Create `src/widgets/LogView.js` to display script output and logs.
  - Extends `Gtk.ScrolledWindow` containing a `Gtk.TextView`.
  - `Gtk.TextView` should be read-only.
  - Provides methods to `append_log(message)` and `clear_log()`.
  - Automatically scrolls to the bottom when new content is added.

## 4. Data Management and Integration

### 4.1 Settings Model
- [x] Create `src/models/SettingsModel.js` to manage application settings.
  - Uses `Gio.Settings` for persistent storage.
  - Defines schema for settings (e.g., `org.gnome.AI-Chat-Reader.gschema.xml`).
  - Provides methods to get and set `input_file_path`, `output_directory_path`, `conversion_options`.

### 4.2 File Manager Utility
- [x] Create `src/utils/FileManager.js` for file system interactions.
  - Provides static methods for opening file/folder choosers (`open_file_chooser()`, `open_folder_chooser()`).
  - Handles `Gtk.FileChooserNative` instantiation and response.

### 4.3 Process Manager Utility
- [x] Create `src/utils/ProcessManager.js` for executing external scripts.
  - Provides a method `execute_script(script_path, args)`.
  - Captures `stdout` and `stderr` of the executed script.
  - Emits signals for `output_received(line)` and `process_finished(exit_code)`.
  - Ensures non-blocking execution.

### 4.4 Notification Manager Utility
- [x] Create `src/utils/NotificationManager.js` for sending desktop notifications.
  - Provides a static method `show_notification(title, body)`.
  - Uses `Gio.Notification`.
- [x] Integrate `NotificationManager` into `MainWindow` to send notifications upon script completion or failure.

## 5. Build and Packaging

### 5.1 Meson Build System
- [X] Update `meson.build` and `meson_options.txt`.
  - Configure for new source files and structure.
  - Ensure correct installation paths.

### 5.2 GSchema Compilation
- [X] Ensure `gschema.xml` is compiled during build process.
  - Created `data/org.gnome.AI-Chat-Reader.gschema.xml`

### 5.3 .deb Package
- [X] Build GNOME app as .deb package via `scripts/build.py`
  - Output: `dist/ai-chat-reader-gnome-{version}-{build}-all.deb`

### 5.4 AppImage Package
- [X] Build GNOME app as AppImage via `scripts/build.py`
  - Output: `dist/AI-Chat-Reader-{version}-{build}-x86_64.AppImage`

### 5.5 Flatpak Packaging
- [ ] Update `flatpak/org.gnome.AI-Chat-Reader.yaml`.
  - Reflect new file structure and dependencies.

## 6. Testing and Validation

### 6.1 Unit Tests
- [ ] Write unit tests for `SettingsModel`, `FileManager`, `ProcessManager`.

### 6.2 Integration Tests
- [ ] Write integration tests for `ConfigView` and `LogView` interaction.

### 6.3 Manual Testing
- [ ] Verify GUI functionality: file selection, option setting, script execution, log display, notifications.

## 7. Documentation

### 7.1 User Documentation
- [ ] Create `docs/user/usage.md` explaining how to use the GUI.

### 7.2 Developer Documentation
- [ ] Update `README.md` with build and run instructions for the GUI.
