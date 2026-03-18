import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QFrame
from PyQt6.QtCore import Qt

# Importation de vos nouveaux modules séparés
from interface.surveillanceInterface import SurveillanceInterface
from interface.presenceInterface import PresenceInterface

class ExamGuardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Système de Surveillance Intelligent")
        self.resize(1280, 850)
        self.setStyleSheet("background-color: #0f111a; color: white; font-family: 'Segoe UI';")
        self.init_ui()

    def init_ui(self):
        # Layout principal : contiendra uniquement le StackedWidget
        self.central_layout = QVBoxLayout()
        self.central_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()

        # --- INDEX 0 : ACCUEIL ---
        self.stack.addWidget(self.create_home_menu())

        # --- INDEX 1 : SURVEILLANCE (Le fichier séparé) ---
        # On passe self.return_to_home pour que le bouton retour fonctionne
        self.surveillance_ui = SurveillanceInterface(self.return_to_home)
        self.stack.addWidget(self.surveillance_ui)

        # --- INDEX 2 : PRÉSENCE (Le fichier séparé) ---
        self.presence_ui = PresenceInterface(self.return_to_home)
        self.stack.addWidget(self.presence_ui)

        # Installation du Stack dans la fenêtre
        container = QWidget()
        container.setLayout(self.central_layout)
        self.central_layout.addWidget(self.stack)
        self.setCentralWidget(container)

    def create_home_menu(self):
        """Crée l'interface avec les 2 gros boutons"""
        home_widget = QWidget()
        layout = QVBoxLayout(home_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("GESTION DE L'INTERFACE")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #4facfe; margin-bottom: 40px;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()
        
        style = """
            QPushButton {
                background-color: #1a1c2e; border: 2px solid #2d2f41; border-radius: 20px;
                color: white; font-size: 20px; font-weight: bold; padding: 60px; min-width: 250px;
            }
            QPushButton:hover { background-color: #24273d; border-color: #4facfe; }
        """

        btn_surv = QPushButton("🛡️ SURVEILLANCE")
        btn_surv.setStyleSheet(style)
        btn_surv.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        btn_pres = QPushButton("👥 PRÉSENCE")
        btn_pres.setStyleSheet(style)
        btn_pres.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        btn_layout.addWidget(btn_surv)
        btn_layout.addSpacing(40)
        btn_layout.addWidget(btn_pres)
        
        layout.addLayout(btn_layout)
        return home_widget

    def return_to_home(self):
        """Fonction de rappel utilisée par les fichiers séparés"""
        self.stack.setCurrentIndex(0)