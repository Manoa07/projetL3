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
from PyQt6.QtGui import QPixmap
from pathlib import Path
from components.icon_loader import load_icon
from components.theme import NAV_BUTTON_STYLE
from views.liveView import LiveView
from views.elevesView import ElevesView
# Stats removed from Surveillance interface (moved to Presence)
from components.alertCard import AlertCard 

class SurveillanceInterface(QWidget):
    def __init__(self, back_to_home_callback):
        super().__init__()
        self.last_alert_time = 0
        self.alert_cooldown = 5
        self.back_to_home = back_to_home_callback
        self.live_view = None
        self.sidebar_width = 214
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- A. BARRE LATÉRALE ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(self.sidebar_width)
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
        sidebar_layout.setSpacing(7)

        brand = QLabel()
        brand.setObjectName("SidebarBrand")
        logo_path = Path(__file__).resolve().parents[2] / "image" / "logo_ispm.png"
        logo = QPixmap(str(logo_path))
        brand.setPixmap(logo.scaled(174, 74, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        brand.setFixedHeight(74)
        brand.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.sidebar_brand = brand
        sidebar_layout.addWidget(brand)

        subtitle = QLabel("SURVEILLANCE INTELLIGENTE")
        subtitle.setObjectName("SidebarSubtitle")
        self.sidebar_subtitle = subtitle
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addSpacing(18)

        navigation_label = QLabel("NAVIGATION")
        navigation_label.setObjectName("SidebarSection")
        self.navigation_label = navigation_label
        sidebar_layout.addWidget(navigation_label)
        sidebar_layout.addSpacing(4)

        self.btn_live = self.create_nav_btn("Direct", 0, load_icon("live"))
        self.btn_eleves = self.create_nav_btn("Élèves", 1, load_icon("users"))
        self.btn_live.setChecked(True)

        sidebar_layout.addWidget(self.btn_live)
        sidebar_layout.addWidget(self.btn_eleves)
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
                padding: 11px 12px;
                border-radius: 10px;
                font-weight: 700;
                text-align: left;
            }
            QPushButton:hover { background: #eef4ff; color: #2459bd; }
        """)
        btn_back.clicked.connect(self.back_to_home)
        self.btn_back = btn_back
        sidebar_layout.addWidget(btn_back)

        layout.addWidget(self.sidebar)

        # --- B. ZONE CENTRALE (STACK) ---
        self.stack = QStackedWidget()
        self.setup_placeholder_page()
        self.stack.addWidget(ElevesView())
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
        self.start_btn.setStyleSheet("background: #2f6fed; color: white; font-weight: 700; border-radius: 12px; padding: 12px 16px;")
        self.start_btn.clicked.connect(self.start_live_monitoring)
        placeholder_layout.addStretch()
        placeholder_layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.addStretch()
        self.stack.insertWidget(0, self.live_placeholder)

    def start_live_monitoring(self):
        if self.live_view is None:
            self._set_compact_navigation(True)
            self.live_view = LiveView(self.add_new_alert)
            self.live_container = QWidget()
            container_layout = QVBoxLayout(self.live_container)
            container_layout.setContentsMargins(10, 10, 10, 10)
            container_layout.setSpacing(8)
            container_layout.addWidget(self.live_view, 1)

            self.stop_btn = QPushButton("ARRÊTER LA SURVEILLANCE")
            self.stop_btn.setIcon(load_icon("stop"))
            self.stop_btn.setFixedWidth(250)
            self.stop_btn.setStyleSheet("background: #51606f; color: white; padding: 12px 16px; border-radius: 12px;")
            self.stop_btn.clicked.connect(self.stop_live_monitoring)
            container_layout.addWidget(self.stop_btn, 0, alignment=Qt.AlignmentFlag.AlignCenter)

            self.stack.removeWidget(self.live_placeholder)
            self.stack.insertWidget(0, self.live_container)
            self.stack.setCurrentIndex(0)

    def stop_live_monitoring(self):
        """Arrêt propre : Thread -> Widget -> UI"""
        if self.live_view is not None:
            try:
                self.live_view.stop_camera()
            except Exception as e:
                print("[SurveillanceInterface] Erreur lors de l'arrêt de la caméra :", e)
            self.live_view = None

        if hasattr(self, "live_container"):
            self.stack.removeWidget(self.live_container)
            self.live_container.deleteLater()
            self.live_container = None
        self._set_compact_navigation(False)
        self.setup_placeholder_page()
        self.stack.setCurrentIndex(0)

    def _set_compact_navigation(self, compact):
        self.sidebar.setFixedWidth(68 if compact else self.sidebar_width)
        self.sidebar_brand.setVisible(not compact)
        self.sidebar_subtitle.setVisible(not compact)
        self.navigation_label.setVisible(not compact)
        labels = {
            self.btn_live: "Surveillance en direct",
            self.btn_eleves: "Élèves",
        }
        for button, tooltip in labels.items():
            button.setText("" if compact else tooltip)
            button.setToolTip(tooltip)
            button.setMinimumHeight(42 if compact else 47)
        self.btn_back.setText("" if compact else "Accueil")
        self.btn_back.setToolTip("Accueil")


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

    def setup_alerts_panel(self, main_layout):
        alerts_panel = QFrame()
        alerts_panel.setObjectName("AlertsPanel")
        alerts_panel.setFixedWidth(280)
        alerts_panel.setStyleSheet("""
            QFrame#AlertsPanel {
                background-color: #ffffff;
                border-left: 1px solid #e4e9ef;
            }
        """)
        alerts_layout = QVBoxLayout(alerts_panel)
        alerts_layout.setContentsMargins(12, 12, 12, 12)
        alerts_layout.setSpacing(8)
        header = QHBoxLayout()
        title = QLabel("<b>ALERTES EN DIRECT</b>")
        title.setStyleSheet("color: #17212b; font-size: 12px; letter-spacing: 0.8px;")
        header.addWidget(title)
        self.alert_count = QLabel("0")
        self.alert_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.alert_count.setFixedSize(26, 24)
        self.alert_count.setStyleSheet("background: #e74c3c; color: white; border-radius: 12px; font-weight: 800;")
        header.addWidget(self.alert_count)
        alerts_layout.addLayout(header)
        subtitle = QLabel("Événements nécessitant votre attention")
        subtitle.setStyleSheet("color: #718096; font-size: 10px;")
        alerts_layout.addWidget(subtitle)
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
            self.alert_count.setText(str(self.alert_scroll_layout.count()))
