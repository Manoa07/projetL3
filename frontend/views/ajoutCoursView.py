from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton, 
                             QLabel, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
import requests
from components.icon_loader import load_icon

class AjoutCoursView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Titre
        title = QLabel("<h2 style='color: #f4f7fb; letter-spacing: 1.4px;'>AJOUT COURS</h2>")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Formulaire
        self.input_nom = self.create_input("Nom du cours (ex: Algorithmique)")
        self.input_prof = self.create_input("Nom du Professeur")
        self.input_salle = self.create_input("Salle (ex: Salle 102)")

        layout.addWidget(self.input_nom)
        layout.addWidget(self.input_prof)
        layout.addWidget(self.input_salle)

        # Bouton de validation
        btn_save = QPushButton("ENREGISTRER LE COURS")
        btn_save.setIcon(load_icon("course"))
        btn_save.setFixedSize(300, 50)
        btn_save.setStyleSheet("""
            QPushButton { 
                background: #2ecc71; color: white; font-weight: 700; border-radius: 12px; 
            }
            QPushButton:hover { background: #27ae60; }
        """)
        btn_save.clicked.connect(self.submit_cours)
        layout.addWidget(btn_save, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def create_input(self, placeholder):
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setFixedWidth(400)
        field.setStyleSheet("""
            QLineEdit { 
                padding: 12px; border: 1px solid #23283d; 
                border-radius: 10px; background: #151826; color: white;
            }
            QLineEdit:focus {
                border: 1px solid #4facfe;
            }
        """)
        return field

    def submit_cours(self):
        data = {
            "Nom_cours": self.input_nom.text(),
            "Prof_cours": self.input_prof.text(), # Correspond à votre cours_service.py
            "Salle_cours": self.input_salle.text()
        }
        
        if not data["Nom_cours"] or not data["Prof_cours"]:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir les champs obligatoires.")
            return

        try:
            # Assurez-vous que l'URL correspond à votre route FastAPI
            response = requests.post("http://127.0.0.1:8000/cours/create", json=data)
            if response.status_code in [200, 201]:
                QMessageBox.information(self, "Succès", "Cours ajouté avec succès !")
                self.input_nom.clear()
                self.input_prof.clear()
                self.input_salle.clear()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Connexion serveur échouée : {e}")
