import sys
from PyQt6.QtWidgets import QApplication
from components.examGuardApp import ExamGuardApp
from qasync import QEventLoop
import asyncio
import sys
if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop=QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = ExamGuardApp()
    window.showMaximized()
    with loop:
        loop.run_forever()