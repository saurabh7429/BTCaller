import dbus
import dbus.mainloop.glib
from gi.repository import GLib
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

class BluetoothManager(QObject):
    # Signals to update UI
    device_list_updated = pyqtSignal(list)
    connection_status_changed = pyqtSignal(str, bool) # MAC, is_connected

    def __init__(self):
        super().__init__()
        # Set up DBus loop for GI so we can receive signals (requires DBusGMainLoop set as default)
        # We will initialize this from main.py before QApplication
        self.bus = dbus.SystemBus()
        self.bluez_service = 'org.bluez'
        
        # Get ObjectManager to find devices
        self.manager = dbus.Interface(self.bus.get_object(self.bluez_service, '/'), 'org.freedesktop.DBus.ObjectManager')
        
    def get_paired_devices(self):
        """Returns a list of paired bluetooth devices: [{'name': Name, 'mac': Address, 'path': dbus_path, 'connected': bool}]"""
        objects = self.manager.GetManagedObjects()
        devices = []
        for path, interfaces in objects.items():
            if 'org.bluez.Device1' in interfaces:
                props = interfaces['org.bluez.Device1']
                if props.get('Paired') == 1:
                    devices.append({
                        'name': str(props.get('Name', 'Unknown Device')),
                        'mac': str(props.get('Address', '')),
                        'path': str(path),
                        'connected': bool(props.get('Connected', 0))
                    })
        return devices
        
    def connect_device(self, device_path):
        """Attempts to connect to the given device."""
        try:
            device = dbus.Interface(self.bus.get_object(self.bluez_service, device_path), 'org.bluez.Device1')
            device.Connect()
            return True
        except Exception as e:
            print(f"Error connecting to device {device_path}: {e}")
            return False

    def disconnect_device(self, device_path):
        """Attempts to disconnect from the given device."""
        try:
            device = dbus.Interface(self.bus.get_object(self.bluez_service, device_path), 'org.bluez.Device1')
            device.Disconnect()
            return True
        except Exception as e:
            print(f"Error disconnecting device {device_path}: {e}")
            return False
            
    def listen_for_changes(self):
        """Set up listeners for properties changed on devices to track connection status."""
        self.bus.add_signal_receiver(
            self._properties_changed,
            dbus_interface="org.freedesktop.DBus.Properties",
            signal_name="PropertiesChanged",
            arg0="org.bluez.Device1",
            path_keyword="path"
        )
        
    def _properties_changed(self, interface, changed, invalidated, path=None):
        if 'Connected' in changed:
            is_connected = bool(changed['Connected'])
            # Fetch MAC address from path
            try:
                obj = self.bus.get_object(self.bluez_service, path)
                props = dbus.Interface(obj, "org.freedesktop.DBus.Properties")
                mac = str(props.Get("org.bluez.Device1", "Address"))
                self.connection_status_changed.emit(mac, is_connected)
            except Exception as e:
                pass
