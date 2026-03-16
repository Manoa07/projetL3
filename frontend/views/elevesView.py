from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView

class ElevesView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b style='color:#4facfe; font-size:18px;'>LISTE DES ÉLÈVES - ISAIA L3</b>"))
        
        self.table = QTableWidget(4, 3)
        self.table.setHorizontalHeaderLabels(["N°", "Nom et Prénoms", "Statut Identification"])
        self.table.setStyleSheet("background-color: #1a1c2e; color: white;")
        
        membres = [
            ("14", "RANDRIAMALALARISOA Ianto", "Identifié"),
            ("15", "ANDRIAHERISOLO Fanambiniaina", "Identifié"),
            ("19", "RAVELONJOHANISON Hajatiana", "Identifié"),
            ("22", "RASAMIARIMANANA Andrianary", "Identifié")
        ]
        
        for i, (n, nom, s) in enumerate(membres):
            self.table.setItem(i, 0, QTableWidgetItem(n))
            self.table.setItem(i, 1, QTableWidgetItem(nom))
            self.table.setItem(i, 2, QTableWidgetItem(s))
            
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)