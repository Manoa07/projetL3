from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

class CameraView(QFrame):
    def __init__(self, name, overlay_type):
        super().__init__()
        self.setStyleSheet("background-color: #1f2128; border: 2px solid #2d2f41; border-radius: 8px;")
        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        header.addWidget(QLabel(f"<b>{name}</b>"))
        presence = QLabel("PRÉSENTS: 24/25")
        presence.setStyleSheet("color: #2ecc71; font-weight: bold;")
        header.addStretch()
        header.addWidget(presence)
        layout.addLayout(header)
        center_label = QLabel("FLUX VIDÉO EN TEMPS RÉEL")
        center_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_label.setStyleSheet("color: #454859; font-size: 14px; border: none;")
        layout.addWidget(center_label)
        footer = QLabel(overlay_type)
        footer.setStyleSheet("color: #7a7c8c; font-size: 10px; border: none;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)