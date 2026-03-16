import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QGridLayout, QLabel, QFrame, 
                             QPushButton, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QPalette, QFont

class ClickableCard(QFrame):
    """Composant pour les alertes dans le fil d'actualité"""
    def __init__(self, title, time, status="warning"):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        color = "#e74c3c" if status == "critical" else "#f39c12"
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #252836;
                border-left: 5px solid {color};
                border-radius: 4px;
                margin-bottom: 8px;
                padding: 10px;
            }}
            QLabel {{ color: white; border: none; background: none; }}
        """)
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        icon_label = QLabel("⚠️")
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        time_label = QLabel(time)
        time_label.setStyleSheet("color: #7a7c8c; font-size: 11px;")
        
        layout.addLayout(header_layout)
        layout.addWidget(QLabel("Détection via YOLOv8 & MediaPipe"))
        layout.addWidget(time_label)

class CameraView(QFrame):
    """Composant pour l'affichage des flux de surveillance"""
    def __init__(self, name, quadrant_text="Quadrant 1"):
        super().__init__()
        self.setObjectName("CameraWidget")
        self.setStyleSheet("""
            #CameraWidget {
                background-color: #1f2128;
                border: 2px solid #2d2f41;
                border-radius: 5px;
            }
            QLabel { color: #4facfe; font-weight: bold; background: rgba(0,0,0,100); padding: 5px; }
        """)
        
        layout = QGridLayout(self)
        
        # Simulation des Overlays (Haut Gauche / Haut Droite)
        self.name_label = QLabel(name)
        self.presence_label = QLabel("PRÉSENTS: 24/25")
        self.presence_label.setStyleSheet("color: #2ecc71; background: rgba(0,0,0,150);")
        
        layout.addWidget(self.name_label, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.presence_label, 0, 1, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        # Zone centrale pour le futur flux OpenCV
        self.placeholder = QLabel("FLUX VIDÉO TEMPS RÉEL")
        self.placeholder.setStyleSheet("color: #454859; font-size: 18px; background: none;")
        layout.addWidget(self.placeholder, 1, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        
        # Label en bas pour le type d'overlay
        self.bottom_label = QLabel(quadrant_text)
        self.bottom_label.setStyleSheet("color: #7a7c8c; font-size: 10px; background: none;")
        layout.addWidget(self.bottom_label, 2, 0, 1, 2, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)

class ExamGuardInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ExamGuard AI - Système de Surveillance Intelligent")
        self.resize(1280, 800)
        self.init_ui()

    def init_ui(self):
        # Configuration de la couleur de fond principale (Dark Theme)
        self.setStyleSheet("background-color: #0f111a; color: #ffffff; font-family: 'Segoe UI', sans-serif;")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 1. SIDEBAR (Navigation) ---
        sidebar = QFrame()
        sidebar.setFixedWidth(100)
        sidebar.setStyleSheet("background-color: #1a1c2e; border-right: 1px solid #2d2f41;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        
        nav_items = [("📺", "Live"), ("📅", "Sessions"), ("👥", "Élèves"), ("⚙️", "Settings")]
        for icon, text in nav_items:
            btn = QPushButton(f"{icon}\n{text}")
            btn.setCheckable(True)
            btn.setFixedSize(100, 70)
            btn.setStyleSheet("""
                QPushButton { background: transparent; border: none; color: #7a7c8c; font-size: 11px; }
                QPushButton:checked { color: #4facfe; border-left: 3px solid #4facfe; background: #24273d; }
            """)
            sidebar_layout.addWidget(btn)
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # --- 2. CENTRE (Grille Vidéo) ---
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header Info (Basé sur vos fonctionnalités) [cite: 2, 3]
        header_label = QLabel("SESSION : SALLE A - EXAMEN ISAIA L3")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #4facfe;")
        center_layout.addWidget(header_label)
        
        # Grille de caméras
        video_grid = QGridLayout()
        video_grid.setSpacing(15)
        video_grid.addWidget(CameraView("CAMERA 1 - SALLE A", "Realtime Overlays"), 0, 0)
        video_grid.addWidget(CameraView("CAMERA 2 - SALLE A", "YOLOv8 Analysis"), 0, 1)
        video_grid.addWidget(CameraView("CAMERA 3 - COULOIR", "Posture Detection"), 1, 0)
        video_grid.addWidget(CameraView("CAMERA 4 - ENTRÉE", "Face Identification"), 1, 1)
        
        center_layout.addLayout(video_grid)
        main_layout.addWidget(center_container, stretch=5)

        # --- 3. DROITE (Fil d'Alertes et Stats) --- [cite: 4, 6, 12]
        right_panel = QFrame()
        right_panel.setFixedWidth(320)
        right_panel.setStyleSheet("background-color: #1a1c2e; border-left: 1px solid #2d2f41;")
        right_layout = QVBoxLayout(right_panel)
        
        # Section Alertes
        alert_title = QLabel("FIL D'ALERTES EN TEMPS RÉEL")
        alert_title.setStyleSheet("font-weight: bold; color: #7a7c8c; margin-bottom: 10px;")
        right_layout.addWidget(alert_title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Ajout manuel d'exemples d'alertes basés sur vos doc [cite: 33]
        scroll_layout.addWidget(ClickableCard("Objet Interdit: Smartphone", "10:42:15", "critical"))
        scroll_layout.addWidget(ClickableCard("Posture Suspecte", "10:41:02"))
        scroll_layout.addWidget(ClickableCard("Identification Inconnue", "10:38:45", "critical"))
        scroll_layout.addWidget(ClickableCard("Comportement: Fraude", "10:35:20"))
        
        scroll.setWidget(scroll_content)
        right_layout.addWidget(scroll)
        
        # Section Statistiques (Basé sur Fonctionnalités Optionnelles) 
        stats_box = QFrame()
        stats_box.setStyleSheet("background: #24273d; border-radius: 8px; padding: 10px;")
        stats_layout = QVBoxLayout(stats_box)
        stats_layout.addWidget(QLabel("STATISTIQUES SESSION"))
        stats_layout.addWidget(QLabel("Taux de présence : 96%"))
        stats_layout.addWidget(QLabel("Incidents détectés : 4"))
        right_layout.addWidget(stats_box)
        
        main_layout.addWidget(right_panel)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExamGuardInterface()
    window.showMaximized() # Pour un rendu plein écran comme sur la maquette
    sys.exit(app.exec())