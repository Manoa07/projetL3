import cv2
import time
import mediapipe as mp
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
from mediapipe.tasks.python import vision

# Importation de votre logique de détection
from posture_detection.posture_detection import PoseLandmarker, options, define_precision_tolerance
from posture_detection.mouvement import detect_suspicious_movements

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    alert_signal = pyqtSignal(str, str)

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self._run_flag = True  
        self.cap = None  # Initialisation de l'attribut pour éviter l'AttributeError

    def run(self):
        # Initialisation du landmarker (BUG-02 : instance unique ici, pas au niveau module)
        landmarker = PoseLandmarker.create_from_options(options)
        
        self.cap = cv2.VideoCapture(self.camera_index)
        # BUG-03 : timestamp relatif au démarrage du thread (MediaPipe VIDEO exige monotonique depuis 0)
        start_ms = int(time.time() * 1000)

        try:
            while self._run_flag:
                if self.cap is None or not self.cap.isOpened():
                    break

                ret, frame = self.cap.read()
                if not ret or not self._run_flag:
                    break

                # 1. Préparation de l'image pour MediaPipe
                timestamp = int(time.time() * 1000) - start_ms + 1  # toujours > 0 et croissant
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                
                # 2. Appel de la détection
                try:
                    result = landmarker.detect_for_video(mp_image, timestamp)
                except Exception:
                    result = None

                # 3. Traitement des résultats
                if result and result.pose_landmarks and self._run_flag:
                    suspicious_movements = []

                    for landmarks in result.pose_landmarks:
                        h, w, _ = frame.shape
                        points = [[lm.x * w, lm.y * h] for lm in landmarks]
                        
                        if landmarks[0].visibility > define_precision_tolerance:
                            movements = detect_suspicious_movements(points)
                            if movements:
                                suspicious_movements.extend(movements)

                    # 4. Envoi des alertes
                    for msg in suspicious_movements:
                        if not self._run_flag:
                            break
                        self.alert_signal.emit(msg, time.strftime("%H:%M"))
                        cv2.putText(frame, f"ALERTE: {msg}", (10, 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # 5. Conversion pour l'affichage PyQt (.copy() indispensable pour éviter les conflits mémoire)
                if self._run_flag:
                    h, w, ch = rgb_frame.shape
                    bytes_per_line = ch * w
                    qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
                    self.change_pixmap_signal.emit(qt_img)

                # Micro-pause pour relâcher le CPU
                time.sleep(0.01)
        
        finally:
            # Garantie que la caméra est libérée EXCLUSIVEMENT par ce thread pour éviter tout crash C++
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
        """Arrête la boucle et libère les ressources proprement sans crash"""
        self._run_flag = False
        self.quit()
        # On attend la fin réelle du thread avec un timeout de 2s
        if not self.wait(2000):
            self.terminate()
            self.wait(500)