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
        
        # Placeholders pour les autres caméras
        grid.addWidget(CameraView("SALLE EXAMEN B", "Reconnaissance Faciale"), 0, 1)
        grid.addWidget(CameraView("COULOIR 1", "Comptage"), 1, 0)
        grid.addWidget(CameraView("ENTRÉE", "Vérification"), 1, 1)
        
        layout.addLayout(grid)

        # Initialisation du Thread avec l'index 0 (Webcam)
        self.thread = VideoThread(0) 
        self.thread.change_pixmap_signal.connect(self.cam1.update_frame)
        self.thread.alert_signal.connect(self.alert_callback)
        self.thread.start()

    def stop_camera(self):
        """Appelée lors de la fermeture pour éviter les crashs"""
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.stop()