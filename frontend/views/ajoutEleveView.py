from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFileDialog, QFrame, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import cv2
from services.events import global_signals
import httpx
import asyncio

class AjoutEleveView(QWidget):
    def __init__(self):
        super().__init__()
        # Layout principal de la vue
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- 1. ZONE DE DÉFILEMENT (SCROLL AREA) ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        
        # Widget qui contient le contenu scrollable
        container = QWidget()
        container.setStyleSheet("background-color: #0f111a;")
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(20, 5, 20, 5)

        # Titre
        title = QLabel("<b style='color:#4facfe; font-size:20px;'>AJOUTER UN NOUVEL ÉLÈVE</b>")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # 2. FORMULAIRE (Le cadre interne)
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #1a1c2e; border-radius: 15px; padding: 25px;")
        # Stashed changes
        form_layout = QVBoxLayout(form_frame)

        self.nom = self.create_input(form_layout, "Nom :")
        self.prenom = self.create_input(form_layout, "Prénom :")
        self.classe = self.create_input(form_layout, "Classe :")
        self.numero = self.create_input(form_layout, "Numéro d'inscription :")


       # --- SECTION PHOTO ---
        form_layout.addSpacing(15)
        form_layout.addWidget(QLabel("Photo d'identité (Portrait) :"))
        
        photo_section = QHBoxLayout()
        # Stashed changes
        self.photo_label = QLabel("Format\nPortrait")
        self.photo_label.setFixedSize(150, 200) 
        self.photo_label.setStyleSheet("""
            border: 2px dashed #2d2f41; 
            border-radius: 10px; 
            background-color: #0f111a;
            color: #454859;
        """)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        

        # Correction du bouton : On augmente la largeur et on force la couleur blanche
        self.btn_photo = QPushButton("📁 Charger la photo")
        self.btn_photo.setMinimumSize(220, 50) # Utilisation de MinimumSize au lieu de FixedSize
        self.btn_photo.setStyleSheet("""
            QPushButton { 
                background-color: #2d2f41; 
                color: #ffffff; 
                border-radius: 8px; 
                font-weight: bold;
                font-size: 13px;
                padding: 5px;
            }
            QPushButton:hover { 
                background-color: #3d405b; 
            }
        """)
        self.btn_photo.clicked.connect(self.upload_photo)
        
        photo_section.addWidget(self.photo_label)
        photo_section.addSpacing(20)
        photo_section.addWidget(self.btn_photo)
        photo_section.addStretch()
        form_layout.addLayout(photo_section)
        #Bouton capture image
        self.btn_capture = QPushButton("📸 Capturer 10 photos")
        self.btn_capture.setStyleSheet("""
             QPushButton {
            background-color: #3498db;
            color: white;
            padding: 12px;
            border-radius: 8px;
            font-weight: bold;
            }
        """)
        self.btn_capture.clicked.connect(self.start_capture)
        form_layout.addWidget(self.btn_capture)

        # Bouton Valider
        self.btn_submit = QPushButton("ENREGISTRER L'ÉLÈVE")
        self.btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_submit.setStyleSheet("""
            QPushButton { background-color: #2ecc71; color: white; font-weight: bold; padding: 18px; margin-top: 30px; border-radius: 10px; font-size: 14px; }
            QPushButton:hover { background-color: #27ae60; }
        """)
        self.btn_submit.clicked.connect(lambda: asyncio.create_task(self.envoyer_donnees()))
        form_layout.addWidget(self.btn_submit)

        layout.addWidget(form_frame)
        
        # Finalisation de la zone de défilement
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    async def envoyer_donnees(self):
        data = {
            "Nom_eleve": self.nom.text(),
            "Prenom_eleve": self.prenom.text(),
            "Classe_eleve": self.classe.text(),
            "Numero_eleve": self.numero.text()
        }
        files=[]
        if hasattr(self, 'photo_path')and self.photo_path:
            files.append((
                "photo",
                (self.photo_path.split("/")[-1],
                open(self.photo_path, "rb"),
                "image/jpeg")
            ))
        if not self.nom.text() or not self.numero.text():
            return
        if hasattr(self,"captured_images"):
            for i, img in enumerate(self.captured_images):
                _,buffer = cv2.imencode(".jpg",img)
                files.append((
                    "images", (f"face_{i}.jpg",buffer.tobytes(),"image/jpeg")
                ))

        try:
            async with httpx.AsyncClient() as client:
                print("FILES ENVOYÉS :")
                for f in files:
                    print(f[0])
                response = await client.post(
                    "http://127.0.0.1:8000/eleve/create",
                    data=data,
                    files=files
                    )
                if response.status_code == 200:
                    global_signals.data_changed.emit()
                    self.clear_fields()
                else:
                    print("Erreur backend :", response.text)
        except Exception as e:
            print(f"Erreur : {e}")

    def create_input(self, layout, label_text):
        layout.addWidget(QLabel(label_text))
        field = QLineEdit()

        field.setStyleSheet("background-color: #0f111a; border: 1px solid #2d2f41; padding: 12px; border-radius: 5px; color: white; margin-bottom: 10px;")

        layout.addWidget(field)
        return field

    def upload_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner la photo", "", "Images (*.png *.jpg *.jpeg)")
        
        if file_path:
            self.photo_path=file_path
            pixmap = QPixmap(file_path)
            self.photo_label.setPixmap(pixmap.scaled(
                self.photo_label.width(), 
                self.photo_label.height(), 
                Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                Qt.TransformationMode.SmoothTransformation
            ))
            self.photo_label.setScaledContents(True)

    def clear_fields(self):
        self.nom.clear()
        self.prenom.clear()
        self.classe.clear()
        self.numero.clear()
        self.photo_label.clear()
        self.photo_label.setText("Format\nPortrait")
    import cv2

    def start_capture(self):
        self.captured_images = []
        cap = cv2.VideoCapture(0)

        count = 0

        while count < 10:
            ret, frame = cap.read()
            if not ret:
               continue

            cv2.imshow("Capture visage (appuie sur espace)", frame)

            key = cv2.waitKey(1)

            if key == 32:  # touche ESPACE
                self.captured_images.append(frame.copy())
                count += 1
                print(f"Photo {count}/10 capturée")

        cap.release()
        cv2.destroyAllWindows()

        print("Capture terminée ✅")
