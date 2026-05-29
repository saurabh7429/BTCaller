DARK_THEME = """
QWidget {
    background-color: #121212;
    color: #E0E0E0;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: 14px;
}

QPushButton {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 8px;
    padding: 10px;
    color: #FFFFFF;
}

QPushButton:hover {
    background-color: #2D2D2D;
    border: 1px solid #555555;
}

QPushButton:pressed {
    background-color: #404040;
}

/* Call Control Buttons */
QPushButton#acceptBtn {
    background-color: #2E7D32;
    border: none;
    font-weight: bold;
}

QPushButton#acceptBtn:hover {
    background-color: #388E3C;
}

QPushButton#rejectBtn, QPushButton#endCallBtn {
    background-color: #C62828;
    border: none;
    font-weight: bold;
}

QPushButton#rejectBtn:hover, QPushButton#endCallBtn:hover {
    background-color: #D32F2F;
}

/* Dialpad Buttons */
QPushButton.dialpadBtn {
    background-color: #2A2A2A;
    font-size: 24px;
    border-radius: 30px;
    min-width: 60px;
    min-height: 60px;
}

QPushButton.dialpadBtn:hover {
    background-color: #3A3A3A;
}

/* Labels */
QLabel {
    color: #E0E0E0;
}

QLabel#titleLabel {
    font-size: 24px;
    font-weight: bold;
    color: #FFFFFF;
}

QLabel#statusLabel {
    color: #AAAAAA;
    font-size: 12px;
}

/* Lists */
QListWidget {
    background-color: #1A1A1A;
    border: 1px solid #333333;
    border-radius: 8px;
}

QListWidget::item {
    padding: 10px;
    border-bottom: 1px solid #2A2A2A;
}

QListWidget::item:selected {
    background-color: #2C3E50;
    color: white;
}

/* Inputs and Containers */
QFrame#inputContainer {
    background-color: #1A1A1A;
    border: 1px solid #333333;
    border-radius: 8px;
}

QLineEdit {
    background-color: transparent;
    border: none;
    padding: 10px;
    font-size: 24px;
    color: #FFFFFF;
}

QPushButton#backspaceBtn {
    background-color: transparent;
    border: none;
    color: #888888;
    font-size: 24px;
    padding: 5px 15px;
}

QPushButton#backspaceBtn:hover {
    color: #FFFFFF;
    background-color: transparent;
    border: none;
}

QPushButton#backspaceBtn:pressed {
    color: #555555;
}
"""
