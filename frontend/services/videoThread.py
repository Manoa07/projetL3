import cv2
import time
import mediapipe as mp
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    alert_signal = pyqtSignal(str, str)

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self._run_flag = True
        self.cap = None # Stockage de la référence de capture

    def run(self):
        # Initialisation ici pour que ce soit dans le thread
        from posture_detection.posture_detection import PoseLandmarker, options
        landmarker = PoseLandmarker.create_from_options(options)
        
        self.cap = cv2.VideoCapture(self.camera_index) #

        while self._run_flag and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            timestamp = int(time.time() * 1000)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            result = landmarker.detect_for_video(mp_image, timestamp)

            if result.pose_landmarks:
                # ... (votre logique de détection reste inchangée) ...
                pass

            h, w, ch = rgb_frame.shape
            qt_img = QImage(rgb_frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
            self.change_pixmap_signal.emit(qt_img)

        if self.cap:
            self.cap.release() #

    def stop(self):
        """Libère physiquement la caméra et arrête le thread"""
        self._run_flag = False
        if self.cap and self.cap.isOpened():
            self.cap.release() # FORCE l'extinction de la LED immédiatement
        self.wait() # Attend la fin propre du thread