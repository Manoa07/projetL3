from PyQt6.QtCore import QDate, QTime, Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)
import requests

from components.icon_loader import load_icon
from config import API_BASE_URL, API_TIMEOUT
from services.events import global_signals


_TIME_STYLE = """
QTimeEdit {
    padding: 10px 12px;
    border: 1px solid #d8e0e8;
    border-radius: 10px;
    background: #ffffff;
    color: #17212b;
    min-width: 400px;
}
QTimeEdit:focus { border: 1px solid #2e9d68; }
QTimeEdit::up-button, QTimeEdit::down-button {
    width: 22px;
    background: #f6f8fb;
    border-left: 1px solid #d8e0e8;
}
QTimeEdit::up-button:hover, QTimeEdit::down-button:hover { background: #dff1e6; }
"""


# Keep time inputs consistent across course and exam forms.
def make_time_edit():
    field = QTimeEdit()
    field.setDisplayFormat("HH:mm")
    field.setMinimumTime(QTime(0, 0))
    field.setMaximumTime(QTime(23, 59))
    field.setTime(QTime())
    field.setStyleSheet(_TIME_STYLE)
    return field


class AjoutCoursView(QWidget):
    """Saisie d'un cours selon les colonnes de la table cours du MLD."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("<h2 style='color:#17212b;'>AJOUT COURS</h2>")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.input_nom = self.create_input("Nom du cours")
        self.input_date = QDateEdit(QDate.currentDate())
        self.input_date.setCalendarPopup(True)
        self.input_date.setDisplayFormat("dd/MM/yyyy")
        self.input_debut = make_time_edit()
        self.input_fin = make_time_edit()
        self.input_prof = QComboBox()
        self.input_salle = QComboBox()
        self.input_matiere = QComboBox()

        combo_style = """
        QComboBox { padding: 10px; border: 1px solid #d8e0e8;
            border-radius: 10px; background: #ffffff; color: #17212b; }
        QComboBox::drop-down { border: none; background: #ffffff; }
        QComboBox QAbstractItemView { background: #ffffff; color: #17212b;
            selection-background-color: #dff1e6; border: 1px solid #d8e0e8; }
        """
        for field, placeholder in (
            (self.input_prof, "Choisir un professeur"),
            (self.input_salle, "Choisir une salle"),
            (self.input_matiere, "Choisir une matière"),
        ):
            field.setPlaceholderText(placeholder)
            field.setMinimumWidth(400)
            field.setStyleSheet(combo_style)

        for label, field in (
            ("Nom du cours", self.input_nom),
            ("Date du cours", self.input_date),
            ("Heure de début", self.input_debut),
            ("Heure de fin", self.input_fin),
            ("Professeur", self.input_prof),
            ("Salle", self.input_salle),
            ("Matière", self.input_matiere),
        ):
            layout.addWidget(QLabel(label))
            layout.addWidget(field)

        self.btn_save = QPushButton("ENREGISTRER LE COURS")
        self.btn_save.setIcon(load_icon("course"))
        self.btn_save.setFixedSize(300, 40)
        self.btn_save.setStyleSheet(
            "QPushButton { background:#2e9d68; color:white; font-weight:700; "
            "border-radius:12px; padding:6px 12px; }"
            "QPushButton:hover { background:#247a50; }"
        )
        self.btn_save.clicked.connect(self.submit_cours)
        layout.addWidget(self.btn_save, alignment=Qt.AlignmentFlag.AlignCenter)

        refresh = QPushButton("Actualiser les référentiels")
        refresh.clicked.connect(self.load_references)
        layout.addWidget(refresh, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status = QLabel("Chargement des référentiels...")
        self.status.setStyleSheet("color:#718096; font-style:italic;")
        layout.addWidget(self.status, alignment=Qt.AlignmentFlag.AlignCenter)

        self.cours_table = QTableWidget(0, 8)
        self.cours_table.setHorizontalHeaderLabels(
            ["ID", "Nom", "Date", "Heure début", "Heure fin", "Salle", "Matière", "Actions"]
        )
        layout.addWidget(self.cours_table)
        layout.addStretch()

        self.editing_cours_id = None
        self.load_references()
        self.load_cours()
        global_signals.data_changed.connect(self.load_references)
        global_signals.data_changed.connect(self.load_cours)

    def create_input(self, placeholder):
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setFixedWidth(400)
        field.setStyleSheet(
            "QLineEdit { padding:12px; border:1px solid #d8e0e8; "
            "border-radius:10px; background:#ffffff; color:#17212b; }"
            "QLineEdit:focus { border:1px solid #2e9d68; }"
        )
        return field

    def load_references(self):
        endpoints = (
            (self.input_prof, "professeur/all", lambda item: f"{item['nom_professeur']} {item['prenom_professeur']}", "id_professeur"),
            (self.input_salle, "salle/all", lambda item: item["nom_salle"], "id_salle"),
            (self.input_matiere, "matiere/all", lambda item: item["nom_matiere"], "id_matiere"),
        )
        try:
            for field, endpoint, label_fn, identifier in endpoints:
                response = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=API_TIMEOUT)
                response.raise_for_status()
                field.clear()
                field.addItem("-- Sélectionner --", None)
                for item in response.json():
                    field.addItem(label_fn(item), item[identifier])
            self.status.setText("Référentiels disponibles")
        except (requests.RequestException, KeyError, TypeError):
            self.status.setText("Référentiels indisponibles")

    def load_cours(self):
        try:
            response = requests.get(f"{API_BASE_URL}/cours/all", timeout=API_TIMEOUT)
            response.raise_for_status()
            self.cours_table.setRowCount(0)
            for row, item in enumerate(response.json()):
                self.cours_table.insertRow(row)
                values = (
                    item.get("Id_cours", item.get("id_cours", "")),
                    item.get("nom_cours", item.get("Nom_cours", "")),
                    item.get("date_cours", ""), item.get("heure_debut_cours", ""),
                    item.get("heure_fin_cours", ""), item.get("id_salle_salle", ""),
                    item.get("id_matiere_matiere", ""),
                )
                for column, value in enumerate(values):
                    self.cours_table.setItem(row, column, QTableWidgetItem(str(value)))
        except requests.RequestException:
            self.status.setText("Impossible de charger les cours")

    def submit_cours(self):
        # QTime() invalide = l'utilisateur n'a pas saisi d'heure
        if not self.input_debut.time().isValid() or not self.input_fin.time().isValid():
            QMessageBox.warning(self, "Erreur",
                                "Veuillez saisir les heures de début et de fin.")
            return

        data = {
            "Nom_cours": self.input_nom.text(),
            "Prof_cours": self.input_prof.currentData(),
            "Salle_cours": self.input_salle.currentData(),
            "Matiere_cours": self.input_matiere.currentData(),
        }
        if not data["Nom_cours"] or data["Prof_cours"] is None:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir les champs obligatoires.")
            return
        endpoint = f"{API_BASE_URL}/cours/create"
        try:
            response = requests.post(endpoint, json=data, timeout=API_TIMEOUT)
            if response.status_code in (200, 201):
                QMessageBox.information(self, "Succès", "Cours ajouté avec succès.")
                self.input_nom.clear()
                global_signals.data_changed.emit()
            else:
                QMessageBox.warning(self, "Erreur", response.text)
        except requests.RequestException as error:
            QMessageBox.critical(self, "Erreur réseau", str(error))
