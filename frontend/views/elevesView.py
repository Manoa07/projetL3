from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
import httpx
import asyncio
from qasync import QEventLoop
from PyQt6.QtCore import QTimer
class ElevesView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b style='color:#4facfe; font-size:18px;'>LISTE DES ÉLÈVES - ISAIA L3</b>"))
        
        self.table = QTableWidget(4, 3)
        self.table.setHorizontalHeaderLabels(["N°", "Nom et Prénoms", "Statut Identification"])
        self.table.setStyleSheet("background-color: #1a1c2e; color: white;")
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        QTimer.singleShot(0, self.start_async)
    
    def start_async(self):
        asyncio.create_task(self.load_eleve())
    
    async def load_eleve(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://127.0.0.1:8000/eleve/all")
                print(response)

                if response.status_code == 200:
                    eleves = response.json()
                    self.populate_table(eleves)
        except Exception as e:
            print("erreur :",e)            

    def populate_table(self, eleves):
        self.table.setRowCount(len(eleves))

        for i, e in enumerate(eleves):
            self.table.setItem(i,0, QTableWidgetItem(str(e["Numero_eleve"])))
            self.table.setItem(i,1, QTableWidgetItem(f"{e['Nom_eleve']} {e['Prenom_eleve']}"))
            self.table.setItem(i,2, QTableWidgetItem(e["Classe_eleve"]))
       
       