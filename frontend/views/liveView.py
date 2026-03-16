from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from components.cameraView import CameraView

class LiveView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b style='color:#4facfe; font-size:18px;'>SURVEILLANCE EN DIRECT</b>"))
        
        grid = QGridLayout()
        grid.addWidget(CameraView("SALLE EXAMEN A", "Identification & Présence"), 0, 0)
        grid.addWidget(CameraView("SALLE EXAMEN B", "Reconnaissance Faciale"), 0, 1)
        grid.addWidget(CameraView("COULOIR 1", "Comptage Automatique"), 1, 0)
        grid.addWidget(CameraView("ENTRÉE", "Vérification Identité"), 1, 1)
        
        layout.addLayout(grid)