from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFileDialog, QFrame,
                             QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
import cv2
from services.events import global_signals
import httpx
from config import API_BASE_URL
import asyncio
from components.icon_loader import load_icon


class CaptureThread(QThread):
    """BUG-06 : capture de 10 photos dans un thread séparé pour ne pas bloquer l'UI."""
    frame_signal = pyqtSignal(object)   # frame courante pour preview éventuelle
    done_signal  = pyqtSignal(list)     # liste des frames capturées
    error_signal = pyqtSignal(str)

    def __init__(self, nb_images=10):
        super().__init__()
        self.nb_images = nb_images
        self._run_flag = True

    def run(self):
        captured = []
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.error_signal.emit("Impossible d'ouvrir la caméra.")
            return
        try:
            while self._run_flag and len(captured) < self.nb_images:
                ret, frame = cap.read()
                if not ret:
                    break
                self.frame_signal.emit(frame.copy())
                # capture automatique toutes les ~0.5 s (pas besoin de touche espace)
                import time
                time.sleep(0.5)
                captured.append(frame.copy())
        finally:
            cap.release()
        self.done_signal.emit(captured)

    def stop(self):
        self._run_flag = False
        self.wait()


class AjoutEleveView(QWidget):
    def __init__(self):
        super().__init__()
        self.photo_path = None
        self.captured_images = []
        self._capture_thread = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")

        container = QWidget()
        container.setObjectName("AjoutEleveContainer")
        container.setStyleSheet("QWidget#AjoutEleveContainer { background-color: #0f111a; }")
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        title = QLabel("<b style='color:#f4f7fb; font-size:20px; letter-spacing: 1.4px;'>AJOUT ÉLÈVE</b>")
        title.setStyleSheet("background: transparent;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        form_frame = QFrame()
        form_frame.setObjectName("Card")
        form_frame.setStyleSheet("""
            QFrame#Card {
                background-color: #151826;
                border: 1px solid #23283d;
                border-radius: 16px;
            }
            QFrame#Card QLabel {
                background: transparent;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(22, 22, 22, 22)
        form_layout.setSpacing(12)

        self.nom    = self.create_input(form_layout, "Nom :")
        self.prenom = self.create_input(form_layout, "Prénom :")
        self.classe = self.create_input(form_layout, "Classe :")
        self.numero = self.create_input(form_layout, "Numéro d'inscription :")

        # --- SECTION PHOTO ---
        form_layout.addSpacing(10)
        photo_title = QLabel("Photo")
        photo_title.setStyleSheet("background: transparent; color: #f4f7fb; font-weight: 700;")
        form_layout.addWidget(photo_title)

        photo_section = QHBoxLayout()
        self.photo_label = QLabel("Format\nPortrait")
        self.photo_label.setFixedSize(150, 200)
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 1px dashed #335a7f;
                border-radius: 12px;
                background-color: #121524;
                color: #586078;
            }
        """)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_photo = QPushButton("Charger")
        self.btn_photo.setIcon(load_icon("course"))
        self.btn_photo.setMinimumSize(220, 50)
        self.btn_photo.setStyleSheet("""
            QPushButton {
                background-color: #20243a;
                color: #ffffff;
                border-radius: 12px;
                font-weight: 700;
                font-size: 13px;
                padding: 10px 14px;
            }
            QPushButton:hover { background-color: #2a304b; }
        """)
        self.btn_photo.clicked.connect(self.upload_photo)

        photo_section.addWidget(self.photo_label)
        photo_section.addSpacing(20)
        photo_section.addWidget(self.btn_photo)
        photo_section.addStretch()
        form_layout.addLayout(photo_section)

        # Bouton capture (BUG-06 : lance CaptureThread, ne bloque plus l'UI)
        self.btn_capture = QPushButton("Capturer 10 photos (auto)")
        self.btn_capture.setStyleSheet("""
            QPushButton {
                background-color: #4facfe;
                color: white;
                padding: 12px;
                border-radius: 12px;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #37b8ff; }
            QPushButton:disabled { background-color: #2a4060; color: #7a8a9a; }
        """)
        # Correction : on ne bloque plus le thread Qt.
        # start_capture lance un CaptureThread en arrière-plan.
        self.btn_capture.clicked.connect(self.start_capture)
        form_layout.addWidget(self.btn_capture)

        self.capture_status = QLabel("")
        self.capture_status.setStyleSheet("background: transparent; color: #8b93a7; font-style: italic;")
        form_layout.addWidget(self.capture_status)

        self.btn_submit = QPushButton("ENREGISTRER L'ÉLÈVE")
        self.btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_submit.setStyleSheet("""
            QPushButton { background-color: #2ecc71; color: white; font-weight: 700;
                          padding: 18px; margin-top: 24px; border-radius: 12px; font-size: 14px; }
            QPushButton:hover { background-color: #27ae60; }
        """)
        self.btn_submit.clicked.connect(lambda: asyncio.create_task(self.envoyer_donnees()))
        form_layout.addWidget(self.btn_submit)

        layout.addWidget(form_frame)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    # ------------------------------------------------------------------
    # Capture (thread dédié)
    # ------------------------------------------------------------------
    def start_capture(self):
        if self._capture_thread and self._capture_thread.isRunning():
            return
        self.captured_images = []
        self.btn_capture.setEnabled(False)
        self.capture_status.setText("Capture en cours… (10 photos automatiques)")
        self._capture_thread = CaptureThread(nb_images=10)
        self._capture_thread.done_signal.connect(self._on_capture_done)
        self._capture_thread.error_signal.connect(self._on_capture_error)
        self._capture_thread.start()

    def _on_capture_done(self, frames):
        self.captured_images = frames
        self.btn_capture.setEnabled(True)
        self.capture_status.setText(f"✓ {len(frames)} photos capturées")
        self.capture_status.setStyleSheet("background: transparent; color: #2ecc71; font-style: italic;")

    def _on_capture_error(self, msg):
        self.btn_capture.setEnabled(True)
        self.capture_status.setText(f"Erreur : {msg}")
        self.capture_status.setStyleSheet("background: transparent; color: #e74c3c; font-style: italic;")

    # ------------------------------------------------------------------
    # Envoi API
    # ------------------------------------------------------------------
    async def envoyer_donnees(self):
        if not self.nom.text() or not self.numero.text():
            QMessageBox.warning(self, "Champs manquants", "Nom et numéro sont obligatoires.")
            return

        data = {
            "Nom_eleve":    self.nom.text(),
            "Prenom_eleve": self.prenom.text(),
            "Classe_eleve": self.classe.text(),
            "Numero_eleve": self.numero.text(),
        }

        files = []

        # WARN-08 : fichier photo fermé proprement avec 'with'
        if self.photo_path:
            filename = self.photo_path.replace("\\", "/").split("/")[-1]
            with open(self.photo_path, "rb") as f:
                photo_bytes = f.read()
            files.append(("photo", (filename, photo_bytes, "image/jpeg")))

        for i, img in enumerate(self.captured_images):
            _, buffer = cv2.imencode(".jpg", img)
            files.append(("images", (f"face_{i}.jpg", buffer.tobytes(), "image/jpeg")))

        if not files:
            QMessageBox.warning(self, "Photos manquantes",
                                "Chargez une photo ou capturez des images avant d'enregistrer.")
            return

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{API_BASE_URL}/eleve/create",
                    data=data,
                    files=files,
                )
            if response.status_code == 200:
                global_signals.data_changed.emit()
                self.clear_fields()
                QMessageBox.information(self, "Succès", "Élève enregistré avec succès.")
            else:
                QMessageBox.warning(self, "Erreur backend", response.text)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    # ------------------------------------------------------------------
    # Helpers UI
    # ------------------------------------------------------------------
    def create_input(self, layout, label_text):
        label = QLabel(label_text)
        label.setStyleSheet("background: transparent; color: #f4f7fb; font-weight: 600; margin-top: 4px;")
        layout.addWidget(label)
        field = QLineEdit()
        field.setStyleSheet("""
            QLineEdit {
                background-color: #121524;
                border: 1px solid #23283d;
                padding: 12px;
                border-radius: 10px;
                color: white;
                margin-bottom: 4px;
            }
            QLineEdit:focus { border: 1px solid #4facfe; }
        """)
        layout.addWidget(field)
        return field

    def upload_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner la photo", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.photo_path = file_path
            pixmap = QPixmap(file_path)
            self.photo_label.setPixmap(pixmap.scaled(
                self.photo_label.width(), self.photo_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
            self.photo_label.setScaledContents(False)

    def clear_fields(self):
        self.nom.clear()
        self.prenom.clear()
        self.classe.clear()
        self.numero.clear()
        self.photo_label.clear()
        self.photo_label.setText("Format\nPortrait")
        self.photo_path = None
        self.captured_images = []
        self.capture_status.setText("")
