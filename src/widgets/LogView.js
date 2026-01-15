const Gtk = imports.gi.Gtk;
const GObject = imports.gi.GObject;

const LogView = GObject.registerClass(
    { GTypeName: 'LogView' },
    class LogView extends Gtk.ScrolledWindow {
        _init(args = {}) {
            super._init(Object.assign({
                hexpand: true,
                vexpand: true,
            }, args));

            // Set scrollbar policies after construction
            this.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS);

            this._textView = new Gtk.TextView({
                editable: false,
                cursor_visible: false,
                monospace: true,
            });
            this.set_child(this._textView);

            this._textBuffer = this._textView.get_buffer();
        }

        append_log(message) {
            const endIter = this._textBuffer.get_end_iter();
            this._textBuffer.insert(endIter, message + '\n', -1);

            // Auto-scroll to the bottom
            const mark = this._textBuffer.create_mark(null, this._textBuffer.get_end_iter(), false);
            this._textView.scroll_to_mark(mark, 0.0, false, 0.0, 0.0);
            this._textBuffer.delete_mark(mark);
        }

        clear_log() {
            this._textBuffer.set_text('', 0);
        }
    }
);

var _LogView = LogView;
