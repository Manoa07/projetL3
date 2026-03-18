from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFileDialog, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import requests
class AjoutEleveView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(20, 5, 20, 5)

        title = QLabel("<b style='color:#4facfe; font-size:20px;'>AJOUTER UN NOUVEL ÉLÈVE</b>")
        layout.addWidget(title)

        # Formulaire
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #1a1c2e; border-radius: 15px; padding: 1px;")
        form_layout = QVBoxLayout(form_frame)

        self.nom = self.create_input(form_layout, "Nom :")
        self.prenom = self.create_input(form_layout, "Prénom :")
        self.classe = self.create_input(form_layout, "Classe :")
        self.numero = self.create_input(form_layout, "Numéro d'inscription :")

        # --- SECTION PHOTO (PORTRAIT IDENTITÉ) ---
        form_layout.addSpacing(10)
        form_layout.addWidget(QLabel("Photo d'identité :"))
        
        photo_section = QHBoxLayout()
        
        # Le cadre de la photo est fixé au format portrait (ex: 150x200 px)
        self.photo_label = QLabel("Format\nPortrait")
        self.photo_label.setFixedSize(150, 200) 
        self.photo_label.setStyleSheet("""
            border: 2px dashed #2d2f41; 
            border-radius: 10px; 
            background-color: #0f111a;
            color: #454859;
        """)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Bouton pour importer
        self.btn_photo = QPushButton("📁 Charger la photo")
        self.btn_photo.setFixedSize(300, 50)
        self.btn_photo.setStyleSheet("""
            QPushButton { background-color: #2d2f41; color: white; border-radius: 8px; }
            QPushButton:hover { background-color: #3d405b; }
        """)
        self.btn_photo.clicked.connect(self.upload_photo)
        
        photo_section.addWidget(self.photo_label)
        photo_section.addWidget(self.btn_photo)
        photo_section.addStretch() # Pousse tout vers la gauche
        
        form_layout.addLayout(photo_section)

        # Bouton Valider
        btn_submit = QPushButton("ENREGISTRER L'ÉLÈVE")
        btn_submit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_submit.setStyleSheet("""
            QPushButton { background-color: #2ecc71; color: white; font-weight: bold; padding: 15px; margin-top: 20px; border-radius: 10px; }
            QPushButton:hover { background-color: #27ae60; }
        """)
        btn_submit.clicked.connect(self.envoyer_donnees)
        form_layout.addWidget(btn_submit)
        

        layout.addWidget(form_frame)
    
    def envoyer_donnees(self):
        data = {
        "Nom_eleve": self.nom.text(),
        "Prenom_eleve": self.prenom.text(),
        "Classe_eleve": self.classe.text(),
        "Numero_eleve": self.numero.text()
        }
        try:
            reponse=requests.post("http://127.0.0.1:8000/eleve/create",json=data)
            if(reponse):
                print("Données envoyées avec succès !")
        except Exception as e:
            print("Erreur :",e)



    def create_input(self, layout, label_text):
        layout.addWidget(QLabel(label_text))
        field = QLineEdit()
        field.setStyleSheet("background-color: #0f111a; border: 1px solid #2d2f41; padding: 10px; border-radius: 5px; color: white;")
        layout.addWidget(field)
        return field

    def upload_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner la photo", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            pixmap = QPixmap(file_path)
            # On redimensionne l'image pour remplir exactement le cadre 150x200
            # IgnoreAspectRatio est utilisé ici pour forcer le format portrait d'identité
            self.photo_label.setPixmap(pixmap.scaled(
                self.photo_label.width(), 
                self.photo_label.height(), 
                Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                Qt.TransformationMode.SmoothTransformation
            ))
            # On s'assure que l'image ne dépasse pas du cadre arrondi
            self.photo_label.setScaledContents(True)