from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox,
    QDateEdit, QTimeEdit, QComboBox, QAbstractSpinBox,
)
from PyQt6.QtCore import Qt, QDate, QTime
import requests
from components.icon_loader import load_icon
from services.events import global_signals


class AjoutCoursView(QWidget):
    """Saisie d'un cours selon les colonnes de la table cours du MLD."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("<h2 style='color: #f4f7fb;'>AJOUT COURS</h2>")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.input_nom = self.create_input("Nom du cours")
        self.input_date = QDateEdit(QDate.currentDate())
        self.input_date.setCalendarPopup(True)
        self.input_date.setDisplayFormat("dd/MM/yyyy")
        self.input_debut = QTimeEdit(QTime(8, 0))
        self.input_fin = QTimeEdit(QTime(10, 0))
        for field in (self.input_debut, self.input_fin):
            field.setDisplayFormat("HH:mm")
            field.setKeyboardTracking(False)
            field.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            field.setReadOnly(False)
            field.lineEdit().setReadOnly(False)
            field.lineEdit().setPlaceholderText("HH:mm")
            field.lineEdit().setStyleSheet("background: transparent; color: #f4f7fb; border: none; padding: 0;")
        self.input_prof = QComboBox()
        self.input_salle = QComboBox()
        self.input_matiere = QComboBox()
        for field, placeholder in ((self.input_prof, "Choisir un professeur"), (self.input_salle, "Choisir une salle"), (self.input_matiere, "Choisir une matière")):
            field.setPlaceholderText(placeholder)
            field.setMinimumWidth(400)
            field.setStyleSheet("""
                QComboBox { padding: 10px; border: 1px solid #23283d;
                            border-radius: 10px; background-color: #151826; color: #f4f7fb; }
                QComboBox::drop-down { border: none; background-color: #151826; }
                QComboBox QAbstractItemView { background-color: #151826; color: #f4f7fb;
                                              selection-background-color: #2a304b;
                                              selection-color: #ffffff; border: 1px solid #23283d; }
            """)

        for label, widget in (
            ("Nom du cours", self.input_nom), ("Date du cours", self.input_date),
            ("Heure de début", self.input_debut), ("Heure de fin", self.input_fin),
            ("Professeur", self.input_prof),
            ("Salle", self.input_salle), ("Matière", self.input_matiere),
        ):
            if label:
                layout.addWidget(QLabel(label))
            layout.addWidget(widget)

        btn_save = QPushButton("ENREGISTRER LE COURS")
        btn_save.setIcon(load_icon("course"))
        btn_save.setFixedSize(300, 50)
        btn_save.setStyleSheet("QPushButton { background: #2ecc71; color: white; font-weight: 700; border-radius: 12px; }")
        btn_save.clicked.connect(self.submit_cours)
        layout.addWidget(btn_save, alignment=Qt.AlignmentFlag.AlignCenter)
        refresh = QPushButton("↻ Actualiser les référentiels")
        refresh.clicked.connect(self.load_references)
        layout.addWidget(refresh, alignment=Qt.AlignmentFlag.AlignCenter)
        self.status = QLabel("Chargement des référentiels…")
        self.status.setStyleSheet("color: #8b93a7; font-style: italic;")
        layout.addWidget(self.status, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        self.load_references()
        global_signals.data_changed.connect(self.load_references)

    def create_input(self, placeholder):
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setFixedWidth(400)
        field.setStyleSheet("QLineEdit { padding: 12px; border: 1px solid #23283d; border-radius: 10px; background: #151826; color: white; }")
        return field

    def load_references(self):
        endpoints = ((self.input_prof, "professeur/all", lambda item: f"{item['nom_professeur']} {item['prenom_professeur']} — {item['matricule_professeur']}", "id_professeur"), (self.input_salle, "salle/all", lambda item: item["nom_salle"], "id_salle"), (self.input_matiere, "matiere/all", lambda item: item["nom_matiere"], "id_matiere"))
        try:
            for field, endpoint, label, identifier in endpoints:
                response = requests.get(f"http://127.0.0.1:8000/{endpoint}", timeout=5)
                response.raise_for_status()
                field.clear()
                field.addItem("— Sélectionner —", None)
                for item in response.json():
                    field.addItem(label(item), item[identifier])
            self.status.setText("Référentiels disponibles")
            self.status.setStyleSheet("color: #2ecc71;")
        except (requests.RequestException, KeyError, TypeError) as error:
            self.status.setText("Référentiels indisponibles — démarrez le backend puis actualisez")
            self.status.setStyleSheet("color: #f39c12;")

    def submit_cours(self):
        data = {
            "nom_cours": self.input_nom.text().strip(),
            "date_cours": self.input_date.date().toString("yyyy-MM-dd"),
            "heure_debut_cours": self.input_debut.time().toString("HH:mm:ss"),
            "heure_fin_cours": self.input_fin.time().toString("HH:mm:ss"),
            "id_professeur_professeur": self.input_prof.currentData(),
            "id_salle_salle": self.input_salle.currentData(),
            "id_matiere_matiere": self.input_matiere.currentData(),
        }
        if not data["nom_cours"] or not all(data[key] for key in (
            "id_professeur_professeur", "id_salle_salle", "id_matiere_matiere")):
            QMessageBox.warning(self, "Erreur", "Renseignez le cours et les trois identifiants du MLD.")
            return
        try:
            response = requests.post("http://127.0.0.1:8000/cours/create", json=data, timeout=10)
            if response.status_code in (200, 201):
                QMessageBox.information(self, "Succès", "Cours ajouté avec succès !")
                global_signals.data_changed.emit()
                self.input_nom.clear()
                for field in (self.input_prof, self.input_salle, self.input_matiere):
                    field.setCurrentIndex(0)
            else:
                QMessageBox.warning(self, "Erreur", f"Impossible d'enregistrer le cours ({response.status_code}) :\n{response.text}")
        except requests.RequestException as error:
            QMessageBox.critical(self, "Erreur", f"Connexion serveur échouée : {error}")
