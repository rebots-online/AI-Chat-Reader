const Gtk = imports.gi.Gtk;
const Gio = imports.gi.Gio;

class FileManager {
    static async open_file_chooser(parentWindow, title, filters = []) {
        return new Promise((resolve) => {
            const dialog = new Gtk.FileChooserNative({
                title: title,
                transient_for: parentWindow,
                action: Gtk.FileChooserAction.OPEN,
                accept_label: 'Open',
            });

            filters.forEach(filter => {
                const gtkFilter = new Gtk.FileFilter();
                gtkFilter.set_name(filter.name);
                filter.patterns.forEach(pattern => gtkFilter.add_pattern(pattern));
                dialog.add_filter(gtkFilter);
            });

            dialog.connect('response', (dialog, response) => {
                if (response === Gtk.ResponseType.ACCEPT) {
                    const file = dialog.get_file();
                    if (file) {
                        resolve(file.get_path());
                    } else {
                        resolve(null);
                    }
                } else {
                    resolve(null);
                }
                dialog.destroy();
            });

            dialog.show();
        });
    }

    static async open_folder_chooser(parentWindow, title) {
        return new Promise((resolve) => {
            const dialog = new Gtk.FileChooserNative({
                title: title,
                transient_for: parentWindow,
                action: Gtk.FileChooserAction.SELECT_FOLDER,
                accept_label: 'Select',
            });

            dialog.connect('response', (dialog, response) => {
                if (response === Gtk.ResponseType.ACCEPT) {
                    const file = dialog.get_file();
                    if (file) {
                        resolve(file.get_path());
                    } else {
                        resolve(null);
                    }
                } else {
                    resolve(null);
                }
                dialog.destroy();
            });

            dialog.show();
        });
    }
}

var _FileManager = FileManager;
