from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
                             QFrame, QLabel, QStackedWidget, QScrollArea)
from PyQt6.QtCore import Qt
from components.cameraView import CameraView
from views.elevesView import ElevesView
from views.ajoutEleveView import AjoutEleveView
# Import du thread de service pour la gestion de la caméra
from services.presenceTheard import presenceTheard 

class PresenceInterface(QWidget):
    def __init__(self, back_to_home_callback):
        super().__init__()
        self.back_to_home = back_to_home_callback
        self.camera_active = False
        self.video_thread = None # Stockage de l'instance du thread
        
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
        """Active la caméra et lance le VideoThread pour le traitement"""
        self.cam_scroll = QScrollArea()
        self.cam_scroll.setWidgetResizable(True)
        self.cam_scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        container_layout.addWidget(QLabel("<b style='color:#4facfe; font-size:18px;'>SCAN EN COURS...</b>"))
        
        # La vue caméra
        self.camera_view = CameraView("TERMINAL DE PRÉSENCE", "Scan biométrique actif")
        container_layout.addWidget(self.camera_view)
        
        # --- INITIALISATION DU THREAD VIDEO ---
        #self.video_thread = presenceTheard()
        #self.video_thread.change_pixmap_signal.connect(self.camera_view.update_frame)
        # Connecter le signal de détection pour mettre à jour le label de présence
        #self.video_thread.student_detected_signal.connect(self.update_presence_label)
        #self.video_thread.start()
        
        # Bouton d'arrêt
        self.stop_btn = QPushButton("⏹ ARRÊTER LE SCAN")
        self.stop_btn.setFixedSize(200, 45)
        self.stop_btn.setStyleSheet("background: #34495e; color: white; border-radius: 5px; font-weight: bold;")
        self.stop_btn.clicked.connect(self.stop_presence_camera)
        container_layout.addWidget(self.stop_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        container_layout.addStretch()
        self.cam_scroll.setWidget(container)
        
        self.stack.removeWidget(self.cam_placeholder)
        self.stack.insertWidget(0, self.cam_scroll)
        self.stack.setCurrentIndex(0)
        self.camera_active = True

    def update_presence_label(self, student_name):
        """Met à jour l'en-tête de CameraView avec le nom détecté"""
        if hasattr(self, 'camera_view'):
            self.camera_view.presence.setText(f"DERNIER: {student_name}")

    def stop_presence_camera(self):
        """Arrête proprement le thread et revient au bouton de départ"""
        if self.camera_active and self.video_thread:
            # Arrêt propre du thread OpenCV
            self.video_thread.stop()
            self.video_thread = None
            
            self.stack.removeWidget(self.cam_scroll)
            self.cam_scroll.deleteLater()
            self.camera_active = False
            
            # Recréer la page d'attente
            self.setup_placeholder_page()
            self.stack.setCurrentIndex(0)

    def handle_back_home(self):
        """Coupe la caméra avant de retourner à l'accueil"""
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