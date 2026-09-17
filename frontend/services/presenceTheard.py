
import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
import requests
<<<<<<< Updated upstream
import time

=======
from config import API_BASE_URL, API_TIMEOUT
>>>>>>> Stashed changes


class PresenceThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    student_detected_signal=pyqtSignal(str)
    
    def __init__(self, id_cours):
        super().__init__()
        self.id_cours=id_cours
        self._run_flag = True

    def run(self):
        cap = cv2.VideoCapture(0)
        while self._run_flag:
            ret, frame = cap.read()
            
            if not ret:
                continue     
            print("frame ok")       
            _,buffer = cv2.imencode('.jpg',frame)
            try:
                reponse=requests.post(
                    "http://127.0.0.1:8000/presence/detecter",
                    files={"file":("frame.jpg",buffer.tobytes(),"image/jpeg")},
                    data={"id_cours" : self.id_cours}
                )
                data=reponse.json()

<<<<<<< Updated upstream
=======
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
                timeout=API_TIMEOUT,
            )

            if response.status_code == 200:
                data = response.json()
                scaled_results = []
>>>>>>> Stashed changes
                for face in data.get("resultats", []):
                    x = face.get("x", 0)
                    y = face.get("y", 0)
                    w = face.get("w", 0)
                    h = face.get("h", 0)
                    nom = face.get("nom", "Inconnu")

                    if nom != "Inconnu":
                        color = (0, 255, 0)
                    else:
                        color = (0, 0, 255)

                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    cv2.putText(frame, nom, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            except Exception as e:
                print("Erreur API ",e)
            try:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                self.change_pixmap_signal.emit(qt_image)
            except Exception as e:
                print(e)
            
        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()


# Compatibilité avec l'ancien nom mal orthographié utilisé dans l'interface.
presenceTheard = PresenceThread
