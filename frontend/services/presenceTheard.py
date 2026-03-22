
import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
#from Presence.presence import SystemePresence # Import de votre classe existante

class presenceTheard(QThread):
    # Signal pour envoyer l'image à l'interface
    change_pixmap_signal = pyqtSignal(QImage)
    
    def __init__(self):
        super().__init__()
        self._run_flag = True
   #     self.systeme = SystemePresence(seuil_distance=0.6) # Initialisation du modèle

    def run(self):
        cap = cv2.VideoCapture(0)
        while self._run_flag:
            ret, frame = cap.read()
            if ret:
                # 1. Logique de reconnaissance (reprise de votre code presence.py)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                detections = self.systeme.detector.detect_faces(rgb_frame)

                for det in detections:
                    x, y, w, h = det['box']
                    face = rgb_frame[max(0, y):y+h, max(0, x):x+w]
                    
                    if face.size > 0:
                        embedding = self.systeme.obtenir_embedding(face)
                        nom, dist, id_eleve = self.systeme.comparer_visage(embedding)

                        if nom:
                            # Logique d'enregistrement simplifiée pour l'exemple
                            self.systeme.enregistrer_presence_db(id_eleve, nom)
                            color = (0, 255, 0) # Vert
                            label = f"{nom}"
                        else:
                            color = (255, 0, 0) # Rouge
                            label = "Inconnu"
                        
                        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                        cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                # 2. Conversion pour PyQt6
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                qt_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
                self.change_pixmap_signal.emit(qt_img)
        
        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()