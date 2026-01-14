const Gio = imports.gi.Gio;

class NotificationManager {
    static send_notification(title, body, icon_name = 'dialog-information') {
        const notification = new Gio.Notification();
        notification.set_title(title);
        notification.set_body(body);
        notification.set_icon(new Gio.ThemedIcon({ name: icon_name }));

        // Assuming 'application' is available in the global scope or passed
        // For GJS applications, this typically refers to the Adw.Application instance
        if (typeof application !== 'undefined' && application instanceof Gio.Application) {
            application.send_notification(null, notification);
        } else {
            log('Warning: Gio.Application instance not found for sending notification.');
        }
    }
}

var _NotificationManager = NotificationManager;
