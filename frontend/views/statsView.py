from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar, QGridLayout, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from components.icon_loader import load_icon
from components.statCard import StatCard
import requests
import numpy as np
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

        # Titre de la section
        title = QLabel("<b style='color:#17212b; font-size:18px; letter-spacing: 1px;'>SUIVI DES PRÉSENCES</b>")
        layout.addWidget(title)

        # 1. Cartes de statistiques (KPI)
        kpi_layout = QHBoxLayout()
        self.card_taux = StatCard("Taux", "--%", "#243447")
        self.card_absents = StatCard("Absents", "-- / --", "#e74c3c")
        self.card_retards = StatCard("Retards", "--", "#f39c12")
        kpi_layout.addWidget(self.card_taux)
        kpi_layout.addWidget(self.card_absents)
        kpi_layout.addWidget(self.card_retards)
        layout.addLayout(kpi_layout)

        # Fetch global stats to populate KPI cards
        try:
            resp_stats = requests.get(f"{API_BASE_URL}/stats/presence", timeout=API_TIMEOUT)
            resp_stats.raise_for_status()
            stats = resp_stats.json()
            total = stats.get('total_eleves', 0)
            presents = stats.get('presents', 0)
            absents = stats.get('absents', max(total - presents, 0))
            retards = stats.get('retards', 0)
            taux = stats.get('taux_presence', 0.0)
            self.card_taux.set_value(f"{taux}%")
            self.card_absents.set_value(f"{absents} / {total}")
            self.card_retards.set_value(str(retards))
        except requests.RequestException:
            # leave defaults if API unavailable
            pass

        # 2. Courbe d'évolution (Présents / Retards / Taux)
        # Modern look: smoothing + seaborn colors + filled area for présents
        presence_frame = QFrame()
        presence_frame.setStyleSheet("""
            QFrame { background-color: #ffffff; border: 1px solid #e9eef3; border-radius: 12px; padding: 14px; }
            QLabel { color: #1a2832; }
        """)
        presence_vbox = QVBoxLayout(presence_frame)
        presence_vbox.setContentsMargins(6, 6, 6, 6)
        presence_vbox.setSpacing(8)
        chart_title = QLabel("Évolution des présences")
        chart_title.setStyleSheet("font-weight:700; font-size:13px;")
        presence_vbox.addWidget(chart_title)

        # --- Small circular (donut) charts for Présents / Retards / Taux ---
        try:
            stats  # check existence
        except NameError:
            stats = {}

        total = stats.get('total_eleves', 0)
        presents_val = stats.get('presents', 0)
        retards_val = stats.get('retards', 0)
        taux_val = stats.get('taux_presence', 0.0)

        def make_donut(value, total_for_pct, color, center_text=None, size=(140, 140)):
            fig, ax = plt.subplots(figsize=(size[0]/100, size[1]/100), dpi=100)
            frac = float(value) / float(total_for_pct) if total_for_pct else 0.0
            frac = max(0.0, min(frac, 1.0))
            sizes = [frac, 1 - frac]
            colors = [color, '#e9eef3']
            wedges, _ = ax.pie(sizes, colors=colors, startangle=90, wedgeprops=dict(width=0.32, edgecolor='white'))
            ax.set(aspect="equal")
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
            # center text
            if center_text is None:
                center_text = f"{int(value)}"
            ax.text(0, 0, center_text, ha='center', va='center', fontsize=10, color='#17212b', weight='700')
            buf = io.BytesIO()
            fig.savefig(buf, format='png', transparent=True)
            plt.close(fig)
            buf.seek(0)
            pix = QPixmap()
            pix.loadFromData(buf.getvalue(), 'PNG')
            return pix

        donut_layout = QHBoxLayout()
        donut_layout.setSpacing(18)
        # create vertical blocks (title + donut)
        for title_text, value, denom, color, center in [
            ("Présents", presents_val, total, '#27ae60', f"{presents_val}"),
            ("Retards", retards_val, total, '#e67e22', f"{retards_val}"),
            ("Taux (%)", taux_val, 100.0, '#2980b9', f"{taux_val}%"),
        ]:
            block = QVBoxLayout()
            t = QLabel(title_text)
            t.setStyleSheet('font-weight:700; font-size:12px; color:#17212b;')
            t.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            img = QLabel()
            img.setPixmap(make_donut(value, denom, color, center_text=center))
            img.setAlignment(Qt.AlignmentFlag.AlignCenter)
            block.addWidget(t)
            block.addWidget(img)
            donut_layout.addLayout(block)
        presence_vbox.addLayout(donut_layout)

        layout.addWidget(presence_frame)

        # 3. Information sur le prochain contrôle
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
