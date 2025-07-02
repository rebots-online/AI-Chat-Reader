const Gtk = imports.gi.Gtk;
const Adw = imports.gi.Adw;
const GObject = imports.gi.GObject;
const ConfigView = imports.widgets.ConfigView;
const LogView = imports.widgets.LogView;
const ProcessManager = imports.utils.ProcessManager;
const NotificationManager = imports.utils.NotificationManager;

const MainWindow = GObject.registerClass(
    { GTypeName: 'MainWindow' },
    class MainWindow extends Adw.ApplicationWindow {
        _init(args) {
            super._init(args);



        this.set_title('AI Chat Reader');
        this.set_default_size(800, 600);

        // Main content area
        let content = new Gtk.Box({
            orientation: Gtk.Orientation.VERTICAL,
            hexpand: true,
            vexpand: true,
        });
        this.set_content(content);

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
            const scriptPath = '/path/to/your/conversion/script.py'; // TODO: Replace with actual script path
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
})



// Export the class for use in other files
// This is implicitly handled by GObject.registerClass when assigning to a const

