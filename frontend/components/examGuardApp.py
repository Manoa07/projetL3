import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QStackedWidget, 
                             QScrollArea, QLabel, QFrame)
from PyQt6.QtCore import Qt

# Importation des composants et des vues (vos nouveaux fichiers)
from components.alertCard import AlertCard
from views.liveView import LiveView
from views.elevesView import ElevesView
from views.statsView import StatsView

class ExamGuardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ExamGuard AI - Dashboard")
        self.resize(1280, 850)
        self.setStyleSheet("background-color: #0f111a; color: white; font-family: 'Segoe UI';")
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. BARRE LATÉRALE (Navigation)
        sidebar = QFrame()
        sidebar.setFixedWidth(100)
        sidebar.setStyleSheet("background-color: #1a1c2e; border-right: 1px solid #2d2f41;")
        sidebar_layout = QVBoxLayout(sidebar)
        
        btn_style = """
            QPushButton { background: transparent; border: none; color: #7a7c8c; font-size: 11px; padding: 10px; }
            QPushButton:checked { background: #24273d; color: #4facfe; border-left: 3px solid #4facfe; }
        """

        # Boutons de navigation
        self.btn_live = self.create_nav_btn("📺\nLive", btn_style, 1)
        self.btn_eleves = self.create_nav_btn("👥\nÉlèves", btn_style, 2)
        self.btn_stats = self.create_nav_btn("📊\nPrésence", btn_style, 3)
        
        sidebar_layout.addWidget(self.btn_live)
        sidebar_layout.addWidget(self.btn_eleves)
        sidebar_layout.addWidget(self.btn_stats)
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # 2. ZONE CENTRALE (Conteneur des vues)
        self.stack = QStackedWidget()
        
        # Ajout des pages depuis les fichiers du dossier views/
        self.stack.addWidget(QLabel("Veuillez sélectionner une section")) # Index 0
        self.stack.addWidget(LiveView())   # Index 1 (depuis liveView.py) [cite: 4, 6]
        self.stack.addWidget(ElevesView()) # Index 2 (depuis elevesView.py) [cite: 5, 26, 27, 28, 29]
        self.stack.addWidget(StatsView())  # Index 3 (depuis statsView.py) [cite: 8, 14, 35]
        
        main_layout.addWidget(self.stack, stretch=5)

        # 3. PANNEAU D'ALERTES (Toujours visible à droite)
        self.setup_alerts_panel(main_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def create_nav_btn(self, text, style, index):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setFixedSize(100, 80)
        btn.setStyleSheet(style)
        btn.clicked.connect(lambda: self.switch_page(index))
        return btn

    def setup_alerts_panel(self, layout):
        alerts_panel = QFrame()
        alerts_panel.setFixedWidth(280)
        alerts_panel.setStyleSheet("background-color: #1a1c2e; border-left: 1px solid #2d2f41;")
        alerts_layout = QVBoxLayout(alerts_panel)
        alerts_layout.addWidget(QLabel("<b>FIL D'ALERTES</b>"))
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Alertes par défaut (peuvent être liées au backend plus tard) [cite: 33]
        scroll_layout.addWidget(AlertCard("Smartphone détecté", "14:05", True))
        scroll_layout.addWidget(AlertCard("Posture suspecte", "14:02"))
        
        scroll.setWidget(container)
        alerts_layout.addWidget(scroll)
        layout.addWidget(alerts_panel)

    def switch_page(self, index):
        """Gère l'affichage de la vue sélectionnée"""
        self.btn_live.setChecked(index == 1)
        self.btn_eleves.setChecked(index == 2)
        self.btn_stats.setChecked(index == 3)
        self.stack.setCurrentIndex(index)