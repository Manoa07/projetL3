APP_STYLESHEET = """
QWidget {
    color: #17212b;
    font-family: 'Segoe UI';
    font-size: 12px;
}

QMainWindow {
    background-color: #f6f8fb;
}

QFrame#Sidebar,
QFrame#AlertsPanel,
QFrame#Card {
    background-color: #ffffff;
    border: 1px solid #e4e9ef;
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
<<<<<<< Updated upstream
=======

QComboBox, QDateEdit, QTimeEdit {
    background-color: #ffffff;
    color: #17212b;
    border: 1px solid #d8e0e8;
    border-radius: 10px;
    padding: 10px;
}

QComboBox QAbstractItemView,
QCalendarWidget,
QCalendarWidget QWidget#qt_calendar_navigationbar,
QCalendarWidget QAbstractItemView {
    background-color: #ffffff;
    color: #17212b;
    selection-background-color: #f7d8cf;
    selection-color: #17212b;
}

QDateEdit:focus, QTimeEdit:focus, QComboBox:focus {
    border: 1px solid #2e9d68;
}

QCalendarWidget QToolButton,
QCalendarWidget QSpinBox {
    background-color: #ffffff;
    color: #17212b;
}

QCalendarWidget QAbstractItemView:enabled {
    background-color: #ffffff;
    color: #17212b;
}
>>>>>>> Stashed changes
"""

NAV_BUTTON_STYLE = """
QPushButton {
    background: transparent;
    border: 1px solid transparent;
    color: #718096;
    font-size: 11px;
    font-weight: 600;
    padding: 12px 8px;
    border-radius: 14px;
    text-align: center;
}
<<<<<<< Updated upstream
QPushButton:hover {
    background: #20243a;
    color: #f4f7fb;
=======
QPushButton:hover:!checked {
    background: #edf8f1;
    color: #17212b;
>>>>>>> Stashed changes
}
QPushButton:pressed {
    background: #dff1e6;
}
QPushButton:checked {
    background: #e6f5ec;
    color: #247a50;
    border: 1px solid #b8dfc8;
}
<<<<<<< Updated upstream
=======
QPushButton:checked:hover {
    background: #d8efdf;
    color: #1e6843;
    border: 1px solid #9ed0b2;
}
>>>>>>> Stashed changes
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
