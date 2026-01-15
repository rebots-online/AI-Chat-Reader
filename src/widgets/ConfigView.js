const Gtk = imports.gi.Gtk;
const Adw = imports.gi.Adw;
const GObject = imports.gi.GObject;
const SettingsModel = imports.models.SettingsModel._SettingsModel;
const FileManager = imports.utils.FileManager._FileManager;

const ConfigView = GObject.registerClass(
    { GTypeName: 'ConfigView', Signals: { 'execute-conversion': { param_types: [GObject.TYPE_JSOBJECT] } } },
    class ConfigView extends Gtk.Box {
        _init(args = {}) {
            super._init(Object.assign({
                orientation: Gtk.Orientation.VERTICAL,
                spacing: 10,
                margin_top: 20,
                margin_bottom: 20,
                margin_start: 20,
                margin_end: 20,
            }, args));

        this._settings = new SettingsModel(); // Instantiate SettingsModel

        // Section for Input File Selection
        let inputFileSection = new Adw.PreferencesGroup({
            title: 'Input File',
            description: 'Select the chat export file (OpenAI JSON, Anthropic JSON).'
        });
        this.append(inputFileSection);

        let inputFileRow = new Adw.ActionRow({
            title: 'File Path',
        });
        inputFileSection.add(inputFileRow);

        this.inputFilePathEntry = new Gtk.Entry({
            hexpand: true,
            editable: false,
            placeholder_text: 'No file selected',
        });
        inputFileRow.add_suffix(this.inputFilePathEntry);

        let selectFileButton = new Gtk.Button({
            label: 'Select File',
            css_classes: ['suggested-action'],
        });
        inputFileRow.add_suffix(selectFileButton);

        // Connect signal for button click
        selectFileButton.connect('clicked', async () => {
            const path = await FileManager.open_file_chooser(this.get_root(), 'Select Chat Export File', [
                { name: 'JSON Files', patterns: ['*.json'] },
                { name: 'All Files', patterns: ['*'] }
            ]);
            if (path) {
                this.inputFilePathEntry.set_text(path);
                this._settings.input_file_path = path;
            }
        });

        // Load saved path on initialization
        const savedPath = this._settings.input_file_path;
        if (savedPath) {
            this.inputFilePathEntry.set_text(savedPath);
        }

        // Section for Output Directory Selection
        let outputDirSection = new Adw.PreferencesGroup({
            title: 'Output Directory',
            description: 'Select the directory to save converted files.'
        });
        this.append(outputDirSection);

        let outputDirRow = new Adw.ActionRow({
            title: 'Directory Path',
        });
        outputDirSection.add(outputDirRow);

        this.outputDirPathEntry = new Gtk.Entry({
            hexpand: true,
            editable: false,
            placeholder_text: 'No directory selected',
        });
        outputDirRow.add_suffix(this.outputDirPathEntry);

        let selectDirButton = new Gtk.Button({
            label: 'Select Directory',
            css_classes: ['suggested-action'],
        });
        outputDirRow.add_suffix(selectDirButton);

        // Connect signal for button click
        selectDirButton.connect('clicked', async () => {
            const path = await FileManager.open_folder_chooser(this.get_root(), 'Select Output Directory');
            if (path) {
                this.outputDirPathEntry.set_text(path);
                this._settings.output_directory_path = path;
            }
        });

        // Load saved path on initialization
        const savedOutputDirPath = this._settings.output_directory_path;
        if (savedOutputDirPath) {
            this.outputDirPathEntry.set_text(savedOutputDirPath);
        }

        // Section for Conversion Options
        let conversionOptionsSection = new Adw.PreferencesGroup({
            title: 'Conversion Options',
            description: 'Configure how chat exports are converted.'
        });
        this.append(conversionOptionsSection);

        // strip_metadata option
        let stripMetadataRow = new Adw.ActionRow({
            title: 'Strip Metadata',
        });
        let stripMetadataSwitch = new Gtk.Switch({
            valign: Gtk.Align.CENTER,
            active: this._settings.conversion_options.strip_metadata || false,
        });
        stripMetadataRow.add_suffix(stripMetadataSwitch);
        stripMetadataRow.set_activatable_widget(stripMetadataSwitch);
        conversionOptionsSection.add(stripMetadataRow);

        stripMetadataSwitch.connect('state-set', (sw, state) => {
            let options = this._settings.conversion_options;
            options.strip_metadata = state;
            this._settings.conversion_options = options;
            return false;
        });

        // include_attachments option
        let includeAttachmentsRow = new Adw.ActionRow({
            title: 'Include Attachments',
        });
        let includeAttachmentsSwitch = new Gtk.Switch({
            valign: Gtk.Align.CENTER,
            active: this._settings.conversion_options.include_attachments || false,
        });
        includeAttachmentsRow.add_suffix(includeAttachmentsSwitch);
        includeAttachmentsRow.set_activatable_widget(includeAttachmentsSwitch);
        conversionOptionsSection.add(includeAttachmentsRow);

        includeAttachmentsSwitch.connect('state-set', (sw, state) => {
            let options = this._settings.conversion_options;
            options.include_attachments = state;
            this._settings.conversion_options = options;
            return false;
        });

        // max_tokens_per_message option
        let maxTokensRow = new Adw.ActionRow({
            title: 'Max Tokens Per Message',
        });
        let maxTokensSpinButton = new Gtk.SpinButton({
            valign: Gtk.Align.CENTER,
            adjustment: new Gtk.Adjustment({
                lower: 1,
                upper: 4096,
                step_increment: 1,
                page_increment: 100,
            }),
            value: this._settings.conversion_options.max_tokens_per_message || 1024,
            numeric: true,
        });
        maxTokensRow.add_suffix(maxTokensSpinButton);
        maxTokensRow.set_activatable_widget(maxTokensSpinButton);
        conversionOptionsSection.add(maxTokensRow);

        maxTokensSpinButton.connect('value-changed', (spin) => {
            let options = this._settings.conversion_options;
            options.max_tokens_per_message = spin.get_value_as_int();
            this._settings.conversion_options = options;
        });

        // output_format option
        let outputFormatRow = new Adw.ActionRow({
            title: 'Output Format',
        });
        let outputFormatComboBox = Gtk.ComboBoxText.new();
        outputFormatComboBox.append('markdown', 'Markdown');
        outputFormatComboBox.append('text', 'Plain Text');
        outputFormatComboBox.append('html', 'HTML');
        outputFormatComboBox.set_active_id(this._settings.conversion_options.output_format || 'markdown');

        outputFormatRow.add_suffix(outputFormatComboBox);
        outputFormatRow.set_activatable_widget(outputFormatComboBox);
        conversionOptionsSection.add(outputFormatRow);

        outputFormatComboBox.connect('changed', (combo) => {
            let options = this._settings.conversion_options;
            options.output_format = combo.get_active_id();
            this._settings.conversion_options = options;
        });

        // Section for Execute Button
        let executeSection = new Adw.PreferencesGroup({
            title: 'Execute Conversion',
            description: 'Start the chat export conversion process.'
        });
        this.append(executeSection);

        let executeButtonRow = new Adw.ActionRow({
            title: 'Run Conversion',
        });
        executeSection.add(executeButtonRow);

        let executeButton = new Gtk.Button({
            label: 'Execute',
            css_classes: ['suggested-action', 'pill'],
            halign: Gtk.Align.CENTER,
            hexpand: true,
        });
        executeButtonRow.add_suffix(executeButton);

        executeButton.connect('clicked', () => {
            log('Execute button clicked');
            // Emit custom signal with current settings
            this.emit('execute-conversion', {
                input_file: this._settings.input_file_path,
                output_directory: this._settings.output_directory_path,
                options: this._settings.conversion_options,
            });
        });

        log('ConfigView initialized.');
    }
});

var _ConfigView = ConfigView;

