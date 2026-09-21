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
from PyQt6.QtGui import QPixmap
from pathlib import Path
import requests
from config import API_BASE_URL, API_TIMEOUT
from components.icon_loader import load_icon
from components.theme import NAV_BUTTON_STYLE, ACTION_BUTTON_STYLE
from components.cameraView import CameraView
from views.elevesView import ElevesView
from views.ajoutEleveView import AjoutEleveView
from views.statsView import StatsView
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
        self.sidebar.setFixedWidth(214)
        self.sidebar.setStyleSheet("""
            QFrame#Sidebar {
                background-color: #ffffff;
                border-right: 1px solid #e4e9ef;
            }
            QLabel#SidebarBrand {
                color: #17212b;
                font-size: 17px;
                font-weight: 800;
            }
            QLabel#SidebarSubtitle, QLabel#SidebarSection {
                color: #8a98a8;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1px;
            }
            QFrame#SidebarDivider {
                background-color: #edf1f5;
                max-height: 1px;
            }
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(16, 20, 16, 16)
        sidebar_layout.setSpacing(8)

        brand = QLabel()
        brand.setObjectName("SidebarBrand")
        logo_path = Path(__file__).resolve().parents[2] / "image" / "logo_ispm.png"
        logo = QPixmap(str(logo_path))
        brand.setPixmap(logo.scaled(174, 74, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        brand.setFixedHeight(74)
        brand.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        sidebar_layout.addWidget(brand)
        subtitle = QLabel("GESTION DES PRÉSENCES")
        subtitle.setObjectName("SidebarSubtitle")
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addSpacing(18)

        navigation_label = QLabel("NAVIGATION")
        navigation_label.setObjectName("SidebarSection")
        sidebar_layout.addWidget(navigation_label)
        sidebar_layout.addSpacing(4)

        self.btn_cam = self.create_nav_btn("Direct", 0, load_icon("live"))
        self.btn_list = self.create_nav_btn("Élèves", 1, load_icon("users"))
        self.btn_stats = self.create_nav_btn("Statistiques", 2, load_icon("chart"))
        self.btn_add = self.create_nav_btn("Ajouter", 3, load_icon("add"))
        self.btn_add_cours = self.create_nav_btn("Cours", 4, load_icon("course"))
        self.btn_add_examen = self.create_nav_btn("Examen", 5, load_icon("course"))
        self.btn_data = self.create_nav_btn("Données", 6, load_icon("add"))
        self.btn_cam.setChecked(True)

        sidebar_layout.addWidget(self.btn_cam)
        sidebar_layout.addWidget(self.btn_list)
        sidebar_layout.addWidget(self.btn_stats)
        sidebar_layout.addWidget(self.btn_add)
        sidebar_layout.addWidget(self.btn_add_cours)
        sidebar_layout.addWidget(self.btn_add_examen)
        sidebar_layout.addWidget(self.btn_data)
        sidebar_layout.addStretch()

        sidebar_divider = QFrame()
        sidebar_divider.setObjectName("SidebarDivider")
        sidebar_divider.setFrameShape(QFrame.Shape.HLine)
        sidebar_layout.addWidget(sidebar_divider)
        sidebar_layout.addSpacing(8)
        btn_back = QPushButton("Accueil")
        btn_back.setIcon(load_icon("home"))
        btn_back.setIconSize(QSize(19, 19))
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #718096;
                border: 1px solid transparent;
                padding: 11px 12px;
                border-radius: 10px;
                font-weight: 700;
                text-align: left;
            }
            QPushButton:hover {
                background: #eef4ff;
                color: #2459bd;
                border: 1px solid #d6e2f7;
            }
        """)
        btn_back.clicked.connect(self.handle_back_home)
        sidebar_layout.addWidget(btn_back)

        layout.addWidget(self.sidebar)

        # --- 2. ZONE CENTRALE ---
        self.stack = QStackedWidget()
        
        # Initialisation de la page d'attente (Index 0)
        self.setup_placeholder_page()
        
        # Autres pages
        self.stack.addWidget(ElevesView()) # Index 1
        self.stack.addWidget(StatsView())  # Index 2 (moved here)
        self.stack.addWidget(AjoutEleveView()) # Index 3
        self.stack.addWidget(AjoutCoursView()) # Index 4
        self.stack.addWidget(AjoutExamenView()) # Index 5
        self.stack.addWidget(GestionReferentielsView()) # Index 6

        self.stack.setStyleSheet("background: transparent;")
        layout.addWidget(self.stack, stretch=5)
    def load_cours(self):
        try:
            response = requests.get(
                f"{API_BASE_URL}/cours/all",
                timeout=API_TIMEOUT,
            )
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
            has_courses = bool(cours_list)
            self.cours_select.setVisible(has_courses)
            self.start_btn.setEnabled(has_courses)
        except Exception as e:
            print("Erreur chargement cours :", e)
            self.cours_select.setVisible(False)
            self.start_btn.setEnabled(False)
    def setup_placeholder_page(self):
        """Crée l'interface d'attente avec le bouton de démarrage"""
        self.cam_placeholder = QWidget()
        placeholder_layout = QVBoxLayout(self.cam_placeholder)
        placeholder_layout.setContentsMargins(4, 24, 24, 24)
        placeholder_layout.setSpacing(16)
        title = QLabel("<b style='color:#2f6fed; font-size:18px;'>POINTAGE : RECONNAISSANCE FACIALE</b>")
        placeholder_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignTop)

        # BUG-14 : cours_select créé et ajouté au layout AVANT insertWidget
        self.cours_select = QComboBox()
        self.cours_select.setFixedWidth(300)
        self.cours_select.setVisible(False)
        self.cours_select.setStyleSheet("""
            QComboBox {
                background: #edf4ff;
                border: 2px solid #3b6ee8;
                border-radius: 10px;
                padding: 10px 36px 10px 12px;
                color: #102a43;
                font-weight: 600;
            }
            QComboBox:hover {
                background: #e4f0ff;
                border: 2px solid #2957d6;
            }
            QComboBox::drop-down {
                border: none;
                background: transparent;
                width: 28px;
            }
            QComboBox::down-arrow {
                width: 0px;
                height: 0px;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid #1f4fc9;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background: #ffffff;
                color: #102a43;
                selection-background-color: #dfeaff;
                selection-color: #102a43;
                border: 1px solid #bfd0ff;
                border-radius: 8px;
            }
        """)

        self.start_btn = QPushButton("ACTIVER LE SCAN DE PRÉSENCE")
        self.start_btn.setIcon(load_icon("play"))
        self.start_btn.setFixedSize(300, 70)
        # Harmonize with global action button style (rounded, bold)
        self.start_btn.setStyleSheet(
            ACTION_BUTTON_STYLE +
            """
            QPushButton {
                background: #243447;
                color: #ffffff;
                font-size: 13px;
                border-radius: 12px;
                padding: 12px 16px;
            }
            QPushButton:hover { background: #1b2838; }
            """
        )
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
        container_layout.setContentsMargins(4, 24, 24, 24)
        container_layout.setSpacing(16)
        
        running_label = QLabel("SCAN EN COURS...")
        running_label.setStyleSheet("color:#17212b; font-size:18px; font-weight:700; letter-spacing: 1px;")
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
        self.stop_btn.setStyleSheet("background: #51606f; color: white; border-radius: 12px; padding: 12px 16px; font-weight: 700;")
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
        btn.setMinimumHeight(47)
        btn.setIcon(icon)
        btn.setIconSize(QSize(19, 19))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid transparent;
                color: #718096;
                font-size: 11px;
                font-weight: 700;
                padding: 10px 12px;
                border-radius: 10px;
                text-align: left;
            }
            QPushButton:hover:!checked {
                background: #f4f7ff;
                color: #17212b;
            }
            QPushButton:pressed { background: #dbe7ff; }
            QPushButton:checked {
                background: #e8f0ff;
                color: #2459bd;
                border: 1px solid #bdd0f7;
            }
            QPushButton:checked:hover {
                background: #dbe7ff;
                color: #204fa8;
            }
        """)
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(index))
        return btn
