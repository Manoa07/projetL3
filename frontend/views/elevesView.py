from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QPushButton,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox,
    QDialog, QDialogButtonBox, QInputDialog
)

from PyQt6.QtCore import QTimer, Qt
import httpx
from config import API_BASE_URL, API_TIMEOUT
import asyncio
from components.icon_loader import load_icon
from components.theme import NAV_BUTTON_STYLE
from components.theme import configure_dialog, configure_table
from services.events import global_signals # Importation du bus d'événements


def safe_int(value, default=0):
    """Convertit une valeur en int sans faire planter l’interface."""
    try:
        if value in (None, ""):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def schedule_async_task(coro):
    """Planifie une coroutine dans le bon contexte Qt/asyncio."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(coro)
        return

    loop.create_task(coro)


class ElevesView(QWidget):
    def __init__(self):
        
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 24, 24, 24)
        layout.setSpacing(14)
        header = QHBoxLayout()
        heading = QVBoxLayout()
        heading.setSpacing(3)
        self.title_label = QLabel("ÉLÈVES")
        self.title_label.setStyleSheet(
            "color:#17212b; font-size:22px; font-weight:800; letter-spacing:0.5px;"
        )
        heading.addWidget(self.title_label)
        subtitle = QLabel("Gérez les inscriptions et consultez l'historique de présence.")
        subtitle.setStyleSheet("color:#718096; font-size:11px;")
        heading.addWidget(subtitle)
        header.addLayout(heading)
        header.addStretch()
        self.count_label = QLabel("0 élève")
        self.count_label.setStyleSheet(
            "color:#2459bd; background:#e8f0ff; border:1px solid #bdd0f7; "
            "border-radius:12px; padding:7px 12px; font-weight:700;"
        )
        header.addWidget(self.count_label)
        self.refresh_button = QPushButton("Rafraîchir")
        self.refresh_button.setIcon(load_icon("refresh"))
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #e8f0ff;
                color: #2459bd;
                border: 1px solid #bdd0f7;
                padding: 8px 14px;
                border-radius: 10px;
                font-weight: 700;
                }
            QPushButton:hover {
                background-color: #dbe7ff;
            }
    """)
        self.refresh_button.clicked.connect(self.refresh_data)
        header.addWidget(self.refresh_button)
        layout.addLayout(header)
        
        # Configuration du tableau
        self.table = QTableWidget(0, 4) # Commence avec 0 ligne
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setHorizontalHeaderLabels(
            ["N°", "Nom et prénom", "Classe", "Actions"]
        )
        configure_table(self.table)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                color: #17212b;
                gridline-color: #e4e9ef;
                border: 1px solid #e4e9ef;
                border-radius: 14px;
            }
            QHeaderView::section {
                background-color: #e8f0ff;
                color: #2459bd;
                padding: 10px;
                border: 1px solid #d6e2f7;
                font-weight: 700;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # reserve space for action buttons to avoid truncation
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 420)
        self.table.verticalHeader().setDefaultSectionSize(42)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)
        self.empty_label = QLabel("Aucun élève enregistré pour le moment.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(
            "color:#718096; background:#f6f8fb; border:1px dashed #d8e0e8; "
            "border-radius:10px; padding:12px; font-style:italic;"
        )
        self.empty_label.setVisible(True)
        layout.addWidget(self.empty_label)

        # --- CONNEXION AU SIGNAL GLOBAL ---
        # Dès que global_signals.data_changed est émis, on rafraîchit la liste
        global_signals.data_changed.connect(self.refresh_data)
        
        # Premier chargement au lancement
        QTimer.singleShot(0, self.refresh_data)
    
    def refresh_data(self):
        """Lance la tâche asynchrone de récupération des données."""
        async def safe_load():
            try:
                if hasattr(self, 'refresh_button'):
                    self.refresh_button.setEnabled(False)
                await self.load_eleve()
            except Exception as error:
                print("Erreur lors du rafraîchissement :", error)
            finally:
                if hasattr(self, 'refresh_button'):
                    self.refresh_button.setEnabled(True)

        schedule_async_task(safe_load())
    
    async def load_eleve(self):
        """Récupère les élèves depuis l'API FastAPI"""
        try:
            timeout = httpx.Timeout(
                API_TIMEOUT[1],
                connect=API_TIMEOUT[0],
            )
            async with httpx.AsyncClient(timeout=timeout) as client:
                # Appel à votre backend local
                response = await client.get("http://127.0.0.1:8000/eleve/all")
                
                if response.status_code == 200:
                    eleves = response.json()
                    self.populate_table(eleves)
                else:
                    QMessageBox.warning(
                        self,
                        "Erreur",
                        f"Impossible de charger les élèves ({response.status_code}).",
                    )
        except (httpx.TimeoutException, httpx.NetworkError):
            QMessageBox.critical(
                self,
                "Erreur réseau",
                "Le serveur est inaccessible ou a mis trop de temps à répondre.",
            )
        except httpx.HTTPError as error:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Connexion serveur échouée : {error}",
            )

    def populate_table(self, eleves):
        """Remplit le tableau avec les données reçues"""
        self.table.setRowCount(len(eleves))
        count = len(eleves)
        self.count_label.setText(f"{count} élève" if count == 1 else f"{count} élèves")
        self.empty_label.setVisible(not eleves)

        for i, e in enumerate(eleves):
            # Colonne Numéro
            self.table.setItem(i, 0, QTableWidgetItem(str(e.get("Numero_eleve", ""))))
            
            # Colonne Nom et Prénom
            nom_complet = f"{e.get('Nom_eleve', '')} {e.get('Prenom_eleve', '')}"
            self.table.setItem(i, 1, QTableWidgetItem(nom_complet.upper()))
            
            # Colonne Classe
            self.table.setItem(i, 2, QTableWidgetItem(e.get("Classe_eleve", "")))

            history_button = QPushButton("Historique")
            history_button.clicked.connect(
                lambda checked=False, eleve=e: self.show_history(eleve)
            )
            update_button = QPushButton("Modifier")
            update_button.clicked.connect(
                lambda checked=False, eleve=e: self.update_eleve(eleve)
            )
            delete_button = QPushButton("Supprimer")
            delete_button.clicked.connect(
                lambda checked=False, eleve=e: self.delete_eleve(eleve)
            )
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(6)
            for button in (history_button, update_button, delete_button):
                button.setMinimumHeight(30)
                button.setCursor(Qt.CursorShape.PointingHandCursor)
                button.setMinimumWidth(80)
            history_button.setStyleSheet(
                "QPushButton { background:#eef4ff; color:#2459bd; border:1px solid #bdd0f7; "
                "border-radius:7px; padding:4px 8px; font-weight:700; }"
                "QPushButton:hover { background:#dbe7ff; }"
            )
            update_button.setStyleSheet(
                "QPushButton { background:#f6f8fb; color:#4b5563; border:1px solid #d8e0e8; "
                "border-radius:7px; padding:4px 8px; font-weight:700; }"
                "QPushButton:hover { background:#e9eef5; }"
            )
            delete_button.setStyleSheet(
                "QPushButton { background:#fff1ef; color:#b42318; border:1px solid #f3c7c2; "
                "border-radius:7px; padding:4px 8px; font-weight:700; }"
                "QPushButton:hover { background:#ffe1dd; }"
            )
            actions_layout.addWidget(history_button)
            actions_layout.addWidget(update_button)
            actions_layout.addWidget(delete_button)
            self.table.setCellWidget(i, 3, actions)

        self.table.setColumnWidth(3, 360)

    def show_history(self, eleve):
        """Affiche l'historique de présence de l'élève sélectionné."""
        eleve_id = eleve.get("Id_eleve")
        if not eleve_id:
            QMessageBox.warning(
                self,
                "Historique indisponible",
                "L'identifiant de cet élève est introuvable.",
            )
            return
        schedule_async_task(self.load_history(eleve_id, eleve))

    def update_eleve(self, eleve):
        """Demande les informations administratives avant la mise à jour."""
        nom, accepted = QInputDialog.getText(
            self, "Modifier l'élève", "Nom :", text=eleve.get("Nom_eleve", "")
        )
        if not accepted:
            return
        prenom, accepted = QInputDialog.getText(
            self, "Modifier l'élève", "Prénom :",
            text=eleve.get("Prenom_eleve", ""),
        )
        if not accepted:
            return
        classe, accepted = QInputDialog.getText(
            self, "Modifier l'élève", "Classe :",
            text=eleve.get("Classe_eleve", ""),
        )
        if not accepted:
            return
        numero_value = safe_int(eleve.get("Numero_eleve"), 1)
        numero, accepted = QInputDialog.getInt(
            self, "Modifier l'élève", "Numéro :",
            value=max(1, numero_value),
            min=1,
        )
        if not accepted:
            return
        matricule, accepted = QInputDialog.getText(
            self, "Modifier l'élève", "Matricule (facultatif) :",
            text="" if eleve.get("matricule_eleve") is None
            else str(eleve.get("matricule_eleve")),
        )
        if not accepted:
            return
        if not nom.strip() or not prenom.strip() or not classe.strip():
            QMessageBox.warning(
                self, "Erreur",
                "Le nom, le prénom et la classe sont obligatoires.",
            )
            return
        if matricule.strip() and not matricule.strip().isdigit():
            QMessageBox.warning(
                self, "Erreur",
                "Le matricule doit être un nombre ou rester vide.",
            )
            return
        payload = {
            "Nom_eleve": nom.strip(),
            "Prenom_eleve": prenom.strip(),
            "Classe_eleve": classe.strip(),
            "Numero_eleve": numero,
            "matricule_eleve": (
                int(matricule.strip()) if matricule.strip() else None
            ),
        }
        schedule_async_task(
            self._send_eleve_update(eleve.get("Id_eleve"), payload)
        )

    async def _send_eleve_update(self, eleve_id, payload):
        timeout = httpx.Timeout(
            API_TIMEOUT[1],
            connect=API_TIMEOUT[0],
        )
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.put(
                    f"{API_BASE_URL}/eleve/{eleve_id}",
                    json=payload,
                )
            if response.status_code == 200:
                QMessageBox.information(
                    self, "Succès", "Élève modifié avec succès."
                )
                global_signals.data_changed.emit()
            elif response.status_code == 409:
                QMessageBox.warning(
                    self, "Conflit",
                    "Un élève avec ces informations existe déjà.",
                )
            elif response.status_code == 404:
                QMessageBox.warning(self, "Introuvable", "Élève introuvable.")
            else:
                QMessageBox.warning(self, "Erreur", response.text)
        except (httpx.TimeoutException, httpx.NetworkError):
            QMessageBox.critical(
                self, "Erreur réseau",
                "Le serveur est inaccessible ou a mis trop de temps à répondre.",
            )
        except httpx.HTTPError as error:
            QMessageBox.critical(
                self, "Erreur",
                f"Connexion serveur échouée : {error}",
            )

    def delete_eleve(self, eleve):
        """Demande confirmation avant la suppression physique protégée."""
        eleve_id = eleve.get("Id_eleve")
        if eleve_id is None:
            QMessageBox.warning(
                self,
                "Suppression impossible",
                "Identifiant de l’élève introuvable.",
            )
            return
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer cet élève et toutes ses données associées ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            schedule_async_task(self._send_eleve_delete(eleve_id))

    async def _send_eleve_delete(self, eleve_id):
        timeout = httpx.Timeout(
            API_TIMEOUT[1],
            connect=API_TIMEOUT[0],
        )
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.delete(
                    f"{API_BASE_URL}/eleve/{eleve_id}"
                )
            if response.status_code == 204:
                QMessageBox.information(
                    self, "Succès", "Élève supprimé avec succès."
                )
                global_signals.data_changed.emit()
            elif response.status_code == 409:
                try:
                    detail = response.json().get("detail")
                except ValueError:
                    detail = None
                QMessageBox.warning(
                    self,
                    "Suppression impossible",
                    detail or (
                        "Cet élève possède un historique et ne peut pas "
                        "être supprimé."
                    ),
                )
            elif response.status_code == 404:
                QMessageBox.warning(self, "Introuvable", "Élève introuvable.")
            else:
                QMessageBox.warning(self, "Erreur", response.text)
        except (httpx.TimeoutException, httpx.NetworkError):
            QMessageBox.critical(
                self, "Erreur réseau",
                "Le serveur est inaccessible ou a mis trop de temps à répondre.",
            )
        except httpx.HTTPError as error:
            QMessageBox.critical(
                self, "Erreur",
                f"Connexion serveur échouée : {error}",
            )

    async def load_history(self, eleve_id, eleve):
        timeout = httpx.Timeout(
            API_TIMEOUT[1],
            connect=API_TIMEOUT[0],
        )
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    f"{API_BASE_URL}/presence/eleve/{eleve_id}"
                )
            if response.status_code == 404:
                QMessageBox.information(
                    self,
                    "Historique",
                    "Aucune présence enregistrée pour cet élève.",
                )
                return
            if response.status_code != 200:
                QMessageBox.warning(
                    self,
                    "Erreur",
                    f"Impossible de charger l'historique ({response.status_code}).",
                )
                return
            self.display_history(eleve, response.json())
        except (httpx.TimeoutException, httpx.NetworkError):
            QMessageBox.critical(
                self,
                "Erreur réseau",
                "Le serveur est inaccessible ou a mis trop de temps à répondre.",
            )
        except httpx.HTTPError as error:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Connexion serveur échouée : {error}",
            )

    def display_history(self, eleve, history):
        dialog = QDialog(self)
        dialog.setWindowTitle(
            f"Historique - {eleve.get('Nom_eleve', '')} "
            f"{eleve.get('Prenom_eleve', '')}"
        )
        dialog.resize(620, 420)
        configure_dialog(dialog)
        layout = QVBoxLayout(dialog)
        table = QTableWidget(len(history), 3, dialog)
        configure_table(table)
        table.setHorizontalHeaderLabels(["Date", "Heure", "Statut"])
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        for row, presence in enumerate(history):
            table.setItem(
                row, 0, QTableWidgetItem(str(presence.get("Date_presence", "")))
            )
            table.setItem(
                row, 1, QTableWidgetItem(str(presence.get("Heure_presence", "")))
            )
            table.setItem(
                row, 2, QTableWidgetItem(
                    str(presence.get("Status_presence", ""))
                )
            )
        layout.addWidget(table)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()
