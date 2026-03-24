from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton, 
                             QLabel, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
import requests

class AjoutCoursView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # Titre
        title = QLabel("<h2 style='color: #4facfe;'>ENREGISTRER UN NOUVEAU COURS</h2>")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Formulaire
        self.input_nom = self.create_input("Nom du cours (ex: Algorithmique)")
        self.input_prof = self.create_input("Nom du Professeur")
        self.input_salle = self.create_input("Salle (ex: Salle 102)")

        layout.addWidget(self.input_nom)
        layout.addWidget(self.input_prof)
        layout.addWidget(self.input_salle)

        # Bouton de validation
        btn_save = QPushButton("💾 ENREGISTRER LE COURS")
        btn_save.setFixedSize(300, 50)
        btn_save.setStyleSheet("""
            QPushButton { 
                background: #2ecc71; color: white; font-weight: bold; border-radius: 5px; 
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
                padding: 12px; border: 1px solid #2d2f41; 
                border-radius: 5px; background: #24273d; color: white;
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