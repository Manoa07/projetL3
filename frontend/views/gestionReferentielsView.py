from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QLineEdit, QMessageBox, QPushButton, QTabWidget, QVBoxLayout, QWidget
import requests
from services.events import global_signals


class GestionReferentielsView(QWidget):
    """Création des données utilisées par les cours et les examens."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.addWidget(QLabel("<h2 style='color:#f4f7fb;'>GESTION DES DONNÉES</h2>"), alignment=Qt.AlignmentFlag.AlignCenter)

        tabs = QTabWidget()
        tabs.addTab(self.professeur_form(), "Professeur")
        tabs.addTab(self.nom_form("Salle", "Nom de la salle", "salle"), "Salle")
        tabs.addTab(self.nom_form("Matière", "Nom de la matière", "matiere"), "Matière")
        layout.addWidget(tabs)
        self.status = QLabel("Les identifiants sont attribués automatiquement.")
        self.status.setStyleSheet("color:#8b93a7; font-style:italic;")
        layout.addWidget(self.status, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def input_field(self, placeholder):
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setStyleSheet("QLineEdit { padding: 12px; border: 1px solid #23283d; border-radius: 10px; background: #151826; color: white; }")
        return field

    def professeur_form(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        nom = self.input_field("Nom")
        prenom = self.input_field("Prénom")
        matricule = self.input_field("Matricule")
        for field in (nom, prenom, matricule):
            layout.addWidget(field)
        button = QPushButton("Enregistrer le professeur")
        button.clicked.connect(lambda: self.save_professeur(nom, prenom, matricule))
        layout.addWidget(button)
        layout.addStretch()
        return page

    def nom_form(self, title, placeholder, kind):
        page = QWidget()
        layout = QVBoxLayout(page)
        name = self.input_field(placeholder)
        layout.addWidget(name)
        button = QPushButton(f"Enregistrer {title.lower()}")
        button.clicked.connect(lambda: self.save_name(name, kind, title))
        layout.addWidget(button)
        layout.addStretch()
        return page

    def post(self, endpoint, payload, success):
        try:
            response = requests.post(f"http://127.0.0.1:8000/{endpoint}", json=payload, timeout=10)
            if response.status_code in (200, 201):
                self.status.setText(success)
                self.status.setStyleSheet("color:#2ecc71;")
                global_signals.data_changed.emit()
                return True
            QMessageBox.warning(self, "Enregistrement impossible", response.text)
        except requests.RequestException as error:
            QMessageBox.critical(self, "Connexion impossible", str(error))
        return False

    def save_professeur(self, nom, prenom, matricule):
        if self.post("professeur/create", {
            "nom_professeur": nom.text().strip(),
            "prenom_professeur": prenom.text().strip(),
            "matricule_professeur": matricule.text().strip(),
        }, "Professeur enregistré. Il est maintenant disponible dans les cours."):
            nom.clear(); prenom.clear(); matricule.clear()

    def save_name(self, field, kind, title):
        value = field.text().strip()
        if not value:
            QMessageBox.warning(self, "Champ obligatoire", f"Saisissez le nom de la {title.lower()}.")
            return
        if self.post(f"{kind}/create", {"nom": value}, f"{title} enregistré(e)."):
            field.clear()
