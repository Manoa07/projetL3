from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from components.cameraView import CameraView
from services.videoThread import VideoThread 

class LiveView(QWidget):
    def __init__(self, alert_callback):
        super().__init__()
        self.alert_callback = alert_callback 
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b style='color:#4facfe; font-size:18px;'>SURVEILLANCE EN DIRECT</b>"))
        
        grid = QGridLayout()
        self.cam1 = CameraView("SALLE EXAMEN A", "Identification & Posture")
        grid.addWidget(self.cam1, 0, 0)
        
        # Conserver les références pour pouvoir les nettoyer
        self.cams = [self.cam1]
        
        # Placeholders
        c2 = CameraView("SALLE EXAMEN B", "Reconnaissance Faciale")
        c3 = CameraView("COULOIR 1", "Comptage")
        c4 = CameraView("ENTRÉE", "Vérification")
        
        grid.addWidget(c2, 0, 1)
        grid.addWidget(c3, 1, 0)
        grid.addWidget(c4, 1, 1)
        self.cams.extend([c2, c3, c4])
        
        layout.addLayout(grid)

        # Initialisation du Thread
        self.thread = VideoThread(0) 
        self.thread.change_pixmap_signal.connect(self.cam1.update_frame)
        self.thread.alert_signal.connect(self.alert_callback)
        self.thread.start()

    def stop_camera(self):
        """Arrête le thread et libère les ressources matérielles"""
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.stop() # Demande l'arrêt (doit appeler cap.release() dans VideoThread)
            self.thread.wait() # Attend la fin réelle du thread pour libérer la LED
        
        for cam in self.cams:
            cam.clear_view()