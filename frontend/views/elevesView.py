<<<<<<< Updated upstream
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget,QPushButton,QTableWidgetItem, QHeaderView

from PyQt6.QtCore import QTimer, Qt
import httpx
=======
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QPushButton,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox,
    QDialog, QDialogButtonBox, QInputDialog
)

from PyQt6.QtCore import QTimer, Qt
import httpx
from config import API_BASE_URL, API_TIMEOUT
>>>>>>> Stashed changes
import asyncio
from components.icon_loader import load_icon
from components.theme import NAV_BUTTON_STYLE
from services.events import global_signals # Importation du bus d'événements
class ElevesView(QWidget):
    def __init__(self):
        
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        self.refresh_button = QPushButton("Rafraîchir")
        self.refresh_button.setIcon(load_icon("chart"))
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2e9d68;
                color: white;
                padding: 10px 14px;
                border-radius: 12px;
                font-weight: 700;
                }
            QPushButton:hover {
                background-color: #247a50;
            }
    """)
        self.refresh_button.clicked.connect(self.refresh_data)

        layout.addWidget(self.refresh_button)        

        # Titre de la section
        self.title_label = QLabel("<b style='color:#17212b; font-size:18px; letter-spacing: 1.4px;'>ÉLÈVES</b>")
        layout.addWidget(self.title_label)
        
        # Configuration du tableau
<<<<<<< Updated upstream
        self.table = QTableWidget(0, 3) # Commence avec 0 ligne
        self.table.setHorizontalHeaderLabels(["N°", "Nom et Prénoms", "Classe"])
=======
        self.table = QTableWidget(0, 4) # Commence avec 0 ligne
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setHorizontalHeaderLabels(
            ["N°", "Nom et Prénoms", "Classe", "Actions"]
        )
>>>>>>> Stashed changes
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                color: #17212b;
                gridline-color: #e4e9ef;
                border: 1px solid #e4e9ef;
                border-radius: 14px;
            }
            QHeaderView::section {
                background-color: #fff5f2;
                color: #247a50;
                padding: 10px;
                border: 1px solid #e4e9ef;
                font-weight: 700;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # --- CONNEXION AU SIGNAL GLOBAL ---
        # Dès que global_signals.data_changed est émis, on rafraîchit la liste
        global_signals.data_changed.connect(self.refresh_data)
        
        # Premier chargement au lancement
        QTimer.singleShot(0, self.refresh_data)
    
    def refresh_data(self):
        """Lance la tâche asynchrone de récupération des données"""
        async def safe_load():
            try:
                self.refresh_button.setEnabled(False)  # Désactive le bouton pendant le chargement
                await self.load_eleve()
            except Exception as error:
                print("Erreur lors du rafraîchissement :", error)
            finally:
                self.refresh_button.setEnabled(True)  # Réactive le bouton une fois le chargement terminé
        asyncio.create_task(safe_load())
    
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
            actions_layout.setSpacing(4)
            actions_layout.addWidget(history_button)
            actions_layout.addWidget(update_button)
            actions_layout.addWidget(delete_button)
            self.table.setCellWidget(i, 3, actions)

        self.table.setColumnWidth(3, 310)

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
        asyncio.create_task(self.load_history(eleve_id, eleve))

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
        numero, accepted = QInputDialog.getInt(
            self, "Modifier l'élève", "Numéro :",
            value=int(eleve.get("Numero_eleve", 0)),
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
        asyncio.create_task(
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
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer cet élève ? "
            "La suppression est interdite s'il possède un historique.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            asyncio.create_task(self._send_eleve_delete(eleve_id))

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
        layout = QVBoxLayout(dialog)
        table = QTableWidget(len(history), 3, dialog)
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
