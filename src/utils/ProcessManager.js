const Gio = imports.gi.Gio;

class ProcessManager {
    static async execute_script(script_path, args = [], on_stdout = null, on_stderr = null, on_exit = null) {
        return new Promise((resolve, reject) => {
            try {
                const argv = [script_path, ...args];
                const subprocess = new Gio.Subprocess({
                    argv: argv,
                    flags: Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE,
                });

                subprocess.init(null);

                // Handle stdout
                subprocess.get_stdout_pipe().read_bytes_async(1024, null, (source, res) => {
                    let bytes = source.read_bytes_finish(res);
                    let decoder = new TextDecoder('utf-8');
                    let text = decoder.decode(bytes.get_data());
                    if (on_stdout) {
                        on_stdout(text);
                    }
                    // Continue reading
                    source.read_bytes_async(1024, null, arguments.callee);
                });

                // Handle stderr
                subprocess.get_stderr_pipe().read_bytes_async(1024, null, (source, res) => {
                    let bytes = source.read_bytes_finish(res);
                    let decoder = new TextDecoder('utf-8');
                    let text = decoder.decode(bytes.get_data());
                    if (on_stderr) {
                        on_stderr(text);
                    }
                    // Continue reading
                    source.read_bytes_async(1024, null, arguments.callee);
                });

                // Handle process exit
                subprocess.wait_async(null, (source, res) => {
                    try {
                        const success = source.wait_finish(res);
                        const exitCode = source.get_exit_status();
                        if (on_exit) {
                            on_exit(exitCode, success);
                        }
                        resolve({ exitCode: exitCode, success: success });
                    } catch (e) {
                        reject(e);
                    }
                });

            } catch (e) {
                reject(e);
            }
        });
    }
}

var _ProcessManager = ProcessManager;
