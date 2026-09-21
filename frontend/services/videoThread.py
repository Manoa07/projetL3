import os
import time
import urllib.request
from collections import deque
from datetime import datetime
from pathlib import Path

import cv2
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage

from services.yolo_detector import YoloDetector

POSE_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
)


def ensure_pose_model(model_path: Path) -> Path:
    """Télécharge le modèle MediaPipe si absent pour ne pas désactiver la posture."""
    if model_path.exists():
        return model_path

    model_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[VideoThread] Modèle pose absent, téléchargement en cours : {model_path}")
    try:
        urllib.request.urlretrieve(POSE_MODEL_URL, str(model_path))
        print(f"[VideoThread] Modèle pose téléchargé : {model_path}")
        return model_path
    except Exception as exc:
        raise FileNotFoundError(
            f"Modèle pose introuvable et impossible à télécharger ({model_path}). "
            f"Vérifiez la connexion Internet ou placez le fichier manuellement. Erreur: {exc}"
        ) from exc


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    alert_signal = pyqtSignal(str, str)

    def __init__(self, camera_source=0, camera_name="Caméra"):
        super().__init__()
        self.camera_source = camera_source
        self.camera_name = camera_name
        self._run_flag = True
        self.cap = None
        self._last_alerts = {}
        self._alert_cooldown = 5.0
        self._gesture_history = deque(maxlen=8)
        self._gesture_vote_threshold = 3
        self._pose_timestamp_ms = 0

    @staticmethod
    def _forbidden_objects():
        configured = os.getenv(
            "YOLO_FORBIDDEN_OBJECTS",
            "cell phone,laptop,tablet,book,backpack,bottle",
        )
        return {item.strip().lower() for item in configured.split(",") if item.strip()}

    def _emit_object_alerts(self, detections):
        forbidden_objects = self._forbidden_objects()
        now = time.time()
        for detection in detections:
            label = detection.get("label", "").strip().lower()
            if label not in forbidden_objects:
                continue
            if now - self._last_alerts.get(label, 0) < self._alert_cooldown:
                continue
            self._last_alerts[label] = now
            confidence = detection.get("confidence", 0.0)
            message = f"[{self.camera_name}] Objet interdit détecté : {label} ({confidence:.0%})"
            self.alert_signal.emit(message, datetime.now().strftime("%H:%M:%S"))

    def _create_pose_detector(self):
        model_path = Path(__file__).resolve().parents[1] / "models" / "pose_landmarker.task"
        try:
            model_path = ensure_pose_model(model_path)
        except FileNotFoundError as error:
            print(f"[VideoThread] {error}")
            return None

        try:
            from mediapipe.tasks.python import BaseOptions
            from mediapipe.tasks.python.vision import (
                PoseLandmarker,
                PoseLandmarkerOptions,
                RunningMode,
            )

            options = PoseLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=str(model_path)),
                running_mode=RunningMode.VIDEO,
                num_poses=10,
                min_pose_detection_confidence=0.4,
                min_pose_presence_confidence=0.4,
                min_tracking_confidence=0.4,
            )
            detector = PoseLandmarker.create_from_options(options)
            print(f"[VideoThread] Modèle gestes chargé : {model_path}")
            return detector
        except Exception as error:
            print(f"[VideoThread] Détection des gestes indisponible : {error}")
            return None

    def _emit_gesture_alerts(self, frame, pose_detector):
        if pose_detector is None:
            return

        try:
            import mediapipe as mp
            from posture_detection.mouvement import detect_suspicious_movements

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp_ms = int(time.monotonic() * 1000)
            if timestamp_ms <= self._pose_timestamp_ms:
                timestamp_ms = self._pose_timestamp_ms + 1
            self._pose_timestamp_ms = timestamp_ms
            result = pose_detector.detect_for_video(mp_image, timestamp_ms)
            detected_events = set()
            for landmarks in result.pose_landmarks:
                detected_events.update(detect_suspicious_movements(landmarks))

            self._gesture_history.append(detected_events)
            recent_events = set().union(*self._gesture_history) if self._gesture_history else set()
            stable_events = {
                event for event in recent_events
                if sum(event in frame_events for frame_events in self._gesture_history)
                >= self._gesture_vote_threshold
            }
            for event in stable_events:
                alert_key = f"gesture:{event}"
                now = time.time()
                if now - self._last_alerts.get(alert_key, 0) < self._alert_cooldown:
                    continue
                self._last_alerts[alert_key] = now
                message = f"[{self.camera_name}] Geste suspect détecté : {event}"
                self.alert_signal.emit(message, datetime.now().strftime("%H:%M:%S"))
        except Exception as error:
            print(f"[VideoThread] Erreur de détection des gestes : {error}")

    def _open_capture(self):
        candidates = []
        seen = set()

        if isinstance(self.camera_source, (int, str)):
            candidates.append(self.camera_source)

        if self.camera_source not in (0, 1):
            candidates.extend([0, 1])

        if isinstance(self.camera_source, str) and self.camera_source.startswith("http"):
            candidates = [self.camera_source]

        ordered = []
        for candidate in candidates:
            key = str(candidate)
            if key not in seen:
                seen.add(key)
                ordered.append(candidate)

        for candidate in ordered:
            cap = cv2.VideoCapture(candidate)
            if cap.isOpened():
                if self.cap is not None and self.cap.isOpened():
                    self.cap.release()
                self.cap = cap
                self.camera_source = candidate
                return True
            cap.release()

        return False

    def run(self):
        detector = None
        pose_detector = self._create_pose_detector()

        try:
            detector = YoloDetector(
                model_path=os.getenv("YOLO_MODEL_PATH"),
                confidence=float(os.getenv("YOLO_CONFIDENCE", "0.25")),
                device=os.getenv("YOLO_DEVICE"),
            )
            print(f"[VideoThread] Modèle YOLO chargé : {detector.model_path}")
        except Exception as error:
            print(f"[VideoThread] YOLO indisponible, caméra sans alertes objet : {error}")

        try:
            if not self._open_capture():
                print(f"[VideoThread] Impossible d'ouvrir {self.camera_name}: {self.camera_source}")
                return

            reconnect_attempts = 0
            while self._run_flag:
                if self.cap is None or not self.cap.isOpened():
                    reconnect_attempts += 1
                    if reconnect_attempts > 5:
                        print(f"[VideoThread] Caméra {self.camera_name} hors service après plusieurs tentatives de reconnexion.")
                        break
                    time.sleep(0.5)
                    if not self._open_capture():
                        continue
                    reconnect_attempts = 0
                    continue

                ok, frame = self.cap.read()
                if not ok:
                    reconnect_attempts += 1
                    if reconnect_attempts > 5:
                        print(f"[VideoThread] Flux invalide pour {self.camera_name}, arrêt du thread.")
                        break
                    time.sleep(0.5)
                    self.cap.release()
                    self.cap = None
                    self._open_capture()
                    continue

                reconnect_attempts = 0
                gesture_frame = frame.copy()
                self._emit_gesture_alerts(gesture_frame, pose_detector)
                if detector is not None:
                    try:
                        frame, detections = detector.annotate(frame)
                        self._emit_object_alerts(detections)
                    except Exception as error:
                        print(f"[VideoThread] Erreur de détection YOLO : {error}")
                        detector = None
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channels = rgb.shape
                image = QImage(rgb.data, width, height, channels * width, QImage.Format.Format_RGB888).copy()
                self.change_pixmap_signal.emit(image)
                time.sleep(0.01)
        finally:
            if pose_detector is not None:
                pose_detector.close()
            if self.cap is not None:
                self.cap.release()
                self.cap = None

    def stop(self):
        self._run_flag = False
        self.quit()
        self.wait(2000)
