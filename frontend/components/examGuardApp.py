import sys
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
<<<<<<< Updated upstream
from PyQt6.QtCore import Qt, QSize
=======
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QGraphicsOpacityEffect
>>>>>>> Stashed changes

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
        self.stack.currentChanged.connect(self.animate_current_page)

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
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(22)
<<<<<<< Updated upstream
=======
        
        pixmap = QPixmap("../image/logo_ispm.png")

        logo_label = QLabel()
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("background-color: transparent;")
        layout.addWidget(logo_label)
>>>>>>> Stashed changes

        title = QLabel("GESTION DE L'INTERFACE")
        title.setStyleSheet("font-size: 30px; font-weight: 800; color: #17212b; letter-spacing: 1.6px;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        style = """
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #e1e7ed;
                border-radius: 24px;
                color: #17212b;
                font-size: 17px;
                font-weight: 700;
                padding: 40px 34px;
                min-width: 250px;
                min-height: 170px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #fff2ee;
                border-color: #2e9d68;
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
        return home_widget

    def return_to_home(self):
        """Fonction de rappel utilisée par les fichiers séparés"""
        self.stack.setCurrentIndex(0)

    def animate_current_page(self, index):
        page = self.stack.widget(index)
        if page is None:
            return
        effect = QGraphicsOpacityEffect(page)
        page.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity", page)
        animation.setDuration(280)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        page._page_animation = animation
        animation.start()
