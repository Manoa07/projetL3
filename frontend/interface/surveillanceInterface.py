from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
                             QStackedWidget, QFrame, QLabel, QScrollArea)
from PyQt6.QtCore import Qt
from views.liveView import LiveView
from views.elevesView import ElevesView
from views.statsView import StatsView
from components.alertCard import AlertCard 

class SurveillanceInterface(QWidget):
    def __init__(self, back_to_home_callback):
        super().__init__()
        self.back_to_home = back_to_home_callback
        
        # Layout Principal Horizontal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- A. BARRE LATÉRALE ---
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(100)
        self.sidebar.setStyleSheet("background-color: #1a1c2e; border-right: 1px solid #2d2f41;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        btn_style = """
            QPushButton { background: transparent; border: none; color: #7a7c8c; font-size: 11px; padding: 10px; }
            QPushButton:checked { background: #24273d; color: #4facfe; border-left: 3px solid #4facfe; }
        """

        self.btn_live = self.create_nav_btn("📺\nLive", btn_style, 0)
        self.btn_eleves = self.create_nav_btn("👥\nÉlèves", btn_style, 1)
        self.btn_stats = self.create_nav_btn("📊\nStats", btn_style, 2)
        
        sidebar_layout.addWidget(self.btn_live)
        sidebar_layout.addWidget(self.btn_eleves)
        sidebar_layout.addWidget(self.btn_stats)
        sidebar_layout.addStretch()

        # Bouton Retour Accueil
        btn_back = QPushButton("🏠\nAccueil")
        btn_back.setStyleSheet("color: #e74c3c; border: none; padding: 15px; font-weight: bold;")
        btn_back.clicked.connect(self.back_to_home)
        sidebar_layout.addWidget(btn_back)

        layout.addWidget(self.sidebar)

        # --- B. ZONE CENTRALE (STACK) ---
        self.stack = QStackedWidget()
        self.stack.addWidget(LiveView())   # Index 0
        self.stack.addWidget(ElevesView()) # Index 1
        self.stack.addWidget(StatsView())  # Index 2
        layout.addWidget(self.stack, stretch=5)

        # --- C. PANNEAU D'ALERTES (À DROITE) ---
        self.setup_alerts_panel(layout)

        # Activer le premier bouton par défaut
        self.btn_live.setChecked(True)

    def create_nav_btn(self, text, style, index):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setFixedSize(100, 80)
        btn.setStyleSheet(style)
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(index))
        return btn

    def setup_alerts_panel(self, layout):
        alerts_panel = QFrame()
        alerts_panel.setFixedWidth(280)
        alerts_panel.setStyleSheet("background-color: #1a1c2e; border-left: 1px solid #2d2f41;")
        alerts_layout = QVBoxLayout(alerts_panel)
        
        title = QLabel("<b>FIL D'ALERTES</b>")
        title.setStyleSheet("color: #4facfe; margin-bottom: 10px;")
        alerts_layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Ajout de quelques alertes exemples
        scroll_layout.addWidget(AlertCard("Smartphone détecté", "14:05", True))
        scroll_layout.addWidget(AlertCard("Posture suspecte", "14:02", False))
        scroll_layout.addWidget(AlertCard("Élève non reconnu", "13:58", True))
        
        scroll.setWidget(container)
        alerts_layout.addWidget(scroll)
        layout.addWidget(alerts_panel)