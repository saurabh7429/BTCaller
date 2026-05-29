import sys
import dbus.mainloop.glib
from PyQt6.QtWidgets import QApplication
from ui.style import DARK_THEME
from ui.main_window import MainWindow
from core.bluetooth_manager import BluetoothManager
from core.call_manager import CallManager

def main():
    # Set up DBus Main Loop (Required to receive DBus signals in a GLib/Qt event loop)
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)
    
    bt_manager = BluetoothManager()
    call_manager = CallManager()
    
    window = MainWindow(bt_manager, call_manager)
    window.show()
    
    # Initialize devices
    window.refresh_devices()
    
    # Listen for bluetooth changes
    bt_manager.listen_for_changes()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
