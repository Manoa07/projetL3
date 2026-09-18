from PyQt6.QtCore import QDate, Qt, QTime
from PyQt6.QtWidgets import (
    QComboBox, QDateEdit, QLineEdit, QTimeEdit,
    QVBoxLayout, QLabel, QPushButton, QMessageBox, QWidget, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QScrollArea,
)
import requests
from config import API_BASE_URL, API_TIMEOUT
from components.icon_loader import load_icon
from components.theme import configure_table
from services.events import global_signals
from views.ajoutCoursView import make_time_edit   # réutilisation du même helper


class AjoutExamenView(QWidget):
    def __init__(self):
        super().__init__()
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(
            QLabel("<h2 style='color:#17212b;'>AJOUT EXAMEN</h2>"),
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        self.semestre = QLineEdit()
        self.semestre.setPlaceholderText("Semestre (ex: S1)")
        self.semestre.setMinimumWidth(400)
        self.semestre.setStyleSheet(
            "QLineEdit { padding: 12px; border: 1px solid #d8e0e8; "
            "border-radius: 10px; background: #ffffff; color: #17212b; }"
        )

        self.date = QDateEdit(QDate.currentDate())
        self.date.setCalendarPopup(True)
        self.date.setStyleSheet("""
            QDateEdit {
                padding: 10px;
                border: 1px solid #d8e0e8;
                border-radius: 10px;
                background: #ffffff;
                color: #17212b;
            }
            QCalendarWidget, QCalendarWidget QWidget,
            QCalendarWidget QTableView,
            QCalendarWidget QHeaderView::section {
                background: #ffffff;
                color: #17212b;
            }
            QCalendarWidget QTableView {
                selection-background-color: #243447;
                selection-color: #ffffff;
            }
            QCalendarWidget QToolButton {
                background: #ffffff;
                color: #17212b;
                border: none;
            }
        """)

        # QTimeEdit correctement configuré : flèches visibles, '--:--' par défaut
        self.debut = make_time_edit()
        self.fin   = make_time_edit()

        self.salle   = QComboBox()
        self.matiere = QComboBox()
        _combo_style = """
            QComboBox { padding: 10px; border: 1px solid #d8e0e8;
                        border-radius: 10px; background-color: #ffffff; color: #17212b; }
            QComboBox::drop-down { border: none; background-color: #ffffff; }
            QComboBox QAbstractItemView { background-color: #ffffff; color: #17212b;
                                          selection-background-color: #dfe5eb;
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
        self.btn_save = save
        save.setStyleSheet(
            """ 
              QPushButton { background: #243447; color: white; font-weight: 700; border-radius: 12px; padding: 6px 12px} 
              QPushButton:hover{ background-color: #1b2838;}
            """
        )
        save.setFixedSize(300, 40)
        layout.addWidget(save, alignment=Qt.AlignmentFlag.AlignCenter)

        refresh = QPushButton("Actualiser les salles et matières")
        refresh.setIcon(load_icon("refresh"))
        refresh.setStyleSheet(
            "QPushButton { background:#e8f0ff; color:#2459bd; font-weight:700; "
            "border:1px solid #bdd0f7; border-radius:10px; padding:8px 14px; }"
            "QPushButton:hover { background:#dbe7ff; }"
        )
        refresh.clicked.connect(self.load_references)
        layout.addWidget(refresh, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status = QLabel("Chargement des salles et matières…")
        self.status.setStyleSheet("color:#8b93a7; font-style:italic;")
        layout.addWidget(self.status, alignment=Qt.AlignmentFlag.AlignCenter)
        self.examens_table = QTableWidget(0, 8)
        self.examens_table.setHorizontalHeaderLabels(
            ["ID", "Date", "Heure de début", "Heure de fin", "Semestre",
             "Salle", "Matière", "Actions"]
        )
        configure_table(self.examens_table)
        layout.addWidget(self.examens_table)
        layout.addStretch()
        page.setMinimumWidth(700)
        scroll.setWidget(page)
        page_layout.addWidget(scroll)

        self.editing_examen_id = None
        self.load_references()
        self.load_examens()
        global_signals.data_changed.connect(self.load_references)
        global_signals.data_changed.connect(self.load_examens)

    def load_references(self):
        try:
            sr = requests.get(
                f"{API_BASE_URL}/salle/all",
                timeout=API_TIMEOUT,
            )
            mr = requests.get(
                f"{API_BASE_URL}/matiere/all",
                timeout=API_TIMEOUT,
            )
            sr.raise_for_status(); mr.raise_for_status()
            self.salle.clear();   self.salle.addItem("— Sélectionner —", None)
            self.matiere.clear(); self.matiere.addItem("— Sélectionner —", None)
            for item in sr.json():
                self.salle.addItem(item["nom_salle"], item["id_salle"])
            for item in mr.json():
                self.matiere.addItem(item["nom_matiere"], item["id_matiere"])
            self.status.setText("Salles et matières disponibles")
            self.status.setStyleSheet("color:#243447;")
        except (requests.RequestException, KeyError, TypeError):
            self.status.setText("Aucune donnée disponible — créez d'abord une salle et une matière")
            self.status.setStyleSheet("color:#f39c12;")

    def _reference_label(self, field, identifier):
        index = field.findData(identifier)
        return field.itemText(index) if index >= 0 else str(identifier or "")

    def load_examens(self):
        try:
            response = requests.get(
                f"{API_BASE_URL}/examen/all",
                timeout=API_TIMEOUT,
            )
            response.raise_for_status()
            self.examens_table.setRowCount(0)
            for row, item in enumerate(response.json()):
                self.examens_table.insertRow(row)
                values = (
                    item.get("id_examen", ""),
                    str(item.get("date_examen", ""))[:10],
                    item.get("Heure_debut", ""),
                    item.get("Heure_fin", ""),
                    item.get("semestre_examen", ""),
                    self._reference_label(
                        self.salle, item.get("id_salle_salle")
                    ),
                    self._reference_label(
                        self.matiere, item.get("id_matiere_matiere")
                    ),
                )
                for column, value in enumerate(values):
                    self.examens_table.setItem(
                        row, column, QTableWidgetItem(str(value))
                    )
                actions = QWidget()
                actions_layout = QHBoxLayout(actions)
                actions_layout.setContentsMargins(2, 2, 2, 2)
                update_button = QPushButton("Modifier")
                delete_button = QPushButton("Supprimer")
                update_button.clicked.connect(
                    lambda checked=False, current=item: self.update_examen(current)
                )
                delete_button.clicked.connect(
                    lambda checked=False, current=item: self.delete_examen(current)
                )
                actions_layout.addWidget(update_button)
                actions_layout.addWidget(delete_button)
                self.examens_table.setCellWidget(row, 7, actions)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            self.status.setText("Impossible de charger les examens.")
            self.status.setStyleSheet("color:#f39c12;")
        except (requests.RequestException, KeyError, TypeError, ValueError):
            self.status.setText("Réponse invalide du serveur.")
            self.status.setStyleSheet("color:#f39c12;")

    def update_examen(self, item):
        self.editing_examen_id = item.get("id_examen")
        self.semestre.setText(item.get("semestre_examen") or "")
        date_value = str(item.get("date_examen", ""))[:10]
        parsed_date = QDate.fromString(date_value, "yyyy-MM-dd")
        if parsed_date.isValid():
            self.date.setDate(parsed_date)
        for field, key in (
            (self.debut, "Heure_debut"),
            (self.fin, "Heure_fin"),
        ):
            parsed_time = QTime.fromString(str(item.get(key) or "")[:8], "HH:mm:ss")
            if parsed_time.isValid():
                field.setTime(parsed_time)
        for field, key in (
            (self.salle, "id_salle_salle"),
            (self.matiere, "id_matiere_matiere"),
        ):
            index = field.findData(item.get(key))
            if index >= 0:
                field.setCurrentIndex(index)
        self.btn_save.setText("MODIFIER L'EXAMEN")
        self.status.setText("Modification en cours : validez avec le bouton ci-dessus.")

    def delete_examen(self, item):
        examen_id = item.get("id_examen")
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer cet examen ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            response = requests.delete(
                f"{API_BASE_URL}/examen/{examen_id}",
                timeout=API_TIMEOUT,
            )
            if response.status_code == 204:
                QMessageBox.information(self, "Succès", "Examen supprimé avec succès.")
                global_signals.data_changed.emit()
            elif response.status_code == 409:
                QMessageBox.warning(
                    self, "Suppression impossible",
                    "Cet examen possède des surveillances ou présences associées.",
                )
            elif response.status_code == 404:
                QMessageBox.warning(self, "Introuvable", "Cet examen n'existe plus.")
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
            method = requests.put if self.editing_examen_id else requests.post
            endpoint = (
                f"{API_BASE_URL}/examen/{self.editing_examen_id}"
                if self.editing_examen_id
                else f"{API_BASE_URL}/examen/create"
            )
            response = method(
                endpoint,
                json=data,
                timeout=API_TIMEOUT,
            )
            if response.status_code in (200, 201):
                message = (
                    "Examen modifié avec succès."
                    if self.editing_examen_id
                    else "Examen ajouté avec succès."
                )
                QMessageBox.information(self, "Succès", message)
                self.editing_examen_id = None
                self.btn_save.setText("ENREGISTRER L'EXAMEN")
                self.semestre.clear()
                # Remettre '--:--' (QTime() invalide)
                self.debut.setTime(QTime())
                self.fin.setTime(QTime())
                global_signals.data_changed.emit()
            elif response.status_code == 404:
                QMessageBox.warning(self, "Introuvable", response.text)
            elif response.status_code == 409:
                QMessageBox.warning(self, "Conflit", response.text)
            else:
                QMessageBox.warning(self, "Erreur", response.text)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            QMessageBox.critical(
                self,
                "Erreur Réseau",
                "Le serveur est inaccessible ou a mis trop de temps à répondre.",
            )
        except requests.RequestException as error:
            QMessageBox.critical(self, "Erreur", f"Connexion serveur échouée : {error}")
