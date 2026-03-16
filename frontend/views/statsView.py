from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar, QGridLayout
from PyQt6.QtCore import Qt
from components.statCard import StatCard

class StatsView(QWidget):
    def __init__(self):
        super().__init__()
        # Mise en page principale de la vue Statistiques
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre de la section basé sur les objectifs du projet 
        title = QLabel("<b style='color:#4facfe; font-size:18px;'>SUIVI PRÉSENTIEL AUTOMATISÉ</b>")
        layout.addWidget(title)
        
        # 1. Cartes de statistiques (KPI) pour une lecture rapide 
        kpi_layout = QHBoxLayout()
        # Taux de présence global calculé par l'IA 
        kpi_layout.addWidget(StatCard("Taux de Remplissage", "96%", "#2ecc71"))
        # Nombre d'élèves absents détectés 
        kpi_layout.addWidget(StatCard("Absents", "1 / 25", "#e74c3c"))
        # Retardataires identifiés après l'horaire précis [cite: 8]
        kpi_layout.addWidget(StatCard("Retardataires", "2", "#f39c12"))
        layout.addLayout(kpi_layout)

        # 2. Section détaillée par salle/classe 
        presence_frame = QFrame()
        presence_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1c2e; 
                border-radius: 10px; 
                padding: 20px;
            }
            QLabel { border: none; background: none; }
        """)
        presence_vbox = QVBoxLayout(presence_frame)
        presence_vbox.addWidget(QLabel("<b>Statistiques de présence par section (Temps Réel)</b>"))
        
        # Simulation de données pour différentes sections de l'ISPM [cite: 19, 23]
        sections = [
            ("Salle A (L3 ISAIA)", 24, 25), 
            ("Salle B (L3 IT)", 18, 20), 
            ("Amphithéâtre (L2)", 45, 50)
        ]
        
        for salle, count, total in sections:
            row = QHBoxLayout()
            row.addWidget(QLabel(salle))
            
            # Barre de progression pour visualiser le taux de présence 
            bar = QProgressBar()
            bar.setValue(int((count/total)*100))
            bar.setFormat(f"{count}/{total} présents")
            bar.setStyleSheet("""
                QProgressBar { 
                    background: #2d2f41; 
                    border-radius: 5px; 
                    height: 15px; 
                    border: none; 
                    text-align: center; 
                    color: white;
                    font-size: 10px;
                } 
                QProgressBar::chunk { 
                    background: #2ecc71; 
                    border-radius: 5px; 
                }
            """)
            row.addWidget(bar)
            presence_vbox.addLayout(row)
        
        layout.addWidget(presence_frame)
        
        # 3. Information sur le prochain contrôle (Contre-présence) [cite: 10]
        # Rappel de la fonctionnalité d'horaire précis (ex: toutes les 30min) [cite: 8, 10]
        info_label = QLabel("ℹ️ Prochain contrôle automatique (Contre-présence) : dans 20 minutes")
        info_label.setStyleSheet("color: #7a7c8c; font-style: italic; margin-top: 10px;")
        layout.addWidget(info_label)
        
        # Espace flexible pour pousser le contenu vers le haut
        layout.addStretch()