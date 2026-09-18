from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar, QGridLayout
from PyQt6.QtCore import Qt
from components.icon_loader import load_icon
from components.statCard import StatCard
import requests
from config import API_BASE_URL, API_TIMEOUT

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
        self.card_taux = StatCard("Taux", "--%", "#243447")
        self.card_absents = StatCard("Absents", "-- / --", "#e74c3c")
        self.card_retards = StatCard("Retards", "--", "#f39c12")
        kpi_layout.addWidget(self.card_taux)
        kpi_layout.addWidget(self.card_absents)
        kpi_layout.addWidget(self.card_retards)
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
        
        # Will be replaced by real data fetched from backend
        sections = []

        try:
            resp = requests.get(f"{API_BASE_URL}/stats/presence", timeout=API_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            total = data.get("total_eleves", 0)
            presents = data.get("presents", 0)
            absents = data.get("absents", max(total - presents, 0))
            retards = data.get("retards", 0)
            taux = data.get("taux_presence", 0.0)

            # Update KPI cards
            self.card_taux.set_value(f"{taux}%")
            self.card_absents.set_value(f"{absents} / {total}")
            self.card_retards.set_value(str(retards))

            # Single global section for now (per-room breakdown not implemented in API)
            sections.append(("Général", presents, total))
            # Fetch list of present students for display
            try:
                resp2 = requests.get(f"{API_BASE_URL}/stats/presence/presents", timeout=API_TIMEOUT)
                resp2.raise_for_status()
                present_list = resp2.json()
            except requests.RequestException:
                present_list = []

            # Display present students as a simple comma-separated line
            names = ", ".join([f"{s.get('Prenom_eleve','')} {s.get('Nom_eleve','')}" for s in present_list])
            present_label = QLabel(f"Présents: {names if names else '—'}")
            present_label.setStyleSheet("color: #243447; font-weight: 600;")
            presence_vbox.addWidget(present_label)
        except requests.RequestException:
            # Fall back to sample data on error
            sections = [
                ("Salle A (L3 ISAIA)", 24, 25),
                ("Salle B (L3 IT)", 18, 20),
                ("Amphithéâtre (L2)", 45, 50),
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
