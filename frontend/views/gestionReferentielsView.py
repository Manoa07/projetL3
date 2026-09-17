from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
import requests
from config import API_BASE_URL, API_TIMEOUT
from services.events import global_signals


class GestionReferentielsView(QWidget):
    """Création des données utilisées par les cours et les examens."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.addWidget(QLabel("<h2 style='color:#f4f7fb;'>GESTION DES DONNÉES</h2>"), alignment=Qt.AlignmentFlag.AlignCenter)

        self.status = QLabel("Les identifiants sont attribués automatiquement.")
        self.status.setStyleSheet("color:#8b93a7; font-style:italic;")
        tabs = QTabWidget()
        tabs.addTab(self.professeur_form(), "Professeur")
        tabs.addTab(self.nom_form("Salle", "Nom de la salle", "salle"), "Salle")
        tabs.addTab(self.nom_form("Matière", "Nom de la matière", "matiere"), "Matière")
        layout.addWidget(tabs)
        layout.addWidget(self.status, alignment=Qt.AlignmentFlag.AlignCenter)
        global_signals.data_changed.connect(self.load_professeurs)
        global_signals.data_changed.connect(self.load_salle)
        global_signals.data_changed.connect(self.load_matiere)
        layout.addStretch()

    def input_field(self, placeholder):
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setStyleSheet("QLineEdit { padding: 12px; border: 1px solid #d8e0e8; border-radius: 10px; background: #ffffff; color: #17212b; }")
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
        button.setFixedSize(300, 40)
        button.setStyleSheet(
            """ 
              QPushButton { background: #2ecc71; color: white; font-weight: 700; border-radius: 12px; padding: 6px 12px} 
              QPushButton:hover{ background-color: #052613;}
            """
        )
        button.clicked.connect(lambda: self.save_professeur(nom, prenom, matricule))
        layout.addWidget(button, alignment = Qt.AlignmentFlag.AlignCenter )
        self.professeur_table = QTableWidget(0, 5)
        self.professeur_table.setHorizontalHeaderLabels(
            ["ID", "Nom", "Prénom", "Matricule", "Actions"]
        )
        layout.addWidget(self.professeur_table)
        self.load_professeurs()
        layout.addStretch()
        return page

    def nom_form(self, title, placeholder, kind):
        page = QWidget()
        layout = QVBoxLayout(page)
        name = self.input_field(placeholder)
        layout.addWidget(name)
        button = QPushButton(f"Enregistrer {title.lower()}")
        button.setFixedSize(300, 40)
        button.setStyleSheet(
            """ 
              QPushButton { background: #2ecc71; color: white; font-weight: 700; border-radius: 12px; padding: 6px 12px} 
              QPushButton:hover{ background-color: #052613;}
            """
        )
        button.clicked.connect(lambda: self.save_name(name, kind, title))
        layout.addWidget(button, alignment = Qt.AlignmentFlag.AlignCenter )        
        table = QTableWidget(0, 3)
        table.setHorizontalHeaderLabels(["ID", "Nom", "Actions"])
        layout.addWidget(table)
        setattr(self, f"{kind}_table", table)
        getattr(self, f"load_{kind}")()
        layout.addStretch()
        return page

    def load_professeurs(self):
        self._load_referentiel(
            "professeur/all",
            self.professeur_table,
            ("id_professeur", "nom_professeur", "prenom_professeur", "matricule_professeur"),
            "professeur",
        )

    def load_salle(self):
        self._load_referentiel(
            "salle/all",
            self.salle_table,
            ("id_salle", "nom_salle"),
            "salle",
        )

    def load_matiere(self):
        self._load_referentiel(
            "matiere/all",
            self.matiere_table,
            ("id_matiere", "nom_matiere"),
            "matiere",
        )

    def _load_referentiel(self, endpoint, table, fields, kind):
        try:
            response = requests.get(
                f"{API_BASE_URL}/{endpoint}",
                timeout=API_TIMEOUT,
            )
            response.raise_for_status()
            values = response.json()
            table.setRowCount(0)
            for row, value in enumerate(values):
                table.insertRow(row)
                for column, field in enumerate(fields):
                    table.setItem(row, column, QTableWidgetItem(str(value[field])))
                actions = QWidget()
                actions_layout = QHBoxLayout(actions)
                actions_layout.setContentsMargins(2, 2, 2, 2)
                update_button = QPushButton("Modifier")
                delete_button = QPushButton("Supprimer")
                update_button.clicked.connect(
                    lambda checked=False, item=value, item_kind=kind:
                    self.update_referentiel(item_kind, item)
                )
                delete_button.clicked.connect(
                    lambda checked=False, item=value, item_kind=kind:
                    self.delete_referentiel(item_kind, item)
                )
                actions_layout.addWidget(update_button)
                actions_layout.addWidget(delete_button)
                table.setCellWidget(row, len(fields), actions)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            self.status.setText("Impossible de charger les référentiels.")
            self.status.setStyleSheet("color: #f39c12;")
        except (requests.RequestException, KeyError, TypeError):
            self.status.setText("Réponse invalide du serveur.")
            self.status.setStyleSheet("color: #f39c12;")

    def update_referentiel(self, kind, item):
        endpoint = {
            "professeur": f"professeur/{item['id_professeur']}",
            "salle": f"salle/{item['id_salle']}",
            "matiere": f"matiere/{item['id_matiere']}",
        }[kind]
        if kind == "professeur":
            nom, ok_nom = QInputDialog.getText(self, "Modifier", "Nom :", text=item["nom_professeur"])
            if not ok_nom:
                return
            prenom, ok_prenom = QInputDialog.getText(
                self, "Modifier", "Prénom :", text=item["prenom_professeur"]
            )
            if not ok_prenom:
                return
            matricule, ok_matricule = QInputDialog.getInt(
                self, "Modifier", "Matricule :", value=item["matricule_professeur"]
            )
            if not ok_matricule:
                return
            payload = {
                "nom_professeur": nom.strip(),
                "prenom_professeur": prenom.strip(),
                "matricule_professeur": matricule,
            }
        else:
            field = "nom_salle" if kind == "salle" else "nom_matiere"
            value, accepted = QInputDialog.getText(
                self, "Modifier", "Nom :", text=item[field]
            )
            if not accepted or not value.strip():
                return
            payload = {field: value.strip()}
        try:
            response = requests.put(
                f"{API_BASE_URL}/{endpoint}",
                json=payload,
                timeout=API_TIMEOUT,
            )
            if response.status_code == 200:
                self.status.setText("Modification enregistrée.")
                global_signals.data_changed.emit()
                return
            if response.status_code == 409:
                QMessageBox.warning(self, "Conflit", "Ce matricule/nom existe déjà.")
                return
            QMessageBox.warning(self, "Modification impossible", response.text)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            QMessageBox.critical(
                self,
                "Erreur Réseau",
                "Le serveur est inaccessible ou a mis trop de temps à répondre.",
            )
        except requests.RequestException as error:
            QMessageBox.critical(self, "Erreur", str(error))

    def delete_referentiel(self, kind, item):
        identifiers = {
            "professeur": item["id_professeur"],
            "salle": item["id_salle"],
            "matiere": item["id_matiere"],
        }
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer cet élément ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            response = requests.delete(
                f"{API_BASE_URL}/{kind}/{identifiers[kind]}",
                timeout=API_TIMEOUT,
            )
            if response.status_code == 204:
                self.status.setText("Suppression effectuée.")
                global_signals.data_changed.emit()
                return
            if response.status_code == 409:
                QMessageBox.warning(
                    self,
                    "Suppression impossible",
                    "Cet élément est actuellement utilisé dans un cours ou un examen.",
                )
                return
            QMessageBox.warning(self, "Suppression impossible", response.text)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            QMessageBox.critical(
                self,
                "Erreur Réseau",
                "Le serveur est inaccessible ou a mis trop de temps à répondre.",
            )
        except requests.RequestException as error:
            QMessageBox.critical(self, "Erreur", str(error))

    def post(self, endpoint, payload, success):
        try:
            response = requests.post(
                f"{API_BASE_URL}/{endpoint}",
                json=payload,
                timeout=API_TIMEOUT,
            )
            if response.status_code in (200, 201):
                self.status.setText(success)
                self.status.setStyleSheet("color:#2ecc71;")
                global_signals.data_changed.emit()
                return True
            QMessageBox.warning(self, "Enregistrement impossible", response.text)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            QMessageBox.critical(
                self,
                "Erreur Réseau",
                "Le serveur est inaccessible ou a mis trop de temps à répondre.",
            )
        except requests.RequestException as error:
            QMessageBox.critical(self, "Connexion impossible", str(error))
        return False

    def save_professeur(self, nom, prenom, matricule):
        # WARN-09 : valider que le matricule est un entier avant d'envoyer
        matricule_val = matricule.text().strip()
        if not matricule_val.lstrip("-").isdigit():
            QMessageBox.warning(self, "Matricule invalide",
                                "Le matricule doit être un nombre entier.")
            return
        if self.post("professeur/create", {
            "nom_professeur":     nom.text().strip(),
            "prenom_professeur":  prenom.text().strip(),
            "matricule_professeur": int(matricule_val),
        }, "Professeur enregistré. Il est maintenant disponible dans les cours."):
            nom.clear(); prenom.clear(); matricule.clear()

    def save_name(self, field, kind, title):
        value = field.text().strip()
        if not value:
            QMessageBox.warning(self, "Champ obligatoire", f"Saisissez le nom de la {title.lower()}.")
            return
        if self.post(f"{kind}/create", {"nom": value}, f"{title} enregistré(e)."):
            field.clear()
