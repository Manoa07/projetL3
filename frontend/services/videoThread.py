import time

import cv2
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    alert_signal = pyqtSignal(str, str)

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self._run_flag = True
        self.cap = None

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        try:
            while self._run_flag and self.cap.isOpened():
                ok, frame = self.cap.read()
                if not ok:
                    break
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channels = rgb.shape
                image = QImage(rgb.data, width, height, channels * width, QImage.Format.Format_RGB888).copy()
                self.change_pixmap_signal.emit(image)
                time.sleep(0.01)
        finally:
            self.cap.release()
            self.cap = None

    def stop(self):
        self._run_flag = False
        self.quit()
        self.wait(2000)
