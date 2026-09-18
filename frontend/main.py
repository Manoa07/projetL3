import sys
from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtWidgets import QApplication
from components.examGuardApp import ExamGuardApp
from components.theme import APP_STYLESHEET
from qasync import QEventLoop
import asyncio

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    # Set global application font to Segoe UI Variable for a more modern look
    try:
        app.setFont(QFont("Segoe UI Variable"))
    except Exception:
        # Fall back silently if font is not available on the system
        pass
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f6f8fb"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#17212b"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#17212b"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#243447"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
    app.setPalette(palette)
    app.setStyleSheet(APP_STYLESHEET)
    loop=QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = ExamGuardApp()
    window.setMinimumSize(1100, 700)
    window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
    window.show()
    with loop:
        loop.run_forever()