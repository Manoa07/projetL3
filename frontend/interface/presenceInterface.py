from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt, QSize
import requests
from components.icon_loader import load_icon
from components.theme import NAV_BUTTON_STYLE
from components.cameraView import CameraView
from views.elevesView import ElevesView
from views.ajoutEleveView import AjoutEleveView
from views.ajoutCoursView import AjoutCoursView
from views.ajoutExamenView import AjoutExamenView
from views.gestionReferentielsView import GestionReferentielsView
from services.presenceTheard import PresenceThread
from services.events import global_signals

class PresenceInterface(QWidget):
    def __init__(self, back_to_home_callback):
        super().__init__()
        self.back_to_home = back_to_home_callback
        self.camera_active = False
        self.video_thread = None # Stockage de l'instance du thread
        global_signals.data_changed.connect(self.load_cours)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- 1. BARRE LATÉRALE ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(155)
        self.sidebar.setStyleSheet("""
            QFrame#Sidebar {
                background-color: #151826;
                border-right: 1px solid #24273d;
            }
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 12, 10, 12)
        sidebar_layout.setSpacing(8)

        self.btn_cam = self.create_nav_btn("LIVE", 0, load_icon("live"))
        self.btn_list = self.create_nav_btn("ÉLÈVES", 1, load_icon("users"))
        self.btn_add = self.create_nav_btn("AJOUT", 2, load_icon("add"))
        self.btn_add_cours = self.create_nav_btn("COURS", 3, load_icon("course"))
        self.btn_add_examen = self.create_nav_btn("EXAMEN", 4, load_icon("course"))
        self.btn_data = self.create_nav_btn("DONNÉES", 5, load_icon("add"))
        self.btn_cam.setChecked(True)

        sidebar_layout.addWidget(self.btn_cam)
        sidebar_layout.addWidget(self.btn_list)
        sidebar_layout.addWidget(self.btn_add)
        sidebar_layout.addWidget(self.btn_add_cours)
        sidebar_layout.addWidget(self.btn_add_examen)
        sidebar_layout.addWidget(self.btn_data)
        sidebar_layout.addStretch()

        btn_back = QPushButton("Accueil")
        btn_back.setIcon(load_icon("home"))
        btn_back.setStyleSheet("color: #e74c3c; padding: 14px; font-weight: 700; border-radius: 12px;")
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
        self.stack.addWidget(AjoutCoursView()) # Index 3
        self.stack.addWidget(AjoutExamenView()) # Index 4
        self.stack.addWidget(GestionReferentielsView()) # Index 5

        self.stack.setStyleSheet("background: transparent;")
        layout.addWidget(self.stack, stretch=5)
    def load_cours(self):
        try:
            response = requests.get("http://127.0.0.1:8000/cours/all")
            response.raise_for_status()
            cours_list = response.json()

            self.cours_select.clear()

            for cours in cours_list:
                # affichage = nom du cours
                # data = id du cours
                self.cours_select.addItem(
                    f"{cours.get('nom_cours') or cours.get('Nom_cours', '')} - "
                    f"Salle #{cours.get('id_salle_salle') or cours.get('Salle_cours', '')}",
                    cours["Id_cours"]
                )
        except Exception as e:
            print("Erreur chargement cours :", e)
    def setup_placeholder_page(self):
        """Crée l'interface d'attente avec le bouton de démarrage"""
        self.cam_placeholder = QWidget()
        placeholder_layout = QVBoxLayout(self.cam_placeholder)
        placeholder_layout.setContentsMargins(24, 24, 24, 24)
        placeholder_layout.setSpacing(16)

        title = QLabel("<b style='color:#4facfe; font-size:18px;'>POINTAGE : RECONNAISSANCE FACIALE</b>")
        placeholder_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignTop)

        # BUG-14 : cours_select créé et ajouté au layout AVANT insertWidget
        self.cours_select = QComboBox()
        self.cours_select.setFixedWidth(300)
        self.cours_select.setStyleSheet("""
            QComboBox {
                background: #1a1f2f;
                border: 1px solid #2a2f45;
                border-radius: 10px;
                padding: 10px 12px;
                color: #f4f7fb;
            }
            QComboBox::drop-down { border: none; }
        """)

        self.start_btn = QPushButton("ACTIVER LE SCAN DE PRÉSENCE")
        self.start_btn.setIcon(load_icon("play"))
        self.start_btn.setFixedSize(300, 70)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: #4facfe;
                color: white;
                font-weight: 700;
                border-radius: 12px;
                font-size: 13px;
                padding: 12px 16px;
            }
            QPushButton:hover { background: #37b8ff; }
        """)
        self.start_btn.clicked.connect(self.start_presence_camera)

        placeholder_layout.addStretch()
        placeholder_layout.addWidget(self.cours_select, alignment=Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.addStretch()

        # insertWidget après construction complète du widget
        self.stack.insertWidget(0, self.cam_placeholder)
        # Charger les cours
        self.load_cours()

    def start_presence_camera(self):
        #selection cours
        self.selected_cours_id = self.cours_select.currentData()
        if not self.selected_cours_id:
            print("Aucun cours sélectionné")
            return
        """Active la caméra et lance le VideoThread pour le traitement"""
        self.cam_scroll = QScrollArea()
        self.cam_scroll.setWidgetResizable(True)
        self.cam_scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(24, 24, 24, 24)
        container_layout.setSpacing(16)
        
        running_label = QLabel("SCAN EN COURS...")
        running_label.setStyleSheet("color:#f4f7fb; font-size:18px; font-weight:700; letter-spacing: 1px;")
        container_layout.addWidget(running_label)


        # La vue caméra
        self.camera_view = CameraView("TERMINAL DE PRÉSENCE", "Scan biométrique actif")
        container_layout.addWidget(self.camera_view)
        
        # --- INITIALISATION DU THREAD VIDEO ---
        self.video_thread = PresenceThread(self.selected_cours_id)
        self.video_thread.change_pixmap_signal.connect(
            self.camera_view.update_frame
        )
        self.video_thread.student_detected_signal.connect(
            self.update_presence_label
        )
        self.video_thread.start()        
        # Bouton d'arrêt
        self.stop_btn = QPushButton("ARRÊTER LE SCAN")
        self.stop_btn.setIcon(load_icon("stop"))
        self.stop_btn.setFixedSize(200, 45)
        self.stop_btn.setStyleSheet("background: #34495e; color: white; border-radius: 12px; padding: 12px 16px; font-weight: 700;")
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

    def create_nav_btn(self, text, index, icon):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setFixedSize(135, 86)
        btn.setIcon(icon)
        btn.setIconSize(QSize(24, 24))
        btn.setStyleSheet(NAV_BUTTON_STYLE)
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(index))
        return btn
