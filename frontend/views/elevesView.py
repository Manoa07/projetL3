from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView

from PyQt6.QtCore import QTimer, Qt
import httpx
import asyncio
from services.events import global_signals # Importation du bus d'événements
class ElevesView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Titre de la section
        self.title_label = QLabel("<b style='color:#4facfe; font-size:18px;'>LISTE DES ÉLÈVES - ISAIA L3</b>")
        layout.addWidget(self.title_label)
        
        # Configuration du tableau
        self.table = QTableWidget(0, 3) # Commence avec 0 ligne
        self.table.setHorizontalHeaderLabels(["N°", "Nom et Prénoms", "Classe"])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1c2e; 
                color: white;
                gridline-color: #2d2f41;
                border: none;
            }
            QHeaderView::section {
                background-color: #24273d;
                color: #4facfe;
                padding: 5px;
                border: 1px solid #2d2f41;
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
        asyncio.create_task(self.load_eleve())
    
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

