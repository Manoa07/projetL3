import cv2
import requests
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage

from config import API_BASE_URL, API_TIMEOUT


class PresenceThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    student_detected_signal = pyqtSignal(str)

    def __init__(self, id_cours):
        super().__init__()
        self.id_cours = id_cours
        self._run_flag = True

    def run(self):
        camera = cv2.VideoCapture(0)
        try:
            while self._run_flag and camera.isOpened():
                ok, frame = camera.read()
                if not ok:
                    break
                self._detect_presence(frame)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channels = rgb.shape
                image = QImage(rgb.data, width, height, channels * width, QImage.Format.Format_RGB888).copy()
                self.change_pixmap_signal.emit(image)
        finally:
            camera.release()

    def _detect_presence(self, frame):
        ok, buffer = cv2.imencode(".jpg", frame)
        if not ok:
            return
        try:
            response = requests.post(
                f"{API_BASE_URL}/presence/detecter",
                files={"file": ("frame.jpg", buffer.tobytes(), "image/jpeg")},
                data={"id_cours": self.id_cours},
                timeout=API_TIMEOUT,
            )
            if response.ok:
                for result in response.json().get("resultats", []):
                    name = result.get("nom")
                    if name and name != "Inconnu":
                        self.student_detected_signal.emit(name)
        except requests.RequestException as error:
            print(f"Erreur API présence : {error}")

    def stop(self):
        self._run_flag = False
        self.wait()


presenceTheard = PresenceThread
