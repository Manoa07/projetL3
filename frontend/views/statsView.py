from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar,
    QGridLayout, QTableWidget, QTableWidgetItem, QGraphicsDropShadowEffect,
    QSizePolicy, QScrollArea, QPushButton, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, QRectF, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor, QFont
from components.icon_loader import load_icon
from components.statCard import StatCard
import requests
from config import API_BASE_URL, API_TIMEOUT
from components.theme import configure_table


class CircularProgress(QWidget):
    """
    Jauge circulaire ("donut") dessinée directement en QPainter.
    Rendu vectoriel : net à toute taille/DPI, sans les artefacts de
    rasterisation qu'on avait avec les Wedge matplotlib (bords facettés,
    coupe nette en haut du cercle sur les captures haute densité).
    """

    def __init__(self, value=0.0, maximum=100.0, color="#2980b9",
                 bg_color="#e9eef3", center_text=None, thickness=10,
                 diameter=120, parent=None):
        super().__init__(parent)
        self._value = float(value)
        self._maximum = float(maximum) if maximum else 1.0
        self._color = QColor(color)
        self._bg_color = QColor(bg_color)
        self._center_text = center_text if center_text is not None else str(int(value))
        self._thickness = thickness
        self.setFixedSize(diameter, diameter)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def set_value(self, value, maximum=None, center_text=None):
        self._value = float(value)
        if maximum is not None:
            self._maximum = float(maximum) if maximum else 1.0
        if center_text is not None:
            self._center_text = center_text
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(
            self._thickness / 2, self._thickness / 2,
            self.width() - self._thickness, self.height() - self._thickness
        )

        frac = 0.0
        if self._maximum:
            frac = max(0.0, min(self._value / self._maximum, 1.0))

        # Anneau de fond
        pen_bg = QPen(self._bg_color)
        pen_bg.setWidth(self._thickness)
        pen_bg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 0, 360 * 16)

        # Arc de progression (démarre à midi, sens horaire)
        if frac > 0:
            pen_fg = QPen(self._color)
            pen_fg.setWidth(self._thickness)
            pen_fg.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen_fg)
            start_angle = 90 * 16
            span_angle = -int(360 * frac * 16)
            painter.drawArc(rect, start_angle, span_angle)

        # Texte central
        painter.setPen(QColor("#17212b"))
        font = QFont()
        font.setBold(True)
        font.setPointSize(max(9, int(self.width() / 10)))
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._center_text)

        painter.end()


def apply_shadow(widget, blur=24, y_offset=6, alpha=35):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, y_offset)
    shadow.setColor(QColor(23, 33, 43, alpha))
    widget.setGraphicsEffect(shadow)


def fit_table_to_content(table, min_height=90, max_height=None):
    """
    Ajuste la hauteur du QTableWidget à son contenu réel (en-tête + lignes),
    au lieu d'une hauteur fixe. Désactive la scrollbar verticale interne
    puisque la table grandit désormais avec ses données ; le débordement
    éventuel est géré par le scroll global de la page.
    """
    table.resizeRowsToContents()
    header_h = table.horizontalHeader().height()
    rows_h = sum(table.rowHeight(r) for r in range(table.rowCount()))
    frame_h = 2 * table.frameWidth()
    total = header_h + rows_h + frame_h + 4  # petite marge de sécurité

    if max_height is not None:
        total = min(total, max_height)
    total = max(total, min_height)

    table.setFixedHeight(total)
    table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


class StatsView(QWidget):
    def __init__(self):
        super().__init__()

        # Widget racine : un QScrollArea pour ne jamais tronquer le contenu
        # quand la fenêtre/l'onglet hôte est plus petit que ce qu'il y a à afficher.
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea { background-color: transparent; border: none; }
            QScrollArea > QWidget > QWidget { background-color: transparent; }
        """)

        content = QWidget()
        content.setStyleSheet("background-color: #f4f6f9;")

        # Mise en page principale de la vue Statistiques
        layout = QVBoxLayout(content)
        layout.setContentsMargins(4, 24, 24, 24)
        layout.setSpacing(20)

        # Titre de la section
        title = QLabel("SUIVI DES PRÉSENCES")
        title.setStyleSheet("""
            border: none;
            color: #17212b;
            font-size: 20px;
            font-weight: 800;
            letter-spacing: 1px;
        """)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.refresh_button = QPushButton("Rafraîchir")
        self.refresh_button.setIcon(load_icon("refresh"))
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #e8f0ff;
                color: #2459bd;
                border: 1px solid #bdd0f7;
                padding: 8px 14px;
                border-radius: 10px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #dbe7ff;
            }
            QPushButton:disabled {
                background-color: #edf2ff;
                color: #7a8fb8;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_button)
        layout.addLayout(header_layout)

        selector_row = QHBoxLayout()
        selector_row.setSpacing(12)
        selector_label = QLabel("Cours :")
        selector_label.setStyleSheet("border: none; font-weight:700; color:#17212b;")
        selector_row.addWidget(selector_label)

        self.course_selector = QComboBox()
        self.course_selector.setMinimumWidth(320)
        self.course_selector.setStyleSheet("""
            QComboBox {
                background: #edf4ff;
                border: 2px solid #3b6ee8;
                border-radius: 10px;
                padding: 10px 36px 10px 12px;
                color: #102a43;
                font-weight: 600;
            }
            QComboBox::drop-down {
                border: none;
                background: transparent;
                width: 28px;
            }
            QComboBox::down-arrow {
                width: 0px;
                height: 0px;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid #1f4fc9;
                margin-right: 10px;
            }
        """)
        self.course_selector.currentIndexChanged.connect(self.on_course_changed)
        selector_row.addWidget(self.course_selector)
        selector_row.addStretch()
        layout.addLayout(selector_row)

        self.course_selector.addItem("Choisir un cours", None)
        try:
            resp_courses = requests.get(f"{API_BASE_URL}/cours/all", timeout=API_TIMEOUT)
            resp_courses.raise_for_status()
            for cours in resp_courses.json() or []:
                name = cours.get("nom_cours") or cours.get("Nom_cours") or "Cours"
                course_id = cours.get("Id_cours", cours.get("id_cours"))
                self.course_selector.addItem(f"{name} — {cours.get('date_cours', '')}", course_id)
        except requests.RequestException:
            pass

        # 1. Cartes de statistiques (KPI)
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(16)
        self.card_taux = StatCard("Taux", "--%", "#243447")
        self.card_absents = StatCard("Absents", "-- / --", "#e74c3c")
        self.card_retards = StatCard("Retards", "--", "#f39c12")
        for card in (self.card_taux, self.card_absents, self.card_retards):
            apply_shadow(card, blur=20, y_offset=4, alpha=25)
            kpi_layout.addWidget(card)
        layout.addLayout(kpi_layout)

        stats = {}
        try:
            course_id = self.course_selector.currentData()
            params = {}
            if course_id is not None:
                params['course_id'] = course_id
            resp_stats = requests.get(f"{API_BASE_URL}/stats/presence", timeout=API_TIMEOUT, params=params)
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
            pass

        # 2. Jauges circulaires (Présents / Retards / Taux)
        presence_frame = QFrame()
        presence_frame.setStyleSheet("""
            QFrame { background-color: #ffffff; border: 1px solid #eef1f5; border-radius: 16px; }
            QLabel { color: #1a2832; }
        """)
        apply_shadow(presence_frame, blur=28, y_offset=8, alpha=18)
        presence_vbox = QVBoxLayout(presence_frame)
        presence_vbox.setContentsMargins(20, 18, 20, 22)
        presence_vbox.setSpacing(16)

        chart_title = QLabel("Évolution des présences")
        chart_title.setStyleSheet("border: none; font-weight:700; font-size:14px; color:#17212b;")
        presence_vbox.addWidget(chart_title)

        total = stats.get('total_eleves', 0)
        presents_val = stats.get('presents', 0)
        retards_val = stats.get('retards', 0)
        taux_val = stats.get('taux_presence', 0.0)

        donut_layout = QHBoxLayout()
        donut_layout.setSpacing(24)
        self.donut_widgets = {}

        for title_text, value, denom, color, center in [
            ("Présents", presents_val, total, '#27ae60', f"{presents_val}"),
            ("Retards", retards_val, total, '#e67e22', f"{retards_val}"),
            ("Taux (%)", taux_val, 100.0, '#2980b9', f"{taux_val}%"),
        ]:
            block_frame = QFrame()
            block_frame.setStyleSheet("""
                QFrame { background-color: #fbfcfe; border: 1px solid #eef1f5; border-radius: 14px; }
            """)
            block = QVBoxLayout(block_frame)
            block.setContentsMargins(14, 16, 14, 16)
            block.setSpacing(10)
            block.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            t = QLabel(title_text)
            t.setStyleSheet('border: none; font-weight:700; font-size:12px; color:#5b6774; letter-spacing: 0.5px;')
            t.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            donut = CircularProgress(
                value=value, maximum=denom if denom else 1.0,
                color=color, center_text=center, thickness=12, diameter=130
            )
            self.donut_widgets[title_text] = donut

            block.addWidget(t)
            block.addWidget(donut, alignment=Qt.AlignmentFlag.AlignHCenter)
            donut_layout.addWidget(block_frame)

        presence_vbox.addLayout(donut_layout)

        layout.addWidget(presence_frame)

        # 3. Information sur le prochain contrôle
        info_row = QHBoxLayout()
        info_row.setSpacing(8)
        info_icon = QLabel()
        info_icon.setPixmap(load_icon("info").pixmap(16, 16))
        info_row.addWidget(info_icon)

        # info_label = QLabel("Prochain contrôle : dans 20 minutes")
        # info_label.setStyleSheet("border: none; color: #7a7c8c; font-style: italic; font-size: 13px;")
        # info_row.addWidget(info_label)
        # info_row.addStretch()
        # layout.addLayout(info_row)

        # 4. Liste des élèves présents (Nom / Numero / Status)
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame { background-color: #ffffff; border: none; border-radius: 14px; }
        """)
        apply_shadow(table_frame, blur=20, y_offset=4, alpha=15)
        table_vbox = QVBoxLayout(table_frame)
        table_vbox.setContentsMargins(16, 14, 16, 16)
        table_vbox.setSpacing(10)

        list_title = QLabel("Élèves présents")
        list_title.setStyleSheet("border: none; font-weight:700; font-size:14px; color:#17212b;")
        table_vbox.addWidget(list_title)

        present_table = QTableWidget(0, 3)
        present_table.setHorizontalHeaderLabels(["Nom", "Numero", "Status"])
        configure_table(present_table, height=260)  # hauteur écrasée plus bas via fit_table_to_content

        # Retire le quadrillage et les bordures internes/externes de la table
        present_table.setShowGrid(False)
        present_table.setFrameShape(QFrame.Shape.NoFrame)
        present_table.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: transparent;
                background-color: #ffffff;
            }
            QHeaderView::section {
                border: none;
                border-bottom: 1px solid #eef1f5;
                background-color: #eef1f5;
                padding: 6px;
            }
            QTableWidget::item {
                border: none;
            }
        """)

        self.present_table = present_table
        fit_table_to_content(self.present_table)

        table_vbox.addWidget(self.present_table)
        layout.addWidget(table_frame)

        layout.addStretch()

        scroll_area.setWidget(content)
        outer_layout.addWidget(scroll_area)

        QTimer.singleShot(0, self.refresh_data)

    def on_course_changed(self):
        if hasattr(self, 'course_selector'):
            self.refresh_data()

    def refresh_data(self):
        if not hasattr(self, 'refresh_button'):
            return
        self.refresh_button.setEnabled(False)
        try:
            self.load_stats_data()
        except Exception as exc:
            print(f"Erreur lors du rafraîchissement des statistiques : {exc}")
            QMessageBox.critical(self, "Erreur", "Impossible de rafraîchir les statistiques.")
        finally:
            if hasattr(self, 'refresh_button'):
                self.refresh_button.setEnabled(True)

    def load_stats_data(self):
        if not hasattr(self, 'course_selector'):
            return
        stats = {}
        try:
            params = {}
            course_id = self.course_selector.currentData()
            if course_id is not None:
                params['course_id'] = course_id
            resp_stats = requests.get(f"{API_BASE_URL}/stats/presence", timeout=API_TIMEOUT, params=params)
            resp_stats.raise_for_status()
            stats = resp_stats.json()
        except requests.RequestException:
            stats = {}

        total = stats.get('total_eleves', 0)
        presents = stats.get('presents', 0)
        absents = stats.get('absents', max(total - presents, 0))
        retards = stats.get('retards', 0)
        taux = stats.get('taux_presence', 0.0)

        if hasattr(self, 'card_taux'):
            self.card_taux.set_value(f"{taux}%")
            self.card_absents.set_value(f"{absents} / {total}")
            self.card_retards.set_value(str(retards))

        if hasattr(self, 'donut_widgets'):
            self.donut_widgets.get("Présents", None).set_value(presents, total if total else 1, f"{presents}")
            self.donut_widgets.get("Retards", None).set_value(retards, total if total else 1, f"{retards}")
            self.donut_widgets.get("Taux (%)", None).set_value(taux, 100.0, f"{taux}%")

        students_map = {}
        try:
            params = {}
            course_id = self.course_selector.currentData()
            if course_id is not None:
                params['course_id'] = course_id
            resp_p = requests.get(f"{API_BASE_URL}/stats/presence/presents", timeout=API_TIMEOUT, params=params)
            resp_r = requests.get(f"{API_BASE_URL}/stats/presence/retards", timeout=API_TIMEOUT, params=params)
            resp_p.raise_for_status(); resp_r.raise_for_status()
            presents_rows = resp_p.json() or []
            retards_rows = resp_r.json() or []
            for s in presents_rows:
                key = s.get('Id_eleve') or s.get('Numero_eleve') or f"{s.get('Nom_eleve','')}_{s.get('Prenom_eleve','')}"
                students_map[key] = {
                    'nom': f"{s.get('Nom_eleve','')} {s.get('Prenom_eleve','')}",
                    'numero': s.get('Numero_eleve',''),
                    'status': 'Présent'
                }
            for s in retards_rows:
                key = s.get('Id_eleve') or s.get('Numero_eleve') or f"{s.get('Nom_eleve','')}_{s.get('Nom_eleve','')}"
                if key in students_map:
                    continue
                students_map[key] = {
                    'nom': f"{s.get('Nom_eleve','')} {s.get('Prenom_eleve','')}",
                    'numero': s.get('Numero_eleve',''),
                    'status': 'Retardataire'
                }
        except requests.RequestException:
            students_map = {}

        if not hasattr(self, 'present_table'):
            return

        self.present_table.setRowCount(0)
        for row, (_, s) in enumerate(students_map.items()):
            self.present_table.insertRow(row)
            self.present_table.setItem(row, 0, QTableWidgetItem(str(s['nom'])))
            self.present_table.setItem(row, 1, QTableWidgetItem(str(s['numero'])))
            status_item = QTableWidgetItem(str(s['status']))
            if s['status'] == 'Retardataire':
                status_item.setForeground(QColor('#e67e22'))
            else:
                status_item.setForeground(QColor('#27ae60'))
            self.present_table.setItem(row, 2, status_item)

        fit_table_to_content(self.present_table)