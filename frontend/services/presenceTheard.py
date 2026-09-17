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
        self._lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.is_detecting = False
        self.current_detections = []
        self.last_detection_received_time = 0.0
        self.last_detection_sent_time = 0.0
        # Intervalle minimum entre deux requêtes d'analyse (ex: 0.3s ~ 3 requêtes/sec max)
        self.detection_interval = 0.3

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

    def _async_detect(self, frame):
        """Exécuté dans un thread séparé en arrière-plan sans bloquer l'affichage vidéo."""
        try:
            orig_h, orig_w = frame.shape[:2]
            target_w = 640
            if orig_w > target_w:
                scale = target_w / float(orig_w)
                target_h = int(orig_h * scale)
                resized = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_AREA)
            else:
                scale = 1.0
                resized = frame

            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
            _, buffer = cv2.imencode('.jpg', resized, encode_param)

            response = requests.post(
                f"{API_BASE_URL}/presence/detecter",
                files={"file": ("frame.jpg", buffer.tobytes(), "image/jpeg")},
                data={"id_cours": self.id_cours},
                timeout=3.0,
            )

            if response.status_code == 200:
                data = response.json()
                scaled_results = []
                for face in data.get("resultats", []):
                    scaled_face = {
                        "x": int(face.get("x", 0) / scale),
                        "y": int(face.get("y", 0) / scale),
                        "w": int(face.get("w", 0) / scale),
                        "h": int(face.get("h", 0) / scale),
                        "nom": face.get("nom", "Inconnu"),
                        "status": face.get("status", ""),
                    }
                    scaled_results.append(scaled_face)
                    nom = scaled_face["nom"]
                    if nom != "Inconnu":
                        self.student_detected_signal.emit(nom)

                with self._lock:
                    self.current_detections = scaled_results
                    self.last_detection_received_time = time.time()
        except Exception as e:
            print("Erreur détection asynchrone :", e)
        finally:
            self.is_detecting = False

    def stop(self):
        self._run_flag = False
        self.wait()
        try:
            self.executor.shutdown(wait=False, cancel_futures=True)
        except Exception:
            self.executor.shutdown(wait=False)


presenceTheard = PresenceThread

