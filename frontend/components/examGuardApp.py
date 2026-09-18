import sys
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap
from pathlib import Path

# Importation de vos nouveaux modules séparés
from components.icon_loader import load_icon
from components.theme import APP_STYLESHEET
from interface.surveillanceInterface import SurveillanceInterface
from interface.presenceInterface import PresenceInterface

class ExamGuardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Système de Surveillance Intelligent")
        self.resize(1280, 800)
        self.setStyleSheet(APP_STYLESHEET)
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
        """Crée l'accueil avec le logo et les deux modes de travail."""
        home_widget = QWidget()
        home_widget.setObjectName("HomePage")
        home_widget.setStyleSheet("""
            QWidget#HomePage {
                background: #f6f8fb;
            }
        """)
        layout = QVBoxLayout(home_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(16)

        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = Path(__file__).resolve().parents[2] / "image" / "logo.png"
        logo = QPixmap(str(logo_path))
        logo_label.setPixmap(logo.scaled(190, 190, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_label.setStyleSheet("background: transparent; padding: 4px;")
        layout.addWidget(logo_label)

        title = QLabel("SYSTÈME DE SURVEILLANCE INTELLIGENTE")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #17212b; font-size: 24px; font-weight: 800; letter-spacing: 1px;")
        layout.addWidget(title)

        subtitle = QLabel("Choisissez le mode de fonctionnement")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #718096; font-size: 13px; font-weight: 600;")
        layout.addWidget(subtitle)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        style = """
            QPushButton {
                background: #ffffff;
                border: 1px solid #e4e9ef;
                border-radius: 16px;
                color: #17212b;
                font-size: 16px;
                font-weight: 800;
                padding: 22px 24px;
                min-width: 190px;
                min-height: 76px;
            }
            QPushButton:hover {
                background: #eef1f5;
                border: 1px solid #243447;
                color: #243447;
            }
            QPushButton:pressed {
                background: #dfe5eb;
            }
        """
        btn_surv = QPushButton("SURVEILLANCE")
        btn_surv.setIcon(load_icon("live"))
        btn_surv.setIconSize(QSize(24, 24))
        btn_surv.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_surv.setStyleSheet(style)
        btn_surv.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        btn_pres = QPushButton("PRÉSENCE")
        btn_pres.setIcon(load_icon("users"))
        btn_pres.setIconSize(QSize(24, 24))
        btn_pres.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pres.setStyleSheet(style)
        btn_pres.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        btn_layout.addWidget(btn_surv)
        btn_layout.addWidget(btn_pres)
        layout.addLayout(btn_layout)

        footer = QLabel("S.S.I  •  PLATEFORME DE SUPERVISION EN TEMPS RÉEL")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #718096; font-size: 10px; font-weight: 700; letter-spacing: 1px;")
        layout.addSpacing(12)
        layout.addWidget(footer)

        return home_widget

    def return_to_home(self):
        """Fonction de rappel utilisée par les fichiers séparés"""
        self.stack.setCurrentIndex(0)

