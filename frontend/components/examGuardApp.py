import sys
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QSize
from PyQt6.QtGui import QPixmap

# Importation de vos nouveaux modules séparés
from components.icon_loader import load_icon
from components.theme import APP_STYLESHEET
from interface.surveillanceInterface import SurveillanceInterface
from interface.presenceInterface import PresenceInterface

class ExamGuardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Système de Surveillance Intelligent")
        self.resize(1280, 850)
        self.setStyleSheet(APP_STYLESHEET)
        self.init_ui()

    def init_ui(self):
        # Layout principal : contiendra uniquement le StackedWidget
        self.central_layout = QVBoxLayout()
        self.central_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.stack.currentChanged.connect(self.animate_page)

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
        """Crée l'accueil principal avec deux parcours clairement identifiés."""
        home_widget = QWidget()
        home_widget.setObjectName("HomePage")
        home_widget.setStyleSheet("QWidget#HomePage { background: #f5f7fb; }")
        layout = QVBoxLayout(home_widget)
        layout.setContentsMargins(72, 54, 72, 54)
        layout.setSpacing(18)

        header = QHBoxLayout()
        brand = QLabel("EXAMGUARD")
        brand.setStyleSheet("color: #1769d2; font-size: 16px; font-weight: 800; letter-spacing: 2px;")
        status = QLabel("●  SYSTÈME PRÊT")
        status.setStyleSheet("color: #15956d; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        header.addWidget(brand)
        header.addStretch()
        header.addWidget(status)
        layout.addLayout(header)

        pixmap = QPixmap("../image/logo_ispm.png")

        logo_label = QLabel()
        logo_label.setPixmap(pixmap.scaled(132, 132, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("background-color: #ffffff; border-radius: 66px; padding: 18px;")
        logo_shadow = QGraphicsDropShadowEffect(self)
        logo_shadow.setBlurRadius(28)
        logo_shadow.setOffset(0, 8)
        logo_shadow.setColor(Qt.GlobalColor.lightGray)
        logo_label.setGraphicsEffect(logo_shadow)
        layout.addWidget(logo_label)

        eyebrow = QLabel("PLATEFORME DE SURVEILLANCE ACADÉMIQUE")
        eyebrow.setStyleSheet("color: #718096; font-size: 11px; font-weight: 700; letter-spacing: 1.6px;")
        layout.addWidget(eyebrow, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Pilotez vos examens avec précision")
        title.setStyleSheet("font-size: 30px; font-weight: 800; color: #172033; letter-spacing: 0px;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        subtitle = QLabel("Choisissez votre espace de travail pour commencer.")
        subtitle.setStyleSheet("color: #718096; font-size: 14px;")
        layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(18)
        btn_layout.setContentsMargins(30, 18, 30, 18)

        style = """
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #e1e8f2;
                border-radius: 16px;
                color: #172033;
                font-size: 14px;
                font-weight: 700;
                padding: 22px 24px;
                min-width: 220px;
                min-height: 116px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #f8fbff;
                border-color: #81b6f7;
                color: #1769d2;
            }
            QPushButton:pressed {
                background-color: #edf5ff;
            }
        """
        btn_surv = QPushButton("SURVEILLANCE")
        btn_surv.setIcon(load_icon("live"))
        btn_surv.setIconSize(QSize(24, 24))
        btn_surv.setStyleSheet(style)
        btn_surv.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        btn_pres = QPushButton("PRÉSENCE")
        btn_pres.setIcon(load_icon("users"))
        btn_pres.setIconSize(QSize(24, 24))
        btn_pres.setStyleSheet(style)
        btn_pres.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        btn_layout.addWidget(btn_surv)
        btn_layout.addWidget(btn_pres)
        
        layout.addLayout(btn_layout)
        footer = QLabel("ISPM  •  Centre de contrôle intelligent")
        footer.setStyleSheet("color: #a0aabd; font-size: 10px; letter-spacing: 0.6px;")
        layout.addWidget(footer, alignment=Qt.AlignmentFlag.AlignCenter)
        return home_widget

    def animate_page(self, index):
        """Anime discrètement l'apparition de chaque vue du stack."""
        widget = self.stack.widget(index)
        if widget is None:
            return
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(260)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.finished.connect(lambda: widget.setGraphicsEffect(None))
        self.page_animation = animation
        animation.start()

    def return_to_home(self):
        """Fonction de rappel utilisée par les fichiers séparés"""
        self.stack.setCurrentIndex(0)
