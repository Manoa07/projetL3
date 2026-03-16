from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt, QTimer

class SurveillanceDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Système de Surveillance Vidéo Intelligent - ISPM") # [cite: 25]
        self.resize(1200, 800)

        # Widget Principal
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QHBoxLayout(self.main_widget)

        # --- PARTIE GAUCHE : FLUX VIDÉO ---
        self.video_container = QVBoxLayout()
        self.video_label = QLabel("Flux Caméra en Temps Réel") # 
        self.video_label.setStyleSheet("background-color: black; color: white;")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_container.addWidget(self.video_label, stretch=4)
        
        # Boutons d'action
        self.btn_start = QPushButton("Démarrer la Surveillance")
        self.video_container.addWidget(self.btn_start)
        
        self.layout.addLayout(self.video_container, stretch=3)

        # --- PARTIE DROITE : INFOS & PRÉSENCE ---
        self.info_panel = QVBoxLayout()
        
        # Identification des élèves
        self.info_panel.addWidget(QLabel("<b>Identification des Élèves</b>")) # [cite: 5]
        self.presence_table = QTableWidget(10, 2)
        self.presence_table.setHorizontalHeaderLabels(["Nom de l'élève", "Statut"]) # [cite: 13]
        self.info_panel.addWidget(self.presence_table)

        # Alertes Comportement
        self.info_panel.addWidget(QLabel("<b>Alertes de Comportement</b>")) # [cite: 6]
        self.alert_log = QLabel("Aucun incident détecté")
        self.alert_log.setStyleSheet("color: green;")
        self.info_panel.addWidget(self.alert_log)

        self.layout.addLayout(self.info_panel, stretch=1)