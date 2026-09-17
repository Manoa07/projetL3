from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox,
    QDateEdit, QTimeEdit, QComboBox, QHBoxLayout, QTableWidget,
    QTableWidgetItem,
)
from PyQt6.QtCore import Qt, QDate, QTime
import requests
from config import API_BASE_URL, API_TIMEOUT
from components.icon_loader import load_icon
from services.events import global_signals

# Style commun pour les QTimeEdit
_TIME_STYLE = """
    QTimeEdit {
        padding: 10px 12px;
        border: 1px solid #23283d;
        border-radius: 10px;
        background-color: #151826;
        color: #f4f7fb;
        font-size: 14px;
        min-width: 400px;
    }
    QTimeEdit:focus {
        border: 1px solid #4facfe;
    }
    QTimeEdit::up-button {
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 22px;
        border-left: 1px solid #23283d;
        border-bottom: 1px solid #23283d;
        border-top-right-radius: 10px;
        background-color: #1a1f2f;
    }
    QTimeEdit::up-button:hover  { background-color: #2a304b; }
    QTimeEdit::down-button {
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 22px;
        border-left: 1px solid #23283d;
        border-bottom-right-radius: 10px;
        background-color: #1a1f2f;
    }
    QTimeEdit::down-button:hover { background-color: #2a304b; }
    QTimeEdit::up-arrow   { image: none; width: 0; height: 0;
                            border-left: 5px solid transparent;
                            border-right: 5px solid transparent;
                            border-bottom: 6px solid #4facfe; }
    QTimeEdit::down-arrow { image: none; width: 0; height: 0;
                            border-left: 5px solid transparent;
                            border-right: 5px solid transparent;
                            border-top: 6px solid #4facfe; }
"""


def make_time_edit() -> QTimeEdit:
    """
    QTimeEdit avec saisie section par section native.

    Comportement :
    - Affiche '--:--' au départ (QTime() invalide)
    - Le ':' est fixe, infranchissable au clavier
    - Saisie chiffre par chiffre : 2 chiffres saisis → passage auto à la section suivante
    - Effacer (Delete/Backspace) remet '--' sur la section active, pas le ':'
    - Flèches haut/bas incrémentent/décrémentent la section active
    - Plage 00:00–23:59 respectée automatiquement par Qt
    """
    field = QTimeEdit()
    # On utilise le format natif avec sections : Qt gère tout automatiquement.
    # QTime() (invalide) → Qt affiche '--' dans chaque section tant que
    # l'utilisateur n'a pas saisi de valeur. C'est le comportement natif
    # sans setSpecialValueText qui casse la navigation.
    field.setDisplayFormat("HH:mm")
    field.setMinimumTime(QTime(0, 0))
    field.setMaximumTime(QTime(23, 59))
    # QTime() invalide → sections affichent '--' nativement
    field.setTime(QTime())
    field.setStyleSheet(_TIME_STYLE)
    field.setMinimumWidth(400)
    return field


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
        self.input_debut = make_time_edit()
        self.input_fin   = make_time_edit()

        self.input_prof    = QComboBox()
        self.input_salle   = QComboBox()
        self.input_matiere = QComboBox()
        _combo_style = """
            QComboBox { padding: 10px; border: 1px solid #23283d;
                        border-radius: 10px; background-color: #151826; color: #f4f7fb; }
            QComboBox::drop-down { border: none; background-color: #151826; }
            QComboBox QAbstractItemView { background-color: #151826; color: #f4f7fb;
                                          selection-background-color: #2a304b;
                                          selection-color: #ffffff; border: 1px solid #23283d; }
        """
        for field, placeholder in (
            (self.input_prof,    "Choisir un professeur"),
            (self.input_salle,   "Choisir une salle"),
            (self.input_matiere, "Choisir une matière"),
        ):
            field.setPlaceholderText(placeholder)
            field.setMinimumWidth(400)
            field.setStyleSheet(_combo_style)

        for label, widget in (
            ("Nom du cours",   self.input_nom),
            ("Date du cours",  self.input_date),
            ("Heure de début", self.input_debut),
            ("Heure de fin",   self.input_fin),
            ("Professeur",     self.input_prof),
            ("Salle",          self.input_salle),
            ("Matière",        self.input_matiere),
        ):
            layout.addWidget(QLabel(label))
            layout.addWidget(widget)

        btn_save = QPushButton("ENREGISTRER LE COURS")
        btn_save.setIcon(load_icon("course"))
        btn_save.setFixedSize(300, 40)
        btn_save.setStyleSheet(
            """ 
              QPushButton { background: #2ecc71; color: white; font-weight: 700; border-radius: 12px; padding: 6px 12px} 
              QPushButton:hover{ background-color: #052613;}
            """
        )
        btn_save.clicked.connect(self.submit_cours)
        self.btn_save = btn_save
        layout.addWidget(btn_save, alignment=Qt.AlignmentFlag.AlignCenter)

        refresh = QPushButton("↻ Actualiser les référentiels")
        refresh.clicked.connect(self.load_references)
        layout.addWidget(refresh, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status = QLabel("Chargement des référentiels…")
        self.status.setStyleSheet("color: #8b93a7; font-style: italic;")
        layout.addWidget(self.status, alignment=Qt.AlignmentFlag.AlignCenter)
        self.cours_table = QTableWidget(0, 8)
        self.cours_table.setHorizontalHeaderLabels(
            ["ID", "Nom", "Date", "Heure début", "Heure fin",
             "Salle", "Matière", "Actions"]
        )
        layout.addWidget(self.cours_table)
        layout.addStretch()

        self.editing_cours_id = None
        self.load_references()
        self.load_cours()
        global_signals.data_changed.connect(self.load_references)
        global_signals.data_changed.connect(self.load_cours)

    # ------------------------------------------------------------------
    def create_input(self, placeholder):
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setFixedWidth(400)
        field.setStyleSheet(
            "QLineEdit { padding: 12px; border: 1px solid #23283d; "
            "border-radius: 10px; background: #151826; color: white; }"
        )
        return field

    def load_references(self):
        endpoints = (
            (self.input_prof,    "professeur/all",
             lambda i: f"{i['nom_professeur']} {i['prenom_professeur']} — {i['matricule_professeur']}",
             "id_professeur"),
            (self.input_salle,   "salle/all",    lambda i: i["nom_salle"],    "id_salle"),
            (self.input_matiere, "matiere/all",  lambda i: i["nom_matiere"],  "id_matiere"),
        )
        try:
            for field, endpoint, label_fn, identifier in endpoints:
                response = requests.get(
                    f"{API_BASE_URL}/{endpoint}",
                    timeout=API_TIMEOUT,
                )
                response.raise_for_status()
                field.clear()
                field.addItem("— Sélectionner —", None)
                for item in response.json():
                    field.addItem(label_fn(item), item[identifier])
            self.status.setText("Référentiels disponibles")
            self.status.setStyleSheet("color: #2ecc71;")
        except (requests.RequestException, KeyError, TypeError):
            self.status.setText("Référentiels indisponibles — démarrez le backend puis actualisez")
            self.status.setStyleSheet("color: #f39c12;")

    def _reference_label(self, field, identifier):
        index = field.findData(identifier)
        return field.itemText(index) if index >= 0 else str(identifier or "")

    def load_cours(self):
        try:
            response = requests.get(
                f"{API_BASE_URL}/cours/all",
                timeout=API_TIMEOUT,
            )
            response.raise_for_status()
            self.cours_table.setRowCount(0)
            for row, item in enumerate(response.json()):
                self.cours_table.insertRow(row)
                values = (
                    item.get("Id_cours", item.get("id_cours", "")),
                    item.get("nom_cours", item.get("Nom_cours", "")),
                    item.get("date_cours", ""),
                    item.get("heure_debut_cours", ""),
                    item.get("heure_fin_cours", ""),
                    self._reference_label(
                        self.input_salle, item.get("id_salle_salle")
                    ),
                    self._reference_label(
                        self.input_matiere, item.get("id_matiere_matiere")
                    ),
                )
                for column, value in enumerate(values):
                    self.cours_table.setItem(
                        row, column, QTableWidgetItem(str(value))
                    )
                actions = QWidget()
                actions_layout = QHBoxLayout(actions)
                actions_layout.setContentsMargins(2, 2, 2, 2)
                update_button = QPushButton("Modifier")
                delete_button = QPushButton("Supprimer")
                update_button.clicked.connect(
                    lambda checked=False, current=item: self.update_cours(current)
                )
                delete_button.clicked.connect(
                    lambda checked=False, current=item: self.delete_cours(current)
                )
                actions_layout.addWidget(update_button)
                actions_layout.addWidget(delete_button)
                self.cours_table.setCellWidget(row, 7, actions)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            self.status.setText("Impossible de charger les cours.")
            self.status.setStyleSheet("color: #f39c12;")
        except (requests.RequestException, KeyError, TypeError, ValueError):
            self.status.setText("Réponse invalide du serveur.")
            self.status.setStyleSheet("color: #f39c12;")

    def update_cours(self, item):
        self.editing_cours_id = item.get("Id_cours", item.get("id_cours"))
        self.input_nom.setText(item.get("nom_cours", item.get("Nom_cours", "")))
        date_value = str(item.get("date_cours", ""))[:10]
        parsed_date = QDate.fromString(date_value, "yyyy-MM-dd")
        if parsed_date.isValid():
            self.input_date.setDate(parsed_date)
        for field, value in (
            (self.input_debut, item.get("heure_debut_cours")),
            (self.input_fin, item.get("heure_fin_cours")),
        ):
            parsed_time = QTime.fromString(str(value or "")[:8], "HH:mm:ss")
            if parsed_time.isValid():
                field.setTime(parsed_time)
        for field, key in (
            (self.input_prof, "id_professeur_professeur"),
            (self.input_salle, "id_salle_salle"),
            (self.input_matiere, "id_matiere_matiere"),
        ):
            index = field.findData(item.get(key))
            if index >= 0:
                field.setCurrentIndex(index)
        self.btn_save.setText("MODIFIER LE COURS")
        self.status.setText("Modification en cours : validez avec le bouton ci-dessus.")

    def delete_cours(self, item):
        cours_id = item.get("Id_cours", item.get("id_cours"))
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer ce cours ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            response = requests.delete(
                f"{API_BASE_URL}/cours/{cours_id}",
                timeout=API_TIMEOUT,
            )
            if response.status_code == 204:
                QMessageBox.information(self, "Succès", "Cours supprimé avec succès.")
                global_signals.data_changed.emit()
            elif response.status_code == 409:
                QMessageBox.warning(
                    self, "Suppression impossible",
                    "Ce cours possède des présences associées.",
                )
            elif response.status_code == 404:
                QMessageBox.warning(self, "Introuvable", "Ce cours n'existe plus.")
                global_signals.data_changed.emit()
            else:
                QMessageBox.warning(self, "Erreur", response.text)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            QMessageBox.critical(
                self, "Erreur Réseau",
                "Le serveur est inaccessible ou a mis trop de temps à répondre.",
            )
        except requests.RequestException as error:
            QMessageBox.critical(self, "Erreur", f"Connexion serveur échouée : {error}")

    def submit_cours(self):
        # QTime() invalide = l'utilisateur n'a pas saisi d'heure
        if not self.input_debut.time().isValid() or not self.input_fin.time().isValid():
            QMessageBox.warning(self, "Erreur",
                                "Veuillez saisir les heures de début et de fin.")
            return

        data = {
            "nom_cours":               self.input_nom.text().strip(),
            "date_cours":              self.input_date.date().toString("yyyy-MM-dd"),
            "heure_debut_cours":       self.input_debut.time().toString("HH:mm:ss"),
            "heure_fin_cours":         self.input_fin.time().toString("HH:mm:ss"),
            "id_professeur_professeur": self.input_prof.currentData(),
            "id_salle_salle":          self.input_salle.currentData(),
            "id_matiere_matiere":      self.input_matiere.currentData(),
        }
        if not data["nom_cours"] or not all(
            data[k] for k in ("id_professeur_professeur", "id_salle_salle", "id_matiere_matiere")
        ):
            QMessageBox.warning(self, "Erreur",
                                "Renseignez le nom du cours et sélectionnez un professeur, une salle et une matière.")
            return

        try:
            method = requests.put if self.editing_cours_id else requests.post
            endpoint = (
                f"{API_BASE_URL}/cours/{self.editing_cours_id}"
                if self.editing_cours_id
                else f"{API_BASE_URL}/cours/create"
            )
            response = method(
                endpoint,
                json=data,
                timeout=API_TIMEOUT,
            )
            if response.status_code in (200, 201):
                message = (
                    "Cours modifié avec succès !"
                    if self.editing_cours_id
                    else "Cours ajouté avec succès !"
                )
                QMessageBox.information(self, "Succès", message)
                self.editing_cours_id = None
                self.btn_save.setText("ENREGISTRER LE COURS")
                global_signals.data_changed.emit()
                self.input_nom.clear()
                # Remettre '--:--' (QTime() invalide)
                self.input_debut.setTime(QTime())
                self.input_fin.setTime(QTime())
                for field in (self.input_prof, self.input_salle, self.input_matiere):
                    field.setCurrentIndex(0)
            elif response.status_code == 404:
                QMessageBox.warning(self, "Introuvable", response.text)
            elif response.status_code == 409:
                QMessageBox.warning(self, "Conflit", response.text)
            else:
                QMessageBox.warning(
                    self, "Erreur",
                    f"Impossible d'enregistrer le cours ({response.status_code}) :\n{response.text}"
                )
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            QMessageBox.critical(
                self,
                "Erreur Réseau",
                "Le serveur est inaccessible ou a mis trop de temps à répondre.",
            )
        except requests.RequestException as error:
            QMessageBox.critical(self, "Erreur", f"Connexion serveur échouée : {error}")
