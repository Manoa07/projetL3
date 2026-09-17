import cv2
import os
import time
import requests
import mediapipe as mp
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage

from posture_detection.posture_detection import PoseLandmarker, options, define_precision_tolerance
from posture_detection.mouvement import detect_suspicious_movements
from services.yolo_detector import YoloDetector

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    alert_signal = pyqtSignal(str, str)

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self._run_flag = True
        self.cap = None
        self.yolo_detector = None
        self.yolo_alert_cooldown = float(os.getenv("YOLO_ALERT_COOLDOWN", "5"))
        self.last_yolo_alerts = {}
        self.forbidden_objects = {
            item.strip().lower()
            for item in os.getenv(
                "YOLO_FORBIDDEN_OBJECTS",
                "cell phone,laptop,tablet,book,backpack,bottle",
            ).split(",")
            if item.strip()
        }

    def _send_object_alert(self, detection):
        object_name = detection["label"]
        now = time.time()
        if now - self.last_yolo_alerts.get(object_name, 0) < self.yolo_alert_cooldown:
            return
        self.last_yolo_alerts[object_name] = now

        message = f"Objet interdit detecte: {object_name}"
        self.alert_signal.emit(message, time.strftime("%H:%M"))
        try:
            response = requests.post(
                os.getenv("SURVEILLANCE_API_URL", "http://127.0.0.1:8000/surveillance/object-alert"),
                json={
                    "id_examen": int(os.getenv("EXAM_ID", "1")),
                    "id_eleve": None,
                    "object_name": object_name,
                    "confidence": detection.get("confidence"),
                },
                timeout=2,
            )
            response.raise_for_status()
        except (requests.RequestException, ValueError) as exc:
            print(f"Erreur envoi alerte objet: {exc}")

    def run(self):
        landmarker = PoseLandmarker.create_from_options(options)
        try:
            self.yolo_detector = YoloDetector(
                model_path=os.getenv("YOLO_MODEL_PATH"),
                confidence=float(os.getenv("YOLO_CONFIDENCE", "0.25")),
            )
            print(f"YOLO active avec {self.yolo_detector.model_path}")
        except (ImportError, FileNotFoundError, ValueError) as exc:
            self.yolo_detector = None
            print(f"YOLO desactive : {exc}")

        self.cap = cv2.VideoCapture(self.camera_index)
        start_ms = int(time.time() * 1000)

        try:
            while self._run_flag:
                if self.cap is None or not self.cap.isOpened():
                    break

                ret, frame = self.cap.read()
                if not ret or not self._run_flag:
                    break

                yolo_annotated = None
                if self.yolo_detector is not None:
                    try:
                        yolo_annotated, detections = self.yolo_detector.annotate(frame.copy())
                        for detection in detections:
                            if detection["label"] in self.forbidden_objects:
                                self._send_object_alert(detection)
                    except Exception as exc:
                        print(f"Erreur detection YOLO, desactivation : {exc}")
                        self.yolo_detector = None

                timestamp = int(time.time() * 1000) - start_ms + 1
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

                try:
                    result = landmarker.detect_for_video(mp_image, timestamp)
                except Exception:
                    result = None

                if result and result.pose_landmarks and self._run_flag:
                    suspicious_movements = []

                    for landmarks in result.pose_landmarks:
                        h, w, _ = frame.shape
                        points = [[lm.x * w, lm.y * h] for lm in landmarks]
                        
                        if landmarks[0].visibility > define_precision_tolerance:
                            movements = detect_suspicious_movements(points)
                            if movements:
                                suspicious_movements.extend(movements)

                    for msg in suspicious_movements:
                        if not self._run_flag:
                            break
                        self.alert_signal.emit(msg, time.strftime("%H:%M"))
                        cv2.putText(frame, f"ALERTE: {msg}", (10, 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                if yolo_annotated is not None:
                    frame = cv2.addWeighted(frame, 0.7, yolo_annotated, 0.3, 0)

                if self._run_flag:
                    display_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = display_rgb.shape
                    bytes_per_line = ch * w
                    qt_img = QImage(
                        display_rgb.data,
                        w,
                        h,
                        bytes_per_line,
                        QImage.Format.Format_RGB888,
                    ).copy()
                    self.change_pixmap_signal.emit(qt_img)

                time.sleep(0.01)

        finally:
            if self.cap is not None:
                try:
                    self.cap.release()
                except Exception:
                    pass
                self.cap = None

            if landmarker is not None:
                try:
                    landmarker.close()
                except Exception:
                    pass

    def stop(self):
        """Arrête la boucle et libère les ressources proprement."""
        self._run_flag = False
        self.quit()
        if not self.wait(2000):
            self.terminate()
            self.wait(500)
