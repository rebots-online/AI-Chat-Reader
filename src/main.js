#!/usr/bin/gjs
// Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.

imports.gi.versions.Gtk = '4.0';
imports.gi.versions.Adw = '1';

const System = imports.system;
const GLib = imports.gi.GLib;
const Gtk = imports.gi.Gtk;
const Gio = imports.gi.Gio;
const Adw = imports.gi.Adw;
const GObject = imports.gi.GObject;

// Set up import paths - check for installed location or development location
const pkgdatadir = GLib.getenv('PKGDATADIR') || GLib.get_current_dir();
imports.searchPath.unshift(pkgdatadir + '/src');
imports.searchPath.unshift(GLib.get_current_dir() + '/src');

const MainWindow = imports.widgets.MainWindow;

// Read version from VERSION file
function getVersion() {
    const versionPaths = [
        GLib.build_filenamev([pkgdatadir, '..', 'VERSION']),
        GLib.build_filenamev([GLib.get_current_dir(), 'VERSION']),
        '/usr/share/ai-chat-reader/VERSION',
    ];
    for (const path of versionPaths) {
        try {
            const [ok, contents] = GLib.file_get_contents(path);
            if (ok) return new TextDecoder().decode(contents).trim();
        } catch (e) { /* continue */ }
    }
    return '1.0.0';
}

// Generate build number using same algorithm as build.py
// epoch % 100 * 1000 + (epoch / 60) % 60
function generateBuildNumber() {
    const epoch = Math.floor(Date.now() / 1000);
    const epochMod = epoch % 100;
    const minutes = Math.floor(epoch / 60) % 60;
    return epochMod * 1000 + minutes;
}

const VERSION = getVersion();
const BUILD_NUM = generateBuildNumber();

// Global variable to hold the application instance
// This is necessary for NotificationManager to access the application object
var application = null;

const Application = GObject.registerClass(
    { GTypeName: 'AI_Chat_Reader_App' },
    class Application extends Adw.Application {
        _init() {
            super._init({
                application_id: 'org.gnome.AI-Chat-Reader',
                flags: Gio.ApplicationFlags.FLAGS_NONE,
            });

            // Print version banner
            print('═'.repeat(70));
            print(`AI Chat Reader v${VERSION} Build ${BUILD_NUM}`);
            print('Copyright (C) 2025 Robin L. M. Cheung, MBA. All rights reserved.');
            print('═'.repeat(70));
            print('');
        }

        vfunc_startup() {
            super.vfunc_startup();

            // Set up application actions
            this._setupActions();

            log('Application startup complete.');
        }

        vfunc_activate() {
            // Create and show the main window
            let window = this.active_window;
            if (!window) {
                window = new MainWindow._MainWindow({
                    application: this,
                });
            }
            window.present();

            log('Application activated.');
        }

        _setupActions() {
            // About action
            const aboutAction = new Gio.SimpleAction({ name: 'about' });
            aboutAction.connect('activate', () => this._showAboutDialog());
            this.add_action(aboutAction);

            // Preferences action
            const preferencesAction = new Gio.SimpleAction({ name: 'preferences' });
            preferencesAction.connect('activate', () => {
                log('Preferences action triggered (not yet implemented)');
            });
            this.add_action(preferencesAction);

            // Quit action
            const quitAction = new Gio.SimpleAction({ name: 'quit' });
            quitAction.connect('activate', () => this.quit());
            this.add_action(quitAction);
            this.set_accels_for_action('app.quit', ['<Control>q']);
        }

        _showAboutDialog() {
            const aboutDialog = new Adw.AboutWindow({
                transient_for: this.active_window,
                application_name: 'AI Chat Reader',
                application_icon: 'org.gnome.AI-Chat-Reader',
                developer_name: 'Robin L. M. Cheung, MBA',
                version: `v${VERSION} Build ${BUILD_NUM}`,
                copyright: '© 2025 Robin L. M. Cheung, MBA. All rights reserved.',
                license_type: Gtk.License.CUSTOM,
                license: 'Proprietary - All rights reserved.',
                website: 'https://github.com/rebots-online/AI-Chat-Reader',
                developers: ['Robin L. M. Cheung, MBA'],
                comments: 'Convert OpenAI and Anthropic chat exports to HTML format with iOS-style chat bubbles, light/dark mode support, and navigation features.',
            });
            aboutDialog.present();
        }
    }
);

// Main application entry point
print('Please wait... Initializing...');
print('');

application = new Application();
application.run([System.programInvocationName].concat(ARGV));
