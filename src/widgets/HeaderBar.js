const Gtk = imports.gi.Gtk;
const Adw = imports.gi.Adw;
const GObject = imports.gi.GObject;
const Gio = imports.gi.Gio;

const HeaderBar = GObject.registerClass(
    { GTypeName: 'HeaderBar' },
    class HeaderBar extends Gtk.HeaderBar {
        _init(args = {}) {
            super._init(args);

            this.set_title_widget(new Adw.WindowTitle({
                title: 'AI Chat Reader Converter',
            }));

            // Menu button with popover menu
            let menuButton = new Gtk.MenuButton({
                icon_name: 'open-menu-symbolic',
                tooltip_text: 'Main Menu',
            });

            // Create menu model
            const menu = new Gio.Menu();
            menu.append('About', 'app.about');
            menu.append('Preferences', 'app.preferences');
            menu.append('Quit', 'app.quit');

            menuButton.set_menu_model(menu);
            this.pack_end(menuButton);

            log('HeaderBar initialized.');
        }
    }
);

// Export the class for use in other files
var _HeaderBar = HeaderBar;
