#!/usr/bin/gjs

const GLib = imports.gi.GLib;
imports.searchPath.unshift(GLib.get_current_dir() + '/src');

const Gio = imports.gi.Gio;
const Adw = imports.gi.Adw;
const MainWindow = imports.widgets.MainWindow;

// Global variable to hold the application instance
// This is necessary for NotificationManager to access the application object
var application = null;

class Application extends Adw.Application {
    constructor() {
        super({
            application_id: 'org.gnome.AI-Chat-Reader',
            flags: Gio.ApplicationFlags.FLAGS_NONE,
        });

        this.connect('activate', this._onActivate);
    }

    _onActivate() {
        // Create and show the main window
        let window = new MainWindow({
            application: this,
        });
        window.present();
    }
}

// Main application entry point
application = new Application(); // Assign to global variable
Adw.init();
application.run(ARGV);
