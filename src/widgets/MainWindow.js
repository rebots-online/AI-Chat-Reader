const Gtk = imports.gi.Gtk;
const Adw = imports.gi.Adw;
const GLib = imports.gi.GLib;
const GObject = imports.gi.GObject;
const HeaderBar = imports.widgets.HeaderBar._HeaderBar;
const ConfigView = imports.widgets.ConfigView._ConfigView;
const LogView = imports.widgets.LogView._LogView;
const ProcessManager = imports.utils.ProcessManager._ProcessManager;
const NotificationManager = imports.utils.NotificationManager._NotificationManager;

const MainWindow = GObject.registerClass(
    { GTypeName: 'MainWindow' },
    class MainWindow extends Adw.ApplicationWindow {
        _init(args = {}) {
            super._init(args);

            this.set_title('AI Chat Reader');
            this.set_default_size(800, 600);

            // Use Adw.ToolbarView for proper libadwaita layout
            const toolbarView = new Adw.ToolbarView();
            this.set_content(toolbarView);

            // Add header bar at top
            toolbarView.add_top_bar(new HeaderBar());

            // Main content box
            let content = new Gtk.Box({
                orientation: Gtk.Orientation.VERTICAL,
                hexpand: true,
                vexpand: true,
            });
            toolbarView.set_content(content);

            // Instantiate ConfigView and LogView
            this.configView = new ConfigView();
            this.logView = new LogView();

        // Add ConfigView and LogView to the content area
        content.append(this.configView);
        content.append(this.logView);

        // Connect to the 'execute-conversion' signal from ConfigView
        this.configView.connect('execute-conversion', (emitter, params) => {
            log(`Conversion requested: ${JSON.stringify(params)}`);
            this.logView.append_log(`Conversion requested for: ${params.input_file}`);
            this.logView.append_log(`Output directory: ${params.output_directory}`);
            this.logView.append_log(`Options: ${JSON.stringify(params.options)}`);

            // Execute the script using ProcessManager
            const scriptPath = GLib.build_filenamev([
                GLib.get_current_dir(),
                'scripts',
                'convert_to_html.py'
            ]);
            const scriptArgs = [
                '--input', params.input_file,
                '--output', params.output_directory,
                '--options', JSON.stringify(params.options)
            ];

            this.logView.append_log(`Executing: ${scriptPath} ${scriptArgs.join(' ')}`);

            ProcessManager.execute_script(
                scriptPath,
                scriptArgs,
                (stdout) => { this.logView.append_log(`STDOUT: ${stdout}`); },
                (stderr) => { this.logView.append_log(`STDERR: ${stderr}`); },
                (exitCode, success) => {
                    if (success) {
                        this.logView.append_log(`Script finished successfully with exit code ${exitCode}.`);
                        NotificationManager.send_notification(
                            'Conversion Successful',
                            `Script exited with code ${exitCode}.`, 
                            'dialog-information'
                        );
                    } else {
                        this.logView.append_log(`Script failed with exit code ${exitCode}.`);
                        NotificationManager.send_notification(
                            'Conversion Failed',
                            `Script exited with code ${exitCode}. Check logs for details.`, 
                            'dialog-error'
                        );
                    }
                }
            );
        });

        this.logView.set_size_request(-1, 200); // Set a default height for the log view

        log('MainWindow initialized.');
    }
});

var _MainWindow = MainWindow;

