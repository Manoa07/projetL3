from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage

class CameraView(QFrame):
    def __init__(self, name, overlay_type):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e4e9ef;
                border-radius: 18px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        
        # Header
        header = QHBoxLayout()
        title = QLabel(f"<b style='color:#17212b; font-size:13px; letter-spacing: 1px;'>{name}</b>")
        header.addWidget(title)
        self.presence = QLabel("Présence : --/--")
        self.presence.setStyleSheet("color: #243447; font-weight: 700;")
        header.addStretch()
        header.addWidget(self.presence)
        layout.addLayout(header)

        # Zone d'affichage du flux
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setFixedHeight(250)
        self.video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.video_label.setText("FLUX EN ATTENTE")
        self.video_label.setStyleSheet("color: #586078; border: none; padding: 12px;")
        layout.addWidget(self.video_label)

        footer = QLabel(overlay_type)
        footer.setStyleSheet("color: #718096; font-size: 10px; border: none; letter-spacing: 0.5px;")
        layout.addWidget(footer, alignment=Qt.AlignmentFlag.AlignCenter)

    def update_frame(self, qt_image):
        """Reçoit l'image du Thread et l'affiche"""
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap.scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))

    def clear_view(self):
        """Nettoie l'écran lors de l'arrêt"""
        self.video_label.clear()
        self.video_label.setText("FLUX STOP")
