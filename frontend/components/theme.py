APP_STYLESHEET = """
QWidget {
    color: #f4f7fb;
    font-family: 'Segoe UI';
    font-size: 12px;
}

QMainWindow {
    background-color: #0f111a;
}

QFrame#Sidebar,
QFrame#AlertsPanel,
QFrame#Card {
    background-color: #151826;
    border: 1px solid #23283d;
    border-radius: 16px;
}

QPushButton {
    border: none;
}

QLabel {
    background: transparent;
}

QLineEdit, QComboBox, QTableWidget, QProgressBar {
    font-size: 12px;
}
"""

NAV_BUTTON_STYLE = """
QPushButton {
    background: transparent;
    border: 1px solid transparent;
    color: #7a7c8c;
    font-size: 11px;
    font-weight: 600;
    padding: 12px 8px;
    border-radius: 14px;
    text-align: center;
}
QPushButton:hover {
    background: #20243a;
    color: #f4f7fb;
}
QPushButton:pressed {
    background: #1d2234;
}
QPushButton:checked {
    background: #242b44;
    color: #4facfe;
    border: 1px solid #335a7f;
}
"""

ACTION_BUTTON_STYLE = """
QPushButton {
    border-radius: 12px;
    font-weight: 700;
    padding: 12px 16px;
}
QPushButton:hover {
    background: rgba(255, 255, 255, 0.04);
}
"""
