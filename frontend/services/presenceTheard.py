
import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
import requests
import time



class presenceTheard(QThread):
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
            time.sleep(0.06)
        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()