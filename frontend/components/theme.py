from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QAbstractItemView, QHeaderView, QSizePolicy


def configure_table(table, height=320):
    table.setMinimumHeight(220)
    table.setMaximumHeight(height)
    table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setAlternatingRowColors(True)
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    header.setMinimumSectionSize(90)
    if table.columnCount() >= 3:
        header.setMinimumSectionSize(90)
        header.setSectionResizeMode(table.columnCount() - 1, QHeaderView.ResizeMode.Stretch)
        table.setColumnWidth(table.columnCount() - 1, 220)


def configure_dialog(dialog):
    palette = dialog.palette()
    for role in (
        QPalette.ColorRole.Window,
        QPalette.ColorRole.Base,
        QPalette.ColorRole.AlternateBase,
    ):
        palette.setColor(role, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#17212b"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#17212b"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#e8f0ff"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#17212b"))
    dialog.setPalette(palette)
    dialog.setStyleSheet("""
        QDialog { background: #ffffff; color: #17212b; }
        QDialog QWidget { background: #ffffff; color: #17212b; }
        QDialog QTableWidget {
            background: #ffffff;
            color: #17212b;
            alternate-background-color: #f6f8fb;
            selection-background-color: #dbe7ff;
            selection-color: #17212b;
            gridline-color: #d8e0e8;
        }
        QDialog QHeaderView::section {
            background: #e6ebf0;
            color: #17212b;
            border: 1px solid #d8e0e8;
            padding: 6px;
            font-weight: 700;
        }
        QDialog QPushButton {
            background: #e8f0ff;
            color: #2459bd;
            border: 1px solid #bdd0f7;
            border-radius: 8px;
            padding: 8px 18px;
        }
    """)


APP_STYLESHEET = """
QWidget {
    color: #17212b;
    font-family: 'Segoe UI';
    font-size: 12px;
}

QMainWindow {
    background-color: #f6f8fb;
}

QDialog {
    background-color: #f6f8fb;
    color: #17212b;
}

QDialog QLabel {
    background: transparent;
    color: #17212b;
}

QDialogButtonBox QPushButton {
    background-color: #e8f0ff;
    color: #2459bd;
    border: 1px solid #bdd0f7;
    border-radius: 8px;
    padding: 8px 18px;
    min-width: 80px;
}

QDialogButtonBox QPushButton:hover {
    background-color: #dbe7ff;
}

QMessageBox {
    background-color: #ffffff;
    color: #17212b;
}

QMessageBox QLabel {
    background-color: transparent;
    color: #17212b;
}

QMessageBox QPushButton {
    background-color: #243447;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    min-width: 80px;
}

QMessageBox QPushButton:hover {
    background-color: #1b2838;
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
    border: 1px solid #243447;
}

QCalendarWidget QToolButton,
QCalendarWidget QSpinBox {
    background-color: #ffffff;
    color: #17212b;
}

QCalendarWidget QAbstractItemView:enabled {
    background-color: #ffffff;
    color: #17212b;
    selection-background-color: #243447;
    selection-color: #ffffff;
}

QCalendarWidget QToolButton {
    background-color: #ffffff;
    color: #17212b;
    border: none;
    padding: 4px;
}

QCalendarWidget QToolButton:hover {
    background-color: #eef1f5;
}

QCalendarWidget QSpinBox {
    background-color: #ffffff;
    color: #17212b;
    selection-background-color: #243447;
    selection-color: #ffffff;
}

QCalendarWidget QWidget {
    background-color: #ffffff;
    color: #17212b;
}

QCalendarWidget QTableView {
    background-color: #ffffff;
    color: #17212b;
    selection-background-color: #243447;
    selection-color: #ffffff;
    alternate-background-color: #f6f8fb;
}

QTableWidget {
    background-color: #ffffff;
    color: #17212b;
    gridline-color: #e4e9ef;
    alternate-background-color: #f6f8fb;
    selection-background-color: #dfe5eb;
    selection-color: #17212b;
    min-height: 220px;
    max-height: 320px;
}

QTableWidget QAbstractItemView {
    background-color: #ffffff;
    color: #17212b;
    selection-background-color: #dbe7ff;
    selection-color: #17212b;
}

QHeaderView::section,
QTableWidget QHeaderView::section {
    background-color: #e6ebf0;
    color: #17212b;
    border: 1px solid #d8e0e8;
    padding: 6px;
    font-weight: 700;
}

QDateEdit {
    selection-background-color: #243447;
    selection-color: #ffffff;
}
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
QPushButton:hover:!checked {
    background: #eef1f5;
    color: #17212b;
}
QPushButton:pressed {
    background: #dfe5eb;
}
QPushButton:checked {
    background: #e6ebf0;
    color: #243447;
    border: 1px solid #c7d0d9;
}
QPushButton:checked:hover {
    background: #dfe5eb;
    color: #1b2838;
    border: 1px solid #b8c4cf;
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
