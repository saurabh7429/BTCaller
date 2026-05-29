import sys
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QListWidget, QStackedWidget, QLineEdit, QGridLayout, QFrame, QMenu
)
from PyQt6.QtCore import Qt, QTimer

class MainWindow(QWidget):
    def __init__(self, bluetooth_manager, call_manager):
        super().__init__()
        self.bt_manager = bluetooth_manager
        self.call_manager = call_manager
        self.current_call_path = None
        
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        self.setWindowTitle('BTCaller')
        self.resize(400, 600)
        
        # Main layout is a stacked widget to switch between screens
        self.stacked_widget = QStackedWidget()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked_widget)
        
        # Create screens
        self.dashboard_screen = self.create_dashboard_screen()
        self.incoming_call_screen = self.create_incoming_call_screen()
        self.ongoing_call_screen = self.create_ongoing_call_screen()
        
        self.stacked_widget.addWidget(self.dashboard_screen)
        self.stacked_widget.addWidget(self.incoming_call_screen)
        self.stacked_widget.addWidget(self.ongoing_call_screen)
        
        self.stacked_widget.setCurrentWidget(self.dashboard_screen)
        
    def connect_signals(self):
        # Bluetooth Signals
        # Note: In a real app we'd poll or wait for device_list_updated
        self.bt_manager.connection_status_changed.connect(self.on_bt_status_changed)
        
        # Call Signals
        self.call_manager.incoming_call.connect(self.on_incoming_call)
        self.call_manager.call_answered.connect(self.on_call_answered)
        self.call_manager.outgoing_call.connect(self.on_outgoing_call)
        self.call_manager.call_ended.connect(self.on_call_ended)
        
    def create_dashboard_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("BTCaller")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.status_label = QLabel("Disconnected")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Devices list
        self.device_list = QListWidget()
        layout.addWidget(self.device_list)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        self.scan_btn = QPushButton("Refresh Devices")
        self.scan_btn.clicked.connect(self.refresh_devices)
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_device)
        
        btn_layout.addWidget(self.scan_btn)
        btn_layout.addWidget(self.connect_btn)
        layout.addLayout(btn_layout)
        
        # Dialpad
        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(0)
        
        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("Enter number...")
        self.number_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        input_layout.addWidget(self.number_input)
        
        self.backspace_btn = QPushButton("⌫")
        self.backspace_btn.setObjectName("backspaceBtn")
        self.backspace_btn.clicked.connect(self.number_input.backspace)
        input_layout.addWidget(self.backspace_btn)
        
        layout.addWidget(input_container)
        
        dialpad_layout = QGridLayout()
        dialpad_layout.setSpacing(10)
        buttons = [
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
            ('*', 3, 0), ('0', 3, 1), ('#', 3, 2),
        ]
        
        for btn_text, row, col in buttons:
            btn = QPushButton(btn_text)
            btn.setProperty("class", "dialpadBtn")
            btn.clicked.connect(lambda checked, text=btn_text: self.number_input.setText(self.number_input.text() + text))
            dialpad_layout.addWidget(btn, row, col)
            
        layout.addLayout(dialpad_layout)
        
        self.dial_btn = QPushButton("Call")
        self.dial_btn.setObjectName("acceptBtn")
        self.dial_btn.clicked.connect(self.dial_number)
        layout.addWidget(self.dial_btn)
        
        return screen

    def create_incoming_call_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)
        
        title = QLabel("Incoming Call")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.caller_id_label = QLabel("Unknown")
        self.caller_id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.caller_id_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self.caller_id_label)
        
        btn_layout = QHBoxLayout()
        self.accept_btn = QPushButton("Accept")
        self.accept_btn.setObjectName("acceptBtn")
        self.accept_btn.setMinimumHeight(50)
        self.accept_btn.clicked.connect(self.accept_call)
        
        self.reject_btn = QPushButton("Reject")
        self.reject_btn.setObjectName("rejectBtn")
        self.reject_btn.setMinimumHeight(50)
        self.reject_btn.clicked.connect(self.reject_call)
        
        btn_layout.addWidget(self.reject_btn)
        btn_layout.addWidget(self.accept_btn)
        
        layout.addLayout(btn_layout)
        return screen

    def create_ongoing_call_screen(self):
        screen = QWidget()
        layout = QVBoxLayout(screen)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)
        
        self.ongoing_caller_label = QLabel("Unknown")
        self.ongoing_caller_label.setObjectName("titleLabel")
        self.ongoing_caller_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.ongoing_caller_label)
        
        self.timer_label = QLabel("00:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 18px; color: #AAAAAA;")
        layout.addWidget(self.timer_label)
        
        controls_layout = QHBoxLayout()
        self.mute_btn = QPushButton("Mute")
        self.mute_btn.setCheckable(True)
        self.speaker_btn = QPushButton("Speaker / Audio Output")
        self.speaker_btn.clicked.connect(self.show_audio_menu)
        
        controls_layout.addWidget(self.mute_btn)
        controls_layout.addWidget(self.speaker_btn)
        layout.addLayout(controls_layout)
        
        self.end_call_btn = QPushButton("End Call")
        self.end_call_btn.setObjectName("endCallBtn")
        self.end_call_btn.setMinimumHeight(50)
        self.end_call_btn.clicked.connect(self.end_call)
        layout.addWidget(self.end_call_btn)
        
        return screen

    # --- Actions ---
    
    def refresh_devices(self):
        self.device_list.clear()
        devices = self.bt_manager.get_paired_devices()
        for dev in devices:
            status = "Connected" if dev['connected'] else "Disconnected"
            item_text = f"{dev['name']} ({dev['mac']}) - {status}"
            self.device_list.addItem(item_text)
            # Store path in user data
            self.device_list.item(self.device_list.count() - 1).setData(Qt.ItemDataRole.UserRole, dev['path'])

    def connect_device(self):
        selected = self.device_list.currentItem()
        if selected:
            path = selected.data(Qt.ItemDataRole.UserRole)
            self.status_label.setText("Connecting...")
            success = self.bt_manager.connect_device(path)
            if success:
                self.status_label.setText("Connected")
                # Once connected, we should try to find the modem
                QTimer.singleShot(2000, self.call_manager.find_modem)
            else:
                self.status_label.setText("Connection failed")

    def dial_number(self):
        number = self.number_input.text().strip()
        if number:
            self.status_label.setText(f"Dialing {number}...")
            self.call_manager.dial(number)

    def on_bt_status_changed(self, mac, is_connected):
        status = "Connected" if is_connected else "Disconnected"
        self.status_label.setText(f"Status: {status}")
        self.refresh_devices()
        if is_connected:
            QTimer.singleShot(2000, self.call_manager.find_modem)

    def on_incoming_call(self, path, caller_id):
        self.current_call_path = path
        self.caller_id_label.setText(caller_id)
        self.stacked_widget.setCurrentWidget(self.incoming_call_screen)

    def accept_call(self):
        if self.current_call_path:
            self.call_manager.answer_call(self.current_call_path)

    def reject_call(self):
        if self.current_call_path:
            self.call_manager.hangup_call(self.current_call_path)
            self.stacked_widget.setCurrentWidget(self.dashboard_screen)

    def on_outgoing_call(self, path, number):
        self.current_call_path = path
        self.ongoing_caller_label.setText(f"Calling: {number}")
        self.stacked_widget.setCurrentWidget(self.ongoing_call_screen)

    def on_call_answered(self, path):
        self.current_call_path = path
        self.stacked_widget.setCurrentWidget(self.ongoing_call_screen)
        # In a real app we'd start a timer

    def on_call_ended(self, path):
        if self.current_call_path == path:
            self.current_call_path = None
            self.stacked_widget.setCurrentWidget(self.dashboard_screen)
            self.status_label.setText("Call ended")

    def end_call(self):
        if self.current_call_path:
            self.call_manager.hangup_call(self.current_call_path)
        else:
            self.call_manager.hangup_all()

    def show_audio_menu(self):
        sinks = []
        try:
            output = subprocess.check_output(['pactl', 'list', 'short', 'sinks'], text=True)
            for line in output.strip().split('\n'):
                if not line: continue
                parts = line.split('\t')
                if len(parts) >= 2:
                    sinks.append((parts[0], parts[1]))
        except Exception as e:
            print(f"Error getting sinks: {e}")
            
        if not sinks:
            return
            
        menu = QMenu(self)
        for sink_id, sink_name in sinks:
            display_name = sink_name.split('.')[-1] if '.' in sink_name else sink_name
            action = menu.addAction(display_name)
            action.triggered.connect(lambda checked, name=sink_name: self.set_audio_sink(name))
            
        menu.exec(self.speaker_btn.mapToGlobal(self.speaker_btn.rect().bottomLeft()))

    def set_audio_sink(self, sink_name):
        try:
            subprocess.run(['pactl', 'set-default-sink', sink_name])
            print(f"Set default sink to {sink_name}")
        except Exception as e:
            print(f"Error setting sink: {e}")
