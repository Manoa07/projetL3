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
        
        btn_back = QPushButton("⬅️\nRetour")
        btn_back.setStyleSheet(btn_style)
        btn_back.clicked.connect(self.back_to_home)

        sidebar_layout.addWidget(self.btn_live)
        sidebar_layout.addWidget(self.btn_eleves)
        sidebar_layout.addWidget(self.btn_stats)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(btn_back)

        layout.addWidget(self.sidebar)

        # --- B. ZONE CENTRALE (STACK) ---
        self.stack = QStackedWidget()
        
        # 1. On initialise d'abord le panneau d'alertes pour créer 'self.alert_scroll_layout'
        self.setup_alerts_panel(layout)

        # 2. Maintenant on peut créer LiveView en lui passant la méthode add_new_alert
        self.live_view = LiveView(self.add_new_alert)
        
        self.stack.addWidget(self.live_view)
        self.stack.addWidget(ElevesView())
        self.stack.addWidget(StatsView())
        
        # On insère le stack au milieu (index 1 du layout horizontal)
        layout.insertWidget(1, self.stack)

        self.btn_live.setChecked(True)

    def create_nav_btn(self, text, style, index):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setFixedSize(100, 80)
        btn.setStyleSheet(style)
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(index))
        return btn

    def setup_alerts_panel(self, main_layout):
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
        container.setStyleSheet("background: transparent;")
        self.alert_scroll_layout = QVBoxLayout(container)
        self.alert_scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.alert_scroll_layout.setSpacing(10)
        
        scroll.setWidget(container)
        alerts_layout.addWidget(scroll)
        
        # On ajoute le panneau au layout principal
        main_layout.addWidget(alerts_panel)

    def add_new_alert(self, message, time_str):
        """Méthode appelée dynamiquement par le flux vidéo"""
        if hasattr(self, 'alert_scroll_layout'):
            new_card = AlertCard(message, time_str, critical=True)
            # Ajoute l'alerte tout en haut de la liste
            self.alert_scroll_layout.insertWidget(0, new_card)