from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar, QGridLayout, QTableWidget, QTableWidgetItem
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
from components.theme import configure_table

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
        # Chart label will display the presence/retards timeseries
        chart_label = QLabel()
        chart_label.setFixedHeight(180)
        presence_vbox.addWidget(chart_label)

        # 2.a Résumé statistique pour cette section (valeurs stylées)
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        def make_stat_widget(title, value="—"):
            w = QLabel()
            w.setAlignment(Qt.AlignmentFlag.AlignCenter)
            w.setFixedHeight(64)
            w.setStyleSheet(
                "background:#f6f8fb; border-radius:10px; padding:8px; color:#243447;"
            )
            w.setText(
                f"<div style='font-weight:700;font-size:16px'>{value}</div>"
                f"<div style='color:#7a7c8c;font-size:11px'>{title}</div>"
            )
            return w

        self.stat_total = make_stat_widget("Total élèves")
        self.stat_presents = make_stat_widget("Présents")
        self.stat_retards = make_stat_widget("Retards")
        self.stat_taux = make_stat_widget("Taux")

        stats_row.addWidget(self.stat_total)
        stats_row.addWidget(self.stat_presents)
        stats_row.addWidget(self.stat_retards)
        stats_row.addWidget(self.stat_taux)
        presence_vbox.addLayout(stats_row)

        # Table for listing students (ID hidden / Nom / Numéro / Statut) — styled like examen table
        self.presence_table = QTableWidget(0, 4)
        self.presence_table.setHorizontalHeaderLabels(["ID", "Nom", "Numéro", "Statut"])
        configure_table(self.presence_table)
        self.presence_table.setColumnHidden(0, True)
        presence_vbox.addWidget(self.presence_table)

        # (No export button as requested)
        
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

            # Update styled stat widgets
            self.stat_total.setText(f"<div style='font-weight:700;font-size:16px'>{total}</div><div style='color:#7a7c8c;font-size:11px'>Total élèves</div>")
            self.stat_presents.setText(f"<div style='font-weight:700;font-size:16px'>{presents}</div><div style='color:#7a7c8c;font-size:11px'>Présents</div>")
            self.stat_retards.setText(f"<div style='font-weight:700;font-size:16px'>{retards}</div><div style='color:#7a7c8c;font-size:11px'>Retards</div>")
            self.stat_taux.setText(f"<div style='font-weight:700;font-size:16px'>{taux}%</div><div style='color:#7a7c8c;font-size:11px'>Taux</div>")

            # Fetch retards list
            try:
                resp4 = requests.get(f"{API_BASE_URL}/stats/presence/retards", timeout=API_TIMEOUT)
                resp4.raise_for_status()
                retards_list = resp4.json()
            except requests.RequestException:
                retards_list = []

            # Build a combined students dict keyed by Id_eleve or Numero; fallback to index
            students = {}
            def student_key(s, idx):
                return s.get('Id_eleve') or s.get('Numero_eleve') or f"idx_{idx}"

            for idx, s in enumerate(present_list):
                key = student_key(s, idx)
                students[key] = {
                    'id': s.get('Id_eleve') or s.get('Numero_eleve') or '',
                    'nom': f"{s.get('Prenom_eleve','')} {s.get('Nom_eleve','')}",
                    'numero': s.get('Numero_eleve') or '',
                    'status': 'Présent'
                }

            for idx, s in enumerate(retards_list):
                key = student_key(s, idx)
                # If already present as Présent, prefer Retard (overwrite), otherwise add
                students[key] = {
                    'id': s.get('Id_eleve') or s.get('Numero_eleve') or '',
                    'nom': f"{s.get('Prenom_eleve','')} {s.get('Nom_eleve','')}",
                    'numero': s.get('Numero_eleve') or '',
                    'status': 'Retard'
                }

            # Populate table
            self.presence_table.setRowCount(0)
            for row_idx, info in enumerate(students.values()):
                self.presence_table.insertRow(row_idx)
                # ID (may be empty)
                self.presence_table.setItem(row_idx, 0, QTableWidgetItem(str(info.get('id') or '')))
                self.presence_table.setItem(row_idx, 1, QTableWidgetItem(info['nom']))
                self.presence_table.setItem(row_idx, 2, QTableWidgetItem(str(info['numero'])))
                self.presence_table.setItem(row_idx, 3, QTableWidgetItem(info['status']))
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
        

        layout.addStretch()

    # CSV export removed per request
