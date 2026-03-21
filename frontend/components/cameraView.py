from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage

class CameraView(QFrame):
    def __init__(self, name, overlay_type):
        super().__init__()
        self.setStyleSheet("background-color: #000000; border: 2px solid #2d2f41; border-radius: 8px;")
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel(f"<b style='color:white;'>{name}</b>"))
        self.presence = QLabel("PRÉSENTS: --/--")
        self.presence.setStyleSheet("color: #2ecc71; font-weight: bold;")
        header.addStretch()
        header.addWidget(self.presence)
        layout.addLayout(header)

        # Zone d'affichage du flux
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setText("INITIALISATION DU FLUX...")
        self.video_label.setStyleSheet("color: #454859; border: none;")
        layout.addWidget(self.video_label)

        footer = QLabel(overlay_type)
        footer.setStyleSheet("color: #7a7c8c; font-size: 10px; border: none;")
        layout.addWidget(footer, alignment=Qt.AlignmentFlag.AlignCenter)

    def update_frame(self, qt_image):
        """Reçoit l'image du Thread et l'affiche"""
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def clear_view(self):
        """Nettoie l'écran lors de l'arrêt"""
        self.video_label.clear()
        self.video_label.setText("FLUX ARRÊTÉ")