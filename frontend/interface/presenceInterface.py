from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
                             QFrame, QLabel, QStackedWidget, QScrollArea)
from PyQt6.QtCore import Qt
from components.cameraView import CameraView
from views.elevesView import ElevesView
from views.ajoutEleveView import AjoutEleveView

class PresenceInterface(QWidget):
    def __init__(self, back_to_home_callback):
        super().__init__()
        self.back_to_home = back_to_home_callback
        self.camera_active = False
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- 1. BARRE LATÉRALE ---
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

        self.btn_cam = self.create_nav_btn("📷\nLIVE", btn_style, 0)
        self.btn_list = self.create_nav_btn("📋\nÉLÈVES", btn_style, 1)
        self.btn_add = self.create_nav_btn("➕\nAJOUT", btn_style, 2)
        self.btn_cam.setChecked(True)

        sidebar_layout.addWidget(self.btn_cam)
        sidebar_layout.addWidget(self.btn_list)
        sidebar_layout.addWidget(self.btn_add)
        sidebar_layout.addStretch()

        btn_back = QPushButton("🏠\nAccueil")
        btn_back.setStyleSheet("color: #e74c3c; border: none; padding: 15px; font-weight: bold;")
        btn_back.clicked.connect(self.handle_back_home)
        sidebar_layout.addWidget(btn_back)

        layout.addWidget(self.sidebar)

        # --- 2. ZONE CENTRALE ---
        self.stack = QStackedWidget()
        
        # Initialisation de la page d'attente (Index 0)
        self.setup_placeholder_page()
        
        # Autres pages
        self.stack.addWidget(ElevesView()) # Index 1
        self.stack.addWidget(AjoutEleveView()) # Index 2

        layout.addWidget(self.stack, stretch=5)

    def setup_placeholder_page(self):
        """Crée l'interface d'attente avec le bouton de démarrage"""
        self.cam_placeholder = QWidget()
        placeholder_layout = QVBoxLayout(self.cam_placeholder)
        
        title = QLabel("<b style='color:#4facfe; font-size:18px;'>POINTAGE : RECONNAISSANCE FACIALE</b>")
        placeholder_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignTop)

        self.start_btn = QPushButton("🚀 ACTIVER LE SCAN DE PRÉSENCE")
        self.start_btn.setFixedSize(300, 70)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: #4facfe; color: white; font-weight: bold; border-radius: 10px; font-size: 13px;
            }
            QPushButton:hover { background: #00f2fe; }
        """)
        self.start_btn.clicked.connect(self.start_presence_camera)
        
        placeholder_layout.addStretch()
        placeholder_layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.addStretch()
        
        self.stack.insertWidget(0, self.cam_placeholder)

    def start_presence_camera(self):
        """Active la caméra et l'insère dans une ScrollArea"""
        # Création de la ScrollArea pour le scroll
        self.cam_scroll = QScrollArea()
        self.cam_scroll.setWidgetResizable(True)
        self.cam_scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        # Titre
        container_layout.addWidget(QLabel("<b style='color:#4facfe; font-size:18px;'>SCAN EN COURS...</b>"))
        
        # La vue caméra (utilise VideoThread en interne)
        # Note: Assurez-vous que CameraView gère son propre VideoThread ou passez-lui un callback
        self.camera_view = CameraView("TERMINAL DE PRÉSENCE", "Scan biométrique actif")
        container_layout.addWidget(self.camera_view)
        
        # Bouton d'arrêt
        self.stop_btn = QPushButton("⏹ ARRÊTER LE SCAN")
        self.stop_btn.setFixedSize(200, 45)
        self.stop_btn.setStyleSheet("background: #34495e; color: white; border-radius: 5px; font-weight: bold;")
        self.stop_btn.clicked.connect(self.stop_presence_camera)
        container_layout.addWidget(self.stop_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        container_layout.addStretch()
        
        self.cam_scroll.setWidget(container)
        
        # Remplacement dans le stack
        self.stack.removeWidget(self.cam_placeholder)
        self.stack.insertWidget(0, self.cam_scroll)
        self.stack.setCurrentIndex(0)
        self.camera_active = True

    def stop_presence_camera(self):
        """Arrête proprement le matériel et revient au bouton de départ"""
        if self.camera_active:
            # Si votre CameraView a un thread, il faut l'arrêter ici
            # Exemple si CameraView possède une méthode stop :
            if hasattr(self.camera_view, 'stop_camera'):
                self.camera_view.stop_camera()
            
            self.stack.removeWidget(self.cam_scroll)
            self.cam_scroll.deleteLater()
            self.camera_active = False
            
            # Recréer la page d'attente
            self.setup_placeholder_page()
            self.stack.setCurrentIndex(0)

    def handle_back_home(self):
        """S'assure que la caméra est coupée si on quitte l'interface"""
        self.stop_presence_camera()
        self.back_to_home()

    def create_nav_btn(self, text, style, index):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setFixedSize(100, 80)
        btn.setStyleSheet(style)
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(index))
        return btn