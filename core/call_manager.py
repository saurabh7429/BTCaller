import dbus
from PyQt6.QtCore import QObject, pyqtSignal

class CallManager(QObject):
    # Signals for UI
    incoming_call = pyqtSignal(str, str) # path, caller_id
    call_answered = pyqtSignal(str) # path
    outgoing_call = pyqtSignal(str, str) # path, number
    call_ended = pyqtSignal(str) # path
    
    def __init__(self):
        super().__init__()
        self.bus = dbus.SystemBus()
        self.ofono_service = 'org.ofono'
        self.modem_path = None
        self.vcm_interface = None
        self.active_calls = {}
        
    def find_modem(self):
        try:
            manager = dbus.Interface(self.bus.get_object(self.ofono_service, '/'), 'org.ofono.Manager')
            modems = manager.GetModems()
            if modems:
                # Use the first available modem (typically the connected phone)
                self.modem_path = modems[0][0]
                modem_props = modems[0][1]
                
                # Attempt to bring the modem online
                modem = dbus.Interface(
                    self.bus.get_object(self.ofono_service, self.modem_path),
                    'org.ofono.Modem'
                )
                try:
                    if not modem_props.get("Powered"):
                        modem.SetProperty("Powered", dbus.Boolean(1))
                    if not modem_props.get("Online"):
                        modem.SetProperty("Online", dbus.Boolean(1))
                except Exception as e:
                    print(f"Warning: Could not power on modem (it may need to be connected first): {e}")

                self.vcm_interface = dbus.Interface(
                    self.bus.get_object(self.ofono_service, self.modem_path), 
                    'org.ofono.VoiceCallManager'
                )
                
                # Listen to CallAdded and CallRemoved
                self.vcm_interface.connect_to_signal("CallAdded", self._on_call_added)
                self.vcm_interface.connect_to_signal("CallRemoved", self._on_call_removed)
                return True
        except Exception as e:
            print(f"Error finding modem: {e}")
        return False

    def dial(self, number):
        if not self.vcm_interface:
            if not self.find_modem():
                return False
        try:
            # hide_id = "default"
            path = self.vcm_interface.Dial(number, "default")
            self.outgoing_call.emit(path, number)
            return True
        except Exception as e:
            print(f"Error dialing: {e}")
            return False

    def answer_call(self, path):
        try:
            call = dbus.Interface(self.bus.get_object(self.ofono_service, path), 'org.ofono.VoiceCall')
            call.Answer()
            self.call_answered.emit(path)
            return True
        except Exception as e:
            print(f"Error answering call: {e}")
            return False

    def hangup_call(self, path):
        try:
            call = dbus.Interface(self.bus.get_object(self.ofono_service, path), 'org.ofono.VoiceCall')
            call.Hangup()
            return True
        except Exception as e:
            print(f"Error hanging up call: {e}")
            return False

    def hangup_all(self):
        if self.vcm_interface:
            try:
                self.vcm_interface.HangupAll()
            except Exception as e:
                print(f"Error hanging up all calls: {e}")

    def _on_call_added(self, path, properties):
        state = str(properties.get("State", ""))
        caller = str(properties.get("LineIdentification", "Unknown"))
        if not caller:
            caller = "Unknown"
        self.active_calls[path] = {"state": state, "caller": caller}
        
        if state == "incoming":
            self.incoming_call.emit(path, caller)
        elif state == "active":
            self.call_answered.emit(path)
        elif state in ["dialing", "alerting"]:
            self.outgoing_call.emit(path, caller)

    def _on_call_removed(self, path):
        if path in self.active_calls:
            del self.active_calls[path]
        self.call_ended.emit(path)
