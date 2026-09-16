import threading
from concurrent.futures import ThreadPoolExecutor
import time
import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
import requests
from config import API_BASE_URL


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
        cap = cv2.VideoCapture(0)
        # Réduire le buffer caméra à 1 pour éviter tout décalage temporel
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        try:
            while self._run_flag:
                ret, frame = cap.read()
                if not ret:
                    break

                now = time.time()

                # Déclencher une détection asynchrone si le worker précédent a terminé
                if not self.is_detecting and (now - self.last_detection_sent_time >= self.detection_interval):
                    self.is_detecting = True
                    self.last_detection_sent_time = now
                    # Envoi d'une copie dans le thread d'arrière-plan sans bloquer la boucle vidéo
                    self.executor.submit(self._async_detect, frame.copy())

                # Dessiner les détections récentes (conservées pendant 1.2 seconde)
                if now - self.last_detection_received_time < 1.2:
                    with self._lock:
                        detections_to_draw = list(self.current_detections)

                    for face in detections_to_draw:
                        x = face.get("x", 0)
                        y = face.get("y", 0)
                        w = face.get("w", 0)
                        h = face.get("h", 0)
                        nom = face.get("nom", "Inconnu")
                        status = face.get("status", "")

                        color = (0, 255, 0) if status == "present" else (0, 0, 255)

                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                        cv2.putText(
                            frame,
                            nom,
                            (x, max(20, y - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            color,
                            2,
                        )

                # Rendu fluide de la frame courante (30 FPS constant)
                try:
                    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_image.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(
                        rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
                    ).copy()
                    self.change_pixmap_signal.emit(qt_image)
                except Exception as e:
                    print("Erreur affichage QImage :", e)

                # Micro-pause pour relâcher le CPU et s'aligner sur la fréquence caméra (~30 FPS)
                time.sleep(0.005)

        finally:
            cap.release()

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


# Compatibilité avec l'ancien nom mal orthographié utilisé dans l'interface.
presenceTheard = PresenceThread

