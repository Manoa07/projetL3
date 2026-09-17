APP_STYLESHEET = """
QWidget {
    color: #172033;
    font-family: 'Segoe UI';
    font-size: 12px;
}

QMainWindow {
    background-color: #f5f7fb;
}

QFrame#Sidebar,
QFrame#AlertsPanel,
QFrame#Card {
    background-color: #ffffff;
    border: 1px solid #e5eaf2;
    border-radius: 14px;
}

QPushButton {
    border: none;
}

QLabel {
    background: transparent;
}

QLineEdit, QComboBox, QDateEdit, QTimeEdit, QTableWidget, QProgressBar {
    font-size: 12px;
}

QComboBox, QDateEdit, QTimeEdit {
    background-color: #ffffff;
    color: #172033;
    border: 1px solid #d8e0ec;
    border-radius: 10px;
    padding: 10px;
}

QComboBox QAbstractItemView,
QCalendarWidget,
QCalendarWidget QWidget#qt_calendar_navigationbar,
QCalendarWidget QAbstractItemView {
    background-color: #151826;
    color: #f4f7fb;
    selection-background-color: #2a304b;
    selection-color: #ffffff;
}

QDateEdit:focus, QTimeEdit:focus, QComboBox:focus {
    border: 1px solid #4facfe;
}

QCalendarWidget QToolButton,
QCalendarWidget QSpinBox {
    background-color: #ffffff;
    color: #172033;
}

QCalendarWidget QAbstractItemView:enabled {
    background-color: #ffffff;
    color: #172033;
}
"""

NAV_BUTTON_STYLE = """
QPushButton {
    background: transparent;
    border: 1px solid transparent;
    color: #718096;
    font-size: 11px;
    font-weight: 600;
    padding: 10px 8px;
    border-radius: 10px;
    text-align: center;
}
QPushButton:hover:!checked {
    background: #edf5ff;
    color: #1769d2;
}
QPushButton:pressed {
    background: #dcecff;
}
QPushButton:checked {
    background: #e7f1ff;
    color: #1769d2;
    border: 1px solid #bed9ff;
}
QPushButton:checked:hover {
    background: #dcecff;
    color: #1769d2;
    border: 1px solid #a8ccff;
}
"""

ACTION_BUTTON_STYLE = """
QPushButton {
    background: #1769d2;
    color: #ffffff;
    border-radius: 10px;
    font-weight: 700;
    padding: 12px 16px;
}
QPushButton:hover {
    background: #0f58b7;
}
QPushButton:pressed {
    background: #0b4694;
}
"""
