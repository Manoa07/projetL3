import sys
from PyQt6.QtWidgets import QApplication
from components.examGuardApp import ExamGuardApp
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExamGuardApp()
    window.showMaximized()
    sys.exit(app.exec())