const Gtk = imports.gi.Gtk;
const Adw = imports.gi.Adw;

class HeaderBar extends Gtk.HeaderBar {
    constructor(args) {
        super(args);

        this.set_title_widget(new Adw.WindowTitle({
            title: 'AI Chat Reader Converter',
        }));

        // Menu button (placeholder)
        let menuButton = Gtk.MenuButton.new();
        menuButton.set_icon_name('open-menu-symbolic');
        this.pack_start(menuButton);



        log('HeaderBar initialized.');
    }
}

// Export the class for use in other files
var _HeaderBar = HeaderBar;
