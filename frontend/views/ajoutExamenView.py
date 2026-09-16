from PyQt6.QtCore import QDate, Qt, QTime
from PyQt6.QtWidgets import (
    QComboBox, QDateEdit, QLineEdit, QTimeEdit,
    QVBoxLayout, QLabel, QPushButton, QMessageBox, QWidget,
)
import requests
from components.icon_loader import load_icon
from services.events import global_signals
from views.ajoutCoursView import make_time_edit   # réutilisation du même helper


class AjoutExamenView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(
            QLabel("<h2 style='color:#f4f7fb;'>AJOUT EXAMEN</h2>"),
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        self.semestre = QLineEdit()
        self.semestre.setPlaceholderText("Semestre (ex: S1)")
        self.semestre.setMinimumWidth(400)
        self.semestre.setStyleSheet(
            "QLineEdit { padding: 12px; border: 1px solid #23283d; "
            "border-radius: 10px; background: #151826; color: white; }"
        )

        self.date = QDateEdit(QDate.currentDate())
        self.date.setCalendarPopup(True)

        # QTimeEdit correctement configuré : flèches visibles, '--:--' par défaut
        self.debut = make_time_edit()
        self.fin   = make_time_edit()

        self.salle   = QComboBox()
        self.matiere = QComboBox()
        _combo_style = """
            QComboBox { padding: 10px; border: 1px solid #23283d;
                        border-radius: 10px; background-color: #151826; color: #f4f7fb; }
            QComboBox::drop-down { border: none; background-color: #151826; }
            QComboBox QAbstractItemView { background-color: #151826; color: #f4f7fb;
                                          selection-background-color: #2a304b;
                                          selection-color: #ffffff; border: 1px solid #23283d; }
        """
        for field in (self.salle, self.matiere):
            field.setMinimumWidth(400)
            field.setStyleSheet(_combo_style)

        for label, field in (
            ("Semestre",        self.semestre),
            ("Date",            self.date),
            ("Heure de début",  self.debut),
            ("Heure de fin",    self.fin),
            ("Salle",           self.salle),
            ("Matière",         self.matiere),
        ):
            layout.addWidget(QLabel(label))
            layout.addWidget(field)

        save = QPushButton("ENREGISTRER L'EXAMEN")
        save.setIcon(load_icon("course"))
        save.clicked.connect(self.submit)
        save.setStyleSheet(
            """ 
              QPushButton { background: #2ecc71; color: white; font-weight: 700; border-radius: 12px; padding: 6px 12px} 
              QPushButton:hover{ background-color: #052613;}
            """
        )
        save.setFixedSize(300, 40)
        layout.addWidget(save, alignment=Qt.AlignmentFlag.AlignCenter)

        refresh = QPushButton("↻ Actualiser les salles et matières")
        refresh.clicked.connect(self.load_references)
        layout.addWidget(refresh, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status = QLabel("Chargement des salles et matières…")
        self.status.setStyleSheet("color:#8b93a7; font-style:italic;")
        layout.addWidget(self.status, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        self.load_references()
        global_signals.data_changed.connect(self.load_references)

    def load_references(self):
        try:
            sr = requests.get("http://127.0.0.1:8000/salle/all",   timeout=5)
            mr = requests.get("http://127.0.0.1:8000/matiere/all", timeout=5)
            sr.raise_for_status(); mr.raise_for_status()
            self.salle.clear();   self.salle.addItem("— Sélectionner —", None)
            self.matiere.clear(); self.matiere.addItem("— Sélectionner —", None)
            for item in sr.json():
                self.salle.addItem(item["nom_salle"], item["id_salle"])
            for item in mr.json():
                self.matiere.addItem(item["nom_matiere"], item["id_matiere"])
            self.status.setText("Salles et matières disponibles")
            self.status.setStyleSheet("color:#2ecc71;")
        except (requests.RequestException, KeyError, TypeError):
            self.status.setText("Aucune donnée disponible — créez d'abord une salle et une matière")
            self.status.setStyleSheet("color:#f39c12;")

    def submit(self):
        # QTime() invalide = l'utilisateur n'a pas saisi d'heure
        if not self.debut.time().isValid() or not self.fin.time().isValid():
            QMessageBox.warning(self, "Erreur",
                                "Veuillez saisir les heures de début et de fin.")
            return

        data = {
            "date_examen":      self.date.date().toString("yyyy-MM-dd"),
            "heure_debut":      self.debut.time().toString("HH:mm:ss"),
            "heure_fin":        self.fin.time().toString("HH:mm:ss"),
            "semestre_examen":  self.semestre.text().strip(),
            "id_salle_salle":   self.salle.currentData(),
            "id_matiere_matiere": self.matiere.currentData(),
        }
        if not data["semestre_examen"] or not data["id_salle_salle"] or not data["id_matiere_matiere"]:
            QMessageBox.warning(self, "Erreur",
                                "Renseignez le semestre et sélectionnez une salle et une matière.")
            return

        try:
            response = requests.post(
                "http://127.0.0.1:8000/examen/create", json=data, timeout=10
            )
            if response.status_code in (200, 201):
                QMessageBox.information(self, "Succès", "Examen ajouté avec succès.")
                self.semestre.clear()
                # Remettre '--:--' (QTime() invalide)
                self.debut.setTime(QTime())
                self.fin.setTime(QTime())
                global_signals.data_changed.emit()
            else:
                QMessageBox.warning(self, "Erreur", response.text)
        except requests.RequestException as error:
            QMessageBox.critical(self, "Erreur", f"Connexion serveur échouée : {error}")
