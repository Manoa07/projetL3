import time

from PyQt6.QtWidgets import (
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
from components.icon_loader import load_icon
from components.theme import NAV_BUTTON_STYLE
from views.liveView import LiveView
from views.elevesView import ElevesView
from views.statsView import StatsView
from components.alertCard import AlertCard 

class SurveillanceInterface(QWidget):
    def __init__(self, back_to_home_callback):
        # Correction : super().__init__() doit être appelé en premier pour que
        # l'objet Qt C++ soit initialisé avant toute affectation d'attributs.
        super().__init__()
        self.last_alert_time = 0
        self.alert_cooldown = 5
        self.back_to_home = back_to_home_callback
        self.live_view = None 
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- A. BARRE LATÉRALE ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(108)
        self.sidebar.setStyleSheet("""
            QFrame#Sidebar {
                background-color: #151826;
                border-right: 1px solid #24273d;
            }
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 12, 10, 12)
        sidebar_layout.setSpacing(8)

        self.btn_live = self.create_nav_btn("Live", 0, load_icon("live"))
        self.btn_eleves = self.create_nav_btn("Élèves", 1, load_icon("users"))
        self.btn_stats = self.create_nav_btn("Stats", 2, load_icon("chart"))
        self.btn_live.setChecked(True)

        sidebar_layout.addWidget(self.btn_live)
        sidebar_layout.addWidget(self.btn_eleves)
        sidebar_layout.addWidget(self.btn_stats)
        sidebar_layout.addStretch()

        btn_back = QPushButton("Accueil")
        btn_back.setIcon(load_icon("home"))
        btn_back.setStyleSheet("color: #e74c3c; padding: 14px; font-weight: 700; border-radius: 12px;")
        btn_back.clicked.connect(self.back_to_home)
        sidebar_layout.addWidget(btn_back)

        layout.addWidget(self.sidebar)

        # --- B. ZONE CENTRALE (STACK) ---
        self.stack = QStackedWidget()
        self.setup_placeholder_page()
        self.stack.addWidget(ElevesView()) 
        self.stack.addWidget(StatsView())  
        self.stack.setStyleSheet("background: transparent;")
        layout.addWidget(self.stack)
        self.setup_alerts_panel(layout)

    def setup_placeholder_page(self):
        self.live_placeholder = QWidget()
        placeholder_layout = QVBoxLayout(self.live_placeholder)
        placeholder_layout.setContentsMargins(24, 24, 24, 24)
        placeholder_layout.setSpacing(16)
        self.start_btn = QPushButton("LANCER LA SURVEILLANCE")
        self.start_btn.setIcon(load_icon("play"))
        self.start_btn.setFixedSize(280, 60)
        self.start_btn.setStyleSheet("background: #e74c3c; color: white; font-weight: 700; border-radius: 12px; padding: 12px 16px;")
        self.start_btn.clicked.connect(self.start_live_monitoring)
        placeholder_layout.addStretch()
        placeholder_layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.addStretch()
        self.stack.insertWidget(0, self.live_placeholder)

    def start_live_monitoring(self):
        if self.live_view is None:
            self.live_scroll = QScrollArea()
            self.live_scroll.setWidgetResizable(True)
            self.live_scroll.setStyleSheet("background: transparent; border: none;")
            
            self.live_container = QWidget()
            container_layout = QVBoxLayout(self.live_container)
            container_layout.setContentsMargins(24, 24, 24, 24)
            container_layout.setSpacing(16)
            
            self.live_view = LiveView(self.add_new_alert)
            container_layout.addWidget(self.live_view)

            self.stop_btn = QPushButton("ARRÊTER LA SURVEILLANCE")
            self.stop_btn.setIcon(load_icon("stop"))
            self.stop_btn.setFixedWidth(250)
            self.stop_btn.setStyleSheet("background: #34495e; color: white; padding: 12px 16px; border-radius: 12px;")
            self.stop_btn.clicked.connect(self.stop_live_monitoring)
            container_layout.addWidget(self.stop_btn, alignment=Qt.AlignmentFlag.AlignCenter)
            container_layout.addStretch()

            self.live_scroll.setWidget(self.live_container)
            self.stack.removeWidget(self.live_placeholder)
            self.stack.insertWidget(0, self.live_scroll)
            self.stack.setCurrentIndex(0)

    def stop_live_monitoring(self):
        """Arrêt propre : Thread -> Widget -> UI"""
        if self.live_view:
            self.live_view.stop_camera() # Éteint la LED
            self.stack.removeWidget(self.live_scroll)
            self.live_scroll.deleteLater()
            self.live_view = None
            self.setup_placeholder_page()
            self.stack.setCurrentIndex(0)

    def create_nav_btn(self, text, index, icon):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setFixedSize(100, 86)
        btn.setIcon(icon)
        btn.setIconSize(QSize(24, 24))
        btn.setStyleSheet(NAV_BUTTON_STYLE)
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(index))
        return btn

    def setup_alerts_panel(self, main_layout):
        alerts_panel = QFrame()
        alerts_panel.setObjectName("AlertsPanel")
        alerts_panel.setFixedWidth(300)
        alerts_panel.setStyleSheet("""
            QFrame#AlertsPanel {
                background-color: #151826;
                border-left: 1px solid #24273d;
            }
        """)
        alerts_layout = QVBoxLayout(alerts_panel)
        alerts_layout.setContentsMargins(14, 16, 14, 14)
        alerts_layout.setSpacing(12)
        title = QLabel("<b>FIL D'ALERTES</b>")
        title.setStyleSheet("color: #f4f7fb; margin-bottom: 8px; font-size: 13px; letter-spacing: 1px;")
        alerts_layout.addWidget(title)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        container = QWidget()
        self.alert_scroll_layout = QVBoxLayout(container)
        self.alert_scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.alert_scroll_layout.setSpacing(8)
        scroll.setWidget(container)
        alerts_layout.addWidget(scroll)
        main_layout.addWidget(alerts_panel)

    def add_new_alert(self, message, time_str):
        current_time=time.time()
        if current_time-self.last_alert_time < self.alert_cooldown:
            return
        self.last_alert_time= current_time
        
        if hasattr(self, 'alert_scroll_layout'):
            new_card = AlertCard(message, time_str, critical=True)
            self.alert_scroll_layout.insertWidget(0, new_card)
