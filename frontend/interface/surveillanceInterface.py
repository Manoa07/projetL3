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
        self.live_view = None 
        
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
        self.btn_live.setChecked(True)

        sidebar_layout.addWidget(self.btn_live)
        sidebar_layout.addWidget(self.btn_eleves)
        sidebar_layout.addWidget(self.btn_stats)
        sidebar_layout.addStretch()

        btn_back = QPushButton("🏠\nAccueil")
        btn_back.setStyleSheet("color: #e74c3c; border: none; padding: 15px; font-weight: bold;")
        btn_back.clicked.connect(self.back_to_home)
        sidebar_layout.addWidget(btn_back)

        layout.addWidget(self.sidebar)

        # --- B. ZONE CENTRALE (STACK) ---
        self.stack = QStackedWidget()
        self.setup_placeholder_page()
        self.stack.addWidget(ElevesView()) 
        self.stack.addWidget(StatsView())  
        
        layout.addWidget(self.stack)
        self.setup_alerts_panel(layout)

    def setup_placeholder_page(self):
        self.live_placeholder = QWidget()
        placeholder_layout = QVBoxLayout(self.live_placeholder)
        self.start_btn = QPushButton("🔴 LANCER LA SURVEILLANCE")
        self.start_btn.setFixedSize(280, 60)
        self.start_btn.setStyleSheet("background: #e74c3c; color: white; font-weight: bold; border-radius: 8px;")
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
            
            self.live_view = LiveView(self.add_new_alert)
            container_layout.addWidget(self.live_view)

            self.stop_btn = QPushButton("⏹ ARRÊTER LA SURVEILLANCE")
            self.stop_btn.setFixedWidth(250)
            self.stop_btn.setStyleSheet("background: #34495e; color: white; padding: 12px; border-radius: 5px;")
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
        self.alert_scroll_layout = QVBoxLayout(container)
        self.alert_scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(container)
        alerts_layout.addWidget(scroll)
        main_layout.addWidget(alerts_panel)

    def add_new_alert(self, message, time_str):
        if hasattr(self, 'alert_scroll_layout'):
            new_card = AlertCard(message, time_str, critical=True)
            self.alert_scroll_layout.insertWidget(0, new_card)