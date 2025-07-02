const Gio = imports.gi.Gio;

class SettingsModel {
    constructor() {
        this._settings = new Gio.Settings({
            schema_id: 'org.gnome.AI-Chat-Reader',
            // You might need to set a path if your schema is not in the default location
            // path: '/org/gnome/AI-Chat-Reader/',
        });
    }

    get input_file_path() {
        return this._settings.get_string('input-file-path');
    }

    set input_file_path(path) {
        this._settings.set_string('input-file-path', path);
    }

    get output_directory_path() {
        return this._settings.get_string('output-directory-path');
    }

    set output_directory_path(path) {
        this._settings.set_string('output-directory-path', path);
    }

    get conversion_options() {
        // Assuming conversion_options is a string for now, e.g., JSON representation of an object
        return JSON.parse(this._settings.get_string('conversion-options') || '{}');
    }

    set conversion_options(options) {
        this._settings.set_string('conversion-options', JSON.stringify(options));
    }
}

// Export the class for use in other files
var _SettingsModel = SettingsModel;
