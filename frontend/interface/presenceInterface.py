from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
                             QFrame, QLabel, QStackedWidget)
from PyQt6.QtCore import Qt
from components.cameraView import CameraView
from views.elevesView import ElevesView
from views.ajoutEleveView import AjoutEleveView

class PresenceInterface(QWidget):
    def __init__(self, back_to_home_callback):
        super().__init__()
        self.back_to_home = back_to_home_callback
        
        # Layout principal horizontal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- 1. BARRE LATÉRALE DE PRÉSENCE ---
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(100)
        self.sidebar.setStyleSheet("background-color: #1a1c2e; border-right: 1px solid #2d2f41;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        btn_style = """
            QPushButton { 
                background: transparent; border: none; color: #7a7c8c; 
                font-size: 10px; padding: 15px; font-weight: bold;
            }
            QPushButton:checked { 
                background: #24273d; color: #4facfe; border-left: 3px solid #4facfe; 
            }
        """

        # Boutons de navigation (Live, Liste, Ajout)
        self.btn_cam = self.create_nav_btn("📷\nLIVE", btn_style, 0)
        self.btn_list = self.create_nav_btn("📋\nÉLÈVES", btn_style, 1)
        self.btn_add = self.create_nav_btn("➕\nAJOUT", btn_style, 2)
        
        self.btn_cam.setChecked(True) # Par défaut sur la caméra

        sidebar_layout.addWidget(self.btn_cam)
        sidebar_layout.addWidget(self.btn_list)
        sidebar_layout.addWidget(self.btn_add)
        sidebar_layout.addStretch()

        # Bouton Retour Accueil (en bas)
        btn_back = QPushButton("🏠\nAccueil")
        btn_back.setStyleSheet("color: #e74c3c; border: none; padding: 15px; font-weight: bold;")
        btn_back.clicked.connect(self.back_to_home)
        sidebar_layout.addWidget(btn_back)

        layout.addWidget(self.sidebar)

        # --- 2. ZONE CENTRALE (STACKED WIDGET) ---
        self.stack = QStackedWidget()
        
        # PAGE 0 : LIVE (Caméra unique de reconnaissance)
        self.cam_page = QWidget()
        cam_layout = QVBoxLayout(self.cam_page)
        cam_layout.setContentsMargins(20, 20, 20, 20)
        cam_layout.addWidget(QLabel("<b style='color:#4facfe; font-size:18px;'>POINTAGE : RECONNAISSANCE FACIALE</b>"))
        
        self.camera = CameraView("TERMINAL DE PRÉSENCE", "Scan biométrique actif")
        cam_layout.addWidget(self.camera)
        
        cam_layout.addWidget(QLabel("<i>Veuillez vous placer devant la caméra pour valider votre présence</i>"), 
                             alignment=Qt.AlignmentFlag.AlignCenter)
        self.stack.addWidget(self.cam_page)
        
        # PAGE 1 : ÉLÈVES (Liste de la classe)
        self.list_page = QWidget()
        list_layout = QVBoxLayout(self.list_page)
        list_layout.setContentsMargins(20, 20, 20, 20)
        self.student_list = ElevesView()
        list_layout.addWidget(self.student_list)
        self.stack.addWidget(self.list_page)

        # PAGE 2 : AJOUT (Formulaire d'inscription)
        self.add_page = AjoutEleveView()
        self.stack.addWidget(self.add_page)

        layout.addWidget(self.stack, stretch=5)

    def create_nav_btn(self, text, style, index):
        """Utilitaire pour créer les boutons de la barre latérale"""
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setFixedSize(100, 80)
        btn.setStyleSheet(style)
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(index))
        return btn