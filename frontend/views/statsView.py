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

        chart_label = QLabel()
        chart_label.setFixedHeight(220)
        chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        presence_vbox.addWidget(chart_label)

        # Fetch timeseries and render chart
        try:
            resp = requests.get(f"{API_BASE_URL}/stats/presence/timeseries?days=14", timeout=API_TIMEOUT)
            resp.raise_for_status()
            timeseries = resp.json()
        except requests.RequestException:
            timeseries = []

        if timeseries:
            # Extract series
            dates = [t.get('date') for t in timeseries]
            presents = np.array([int(t.get('presents', 0)) for t in timeseries], dtype=float)
            retards = np.array([int(t.get('retards', 0)) for t in timeseries], dtype=float)
            taux = None
            if all('taux_presence' in t for t in timeseries):
                taux = np.array([float(t.get('taux_presence', 0.0)) for t in timeseries], dtype=float)

            # Light smoothing (moving average)
            def smooth(a, w=3):
                if a.size < 3:
                    return a
                kernel = np.ones(w) / w
                return np.convolve(a, kernel, mode='same')

            presents_s = smooth(presents, w=3)
            retards_s = smooth(retards, w=3)

            plt.style.use('seaborn-v0_8')
            fig = plt.figure(figsize=(8, 2.4), dpi=100)
            ax = fig.add_subplot(111)
            color_p = '#27ae60'
            color_r = '#e67e22'
            color_t = '#2980b9'

            ax.plot(dates, presents_s, color=color_p, linewidth=2.6, marker='o', label='Présents')
            ax.fill_between(dates, presents_s, color=color_p, alpha=0.12)
            ax.plot(dates, retards_s, color=color_r, linewidth=2.2, marker='o', label='Retards')

            if taux is not None:
                taux_s = smooth(taux, w=3)
                ax2 = ax.twinx()
                ax2.plot(dates, taux_s, color=color_t, linewidth=2, linestyle='--', marker='s', label='Taux (%)')
                ax2.set_ylabel('Taux (%)', color=color_t)
                ax2.tick_params(axis='y', colors=color_t)

            ax.set_ylim(bottom=0)
            ax.set_xlabel('Date')
            ax.set_ylabel('Nombre')
            ax.grid(axis='y', alpha=0.25)
            ax.tick_params(axis='x', rotation=40)
            ax.legend(loc='upper left')
            plt.tight_layout()

            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            plt.close(fig)
            buf.seek(0)
            pix = QPixmap()
            pix.loadFromData(buf.getvalue(), 'PNG')
            w = chart_label.width() or 800
            h = chart_label.height() or 220
            chart_label.setPixmap(pix.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            no_data = QLabel("Aucune donnée disponible")
            no_data.setStyleSheet("color:#7a7c8c;font-size:12px;")
            presence_vbox.addWidget(no_data)

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
