from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget,QPushButton,QTableWidgetItem, QHeaderView

from PyQt6.QtCore import QTimer, Qt
import httpx
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
                background-color: #4facfe;
                color: white;
                padding: 10px 14px;
                border-radius: 12px;
                font-weight: 700;
                }
            QPushButton:hover {
                background-color: #3a8edb;
            }
    """)
        self.refresh_button.clicked.connect(self.refresh_data)

        layout.addWidget(self.refresh_button)        

        # Titre de la section
        self.title_label = QLabel("<b style='color:#f4f7fb; font-size:18px; letter-spacing: 1.4px;'>ÉLÈVES</b>")
        layout.addWidget(self.title_label)
        
        # Configuration du tableau
        self.table = QTableWidget(0, 3) # Commence avec 0 ligne
        self.table.setHorizontalHeaderLabels(["N°", "Nom et Prénoms", "Classe"])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #151826;
                color: white;
                gridline-color: #23283d;
                border: 1px solid #23283d;
                border-radius: 14px;
            }
            QHeaderView::section {
                background-color: #1a1f2f;
                color: #4facfe;
                padding: 10px;
                border: 1px solid #23283d;
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
            async with httpx.AsyncClient() as client:
                # Appel à votre backend local
                response = await client.get("http://127.0.0.1:8000/eleve/all")
                
                if response.status_code == 200:
                    eleves = response.json()
                    self.populate_table(eleves)
                else:
                    print(f"Erreur API : {response.status_code}")
        except Exception as e:
            print("Erreur de connexion :", e)            

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
            
        print(f"Tableau mis à jour : {len(eleves)} élèves affichés.")
