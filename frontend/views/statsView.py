from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar, QGridLayout
from PyQt6.QtCore import Qt
from components.icon_loader import load_icon
from components.statCard import StatCard

class StatsView(QWidget):
    def __init__(self):
        super().__init__()
        # Mise en page principale de la vue Statistiques
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        
        # Titre de la section basé sur les objectifs du projet 
        title = QLabel("<b style='color:#17212b; font-size:18px; letter-spacing: 1px;'>SUIVI DES PRÉSENCES</b>")
        layout.addWidget(title)
        
        # 1. Cartes de statistiques (KPI) pour une lecture rapide 
        kpi_layout = QHBoxLayout()
        # Taux de présence global calculé par l'IA 
        kpi_layout.addWidget(StatCard("Taux", "96%", "#243447"))
        # Nombre d'élèves absents détectés 
        kpi_layout.addWidget(StatCard("Absents", "1 / 25", "#e74c3c"))
        # Retardataires identifiés après l'horaire précis [cite: 8]
        kpi_layout.addWidget(StatCard("Retards", "2", "#f39c12"))
        layout.addLayout(kpi_layout)

        # 2. Section détaillée par salle/classe 
        presence_frame = QFrame()
        presence_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e4e9ef;
                border-radius: 14px;
                padding: 20px;
            }
            QLabel { border: none; background: none; }
        """)
        presence_vbox = QVBoxLayout(presence_frame)
        presence_vbox.setContentsMargins(6, 6, 6, 6)
        presence_vbox.setSpacing(14)
        section_title = QLabel("Présences par section")
        section_title.setStyleSheet("color: #17212b; font-weight: 700;")
        presence_vbox.addWidget(section_title)
        
        # Simulation de données pour différentes sections de l'ISPM [cite: 19, 23]
        sections = [
            ("Salle A (L3 ISAIA)", 24, 25), 
            ("Salle B (L3 IT)", 18, 20), 
            ("Amphithéâtre (L2)", 45, 50)
        ]
        
        for salle, count, total in sections:
            row = QHBoxLayout()
            row.setSpacing(12)
            row.addWidget(QLabel(salle))
            
            # Barre de progression pour visualiser le taux de présence 
            bar = QProgressBar()
            bar.setValue(int((count/total)*100))
            bar.setFormat(f"{count}/{total} présents")
            bar.setStyleSheet("""
                QProgressBar { 
                    background: #edf1f5;
                    border-radius: 7px; 
                    height: 16px; 
                    border: none; 
                    text-align: center; 
                    color: white;
                    font-size: 10px;
                } 
                QProgressBar::chunk { 
                    background: #243447;
                    border-radius: 7px; 
                }
            """)
            row.addWidget(bar)
            presence_vbox.addLayout(row)
        
        layout.addWidget(presence_frame)
        
        # 3. Information sur le prochain contrôle (Contre-présence) [cite: 10]
        # Rappel de la fonctionnalité d'horaire précis (ex: toutes les 30min) [cite: 8, 10]
        info_row = QHBoxLayout()
        info_icon = QLabel()
        info_icon.setPixmap(load_icon("info").pixmap(16, 16))
        info_row.addWidget(info_icon)

        info_label = QLabel("Prochain contrôle : dans 20 minutes")
        info_label.setStyleSheet("color: #7a7c8c; font-style: italic;")
        info_row.addWidget(info_label)
        info_row.addStretch()
        layout.addLayout(info_row)
        
        # Espace flexible pour pousser le contenu vers le haut
        layout.addStretch()
