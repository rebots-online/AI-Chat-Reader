const Gtk = imports.gi.Gtk;

class LogView extends Gtk.ScrolledWindow {
    constructor(args) {
        super({
            hscroll_policy: Gtk.ScrollablePolicy.NATURAL,
            vscroll_policy: Gtk.ScrollablePolicy.ALWAYS,
            hexpand: true,
            vexpand: true,
        });

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
        this._textBuffer.insert(endIter, message + '\n');

        // Auto-scroll to the bottom
        const mark = this._textBuffer.create_mark(null, this._textBuffer.get_end_iter(), false);
        this._textView.scroll_to_mark(mark, 0.0, false, 0.0, 0.0);
        this._textBuffer.delete_mark(mark);
    }
}

var _LogView = LogView;
