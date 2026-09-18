from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar, QGridLayout
from PyQt6.QtCore import Qt
from components.icon_loader import load_icon
from components.statCard import StatCard
import requests
from config import API_BASE_URL, API_TIMEOUT
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from PyQt6.QtGui import QPixmap

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
        # Chart label will display the presence/retards timeseries above lists
        chart_label = QLabel()
        chart_label.setFixedHeight(180)
        presence_vbox.addWidget(chart_label)
        
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
            # Fetch timeseries for last 7 days and render chart
            try:
                resp3 = requests.get(f"{API_BASE_URL}/stats/presence/timeseries?days=7", timeout=API_TIMEOUT)
                resp3.raise_for_status()
                timeseries = resp3.json()
            except requests.RequestException:
                timeseries = []

            # Draw chart if we have data
            if timeseries:
                dates = [t.get('date') for t in timeseries]
                presents_series = [t.get('presents', 0) for t in timeseries]
                retards_series = [t.get('retards', 0) for t in timeseries]
                plt.figure(figsize=(6, 2.2), dpi=100)
                plt.plot(dates, presents_series, marker='o', label='Présents')
                plt.plot(dates, retards_series, marker='o', label='Retards')
                plt.fill_between(dates, presents_series, alpha=0.1)
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.legend()
                buf = io.BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight')
                plt.close()
                buf.seek(0)
                pix = QPixmap()
                pix.loadFromData(buf.getvalue(), 'PNG')
                chart_label.setPixmap(pix.scaled(chart_label.width(), chart_label.height()))

            # Display present students as a simple comma-separated line
            names = ", ".join([f"{s.get('Prenom_eleve','')} {s.get('Nom_eleve','')}" for s in present_list])

            # Fetch retards list
            try:
                resp4 = requests.get(f"{API_BASE_URL}/stats/presence/retards", timeout=API_TIMEOUT)
                resp4.raise_for_status()
                retards_list = resp4.json()
            except requests.RequestException:
                retards_list = []

            names_retards = ", ".join([f"{s.get('Prenom_eleve','')} {s.get('Nom_eleve','')}" for s in retards_list])

            # Lists area: presents on left, retards on right
            lists_row = QHBoxLayout()
            presents_col = QVBoxLayout()
            presents_col.addWidget(QLabel("<b>Présents</b>"))
            presents_text = QLabel(names if names else '—')
            presents_text.setWordWrap(True)
            presents_col.addWidget(presents_text)

            retards_col = QVBoxLayout()
            retards_col.addWidget(QLabel("<b>Retards</b>"))
            retards_text = QLabel(names_retards if names_retards else '—')
            retards_text.setWordWrap(True)
            retards_col.addWidget(retards_text)

            lists_row.addLayout(presents_col)
            lists_row.addLayout(retards_col)
            presence_vbox.addLayout(lists_row)
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
